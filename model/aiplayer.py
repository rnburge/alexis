import queue
import threading
import time
from copy import deepcopy
from threading import Thread

import numpy as np

from model.move import Move
from model.rack import Rack
from util.bit_twiddling import read_bit

from controller.game import GameController
from model.config import Direction, BOARD_SIZE, LETTER_VALUES
from model.player import Player
from model.row import Row
from view.view import View
from model.movevalidator import MoveValidationError
import itertools


class AiPlayer(Player):
    """ represents a AI-controlled player """

    def __init__(self, game: GameController, gui: View, name: str):
        """ Create a new game move """
        self.game = game
        self.board = game.board
        super().__init__(game.bag, gui, name)

    def get_starting_move(self):
        # return self.get_move()
        # only need to consider one starting row (column would just be a transpose):
        row = deepcopy(self.board.get_row(8, Direction.HORIZONTAL))
        
        possible_moves = self.play_on_square(row, 8, [None] * 16, self.rack)

        if '@' in self.rack:
            self.check_blank_permutations()

        move = self.best_move(possible_moves)

        # reset row so it's a reference to the actual board:
        if move.row:
            move.row = self.board.get_row(move.row.rank, move.row.direction)

        return move

        # reset row so it doesn't already contain played tiles:
        #if move.row:
        # #   move.row = self.board.get_row(move.row.rank, move.row.direction)

        #return move

    def get_move(self):
        possible_moves = self.generate_all_moves()
        move = self.best_move(possible_moves)

        # reset row so it's a reference to the actual board:
        if move.row:
            move.row = self.board.get_row(move.row.rank, move.row.direction)
        return move

    def generate_all_moves(self):
        """ returns a list of all possible moves """
        valid_moves = []
        #row_queue = queue.Queue()

        # grab a list of all the rows which have start squares/hooks in them:
        rows_to_consider = \
            [self.board.get_row(i, Direction.HORIZONTAL)
             for i in range(1, BOARD_SIZE)
             if self.board.hook_squares[i, :].any()]

        # do the same for columns:
        rows_to_consider.extend(
            [self.board.get_row(i, Direction.VERTICAL)
             for i in range(1, BOARD_SIZE)
             if self.board.hook_squares[:, i].any()])

        #for row in rows_to_consider:
        #    row_queue.put(row)

        # make list of lists of possible moves, each index will be list from a different thread
        moves = np.full(len(rows_to_consider), None)
        # to keep track of thread references:
        row_threads = []
        # consider each row in separate thread:
        for i in range(len(rows_to_consider)):
            row = rows_to_consider[i]
            thread = Thread(target=self.get_moves, args=(moves, i, row))
            row_threads.append(thread)
            thread.start()
        # wait for all threads to finish:
        [t.join() for t in row_threads]
        #    concatenate all move lists from all threads
        valid_moves.extend(itertools.chain.from_iterable(moves))

        # DEBUG:
        print(str(valid_moves))

        # DEBUG
        print("*** moving on ***")
        print(threading.get_ident())

        if '@' in self.rack:
            self.check_blank_permutations()

        return valid_moves

    def get_moves(self, moves, i, row):
        moves[i] = self.moves_for_row(deepcopy(row), deepcopy(self.rack))
        # **DEBUG** :
        # print("added move "+str(i))

    def best_move(self, potential_moves):
        """ This returns whatever the AI considers the best move to be out of all the moves in the argument list """

        potential_moves.sort(key=lambda x: x.score, reverse=True)
        best_move = potential_moves[0] if potential_moves else Move(None, None, None)
        # now we've decided on a move, remove those tiles from the rack:
        if best_move.tiles:
            self.rack.get_tiles(''.join([str(t) for t in best_move.tiles]))

        # DEBUG:
        print(self.name+": Best move is: "+str(best_move))  # DEBUG

        return best_move

    def moves_for_row(self, row: Row, rack: Rack):
        """ returns all valid moves playable in the argument row """

        hooks = np.nonzero(row.hook_squares)[0]
        valid_moves = []

        for hook in hooks:
            valid_moves.extend(self.play_on_square(row, hook, [None] * 16, rack))

        return valid_moves

    def play_on_square(self, row, index, played_tiles, rack: Rack):

        valid_moves = []

        # get all the letters we could play on this square without making nonsense in the corresponding column:
        valid_cross_plays = [chr(64 + x) for x in range(1, 27) if read_bit(row.this_row_crosschecks[index], x)]

        # filter that to ones we can actually use with tiles from our rack (all of them if we have a blank!)
        valid_tiles = valid_cross_plays if '@' in rack else [x for x in valid_cross_plays if x in rack]

        try:
            # for each of the playable tiles, stick it in the square
            for tile_letter in valid_tiles:
                tile = rack.get_tile(tile_letter)
                played_tiles[index] = tile
                row.existing_letters[index] = ord(tile)-64

                if row.word_at(index) in self.game.lexicon:
                    new_move = Move(row, np.where(played_tiles)[0][0], [tile for tile in played_tiles if tile])
                    new_move.played_squares = np.where(played_tiles)[0]
                    new_move.calculate_score()
                    #DEBUG:
                    #print(self.name+": Considering move: "+str(new_move)+" move.direction="+str(new_move.direction))
                    valid_moves.append(new_move)

                if len(rack) > 0:
                    valid_moves.extend(self.extend_right(index, played_tiles, row, rack))
                    valid_moves.extend(self.extend_left(index, played_tiles, row, rack))

                # return the tile:

                # set any blank back to blank
                if ord(tile) > ord('Z'):
                    tile = '@'
                # put tile back in rack
                rack.add_tile(tile)
                # set board square back to no letter
                row.existing_letters[index] = 0
                # remove tile from list of played tiles:
                played_tiles[index] = None
        except MoveValidationError as err:
            pass
        return valid_moves

    def extend_right(self, index, played_tiles, row, rack: Rack):
        valid_moves = []
        if self.game.lexicon.contains_prefix(row.word_at(index)):
            if row.empty_squares(index + 1).any():
                next_empty_square = row.empty_squares(index + 1)[0]
                valid_moves.extend(self.play_on_square(row, next_empty_square, played_tiles, rack))
        return valid_moves

    def extend_left(self, index, played_tiles, row, rack: Rack):
        valid_moves = []
        if self.game.lexicon.contains_suffix(row.word_at(index)):
            # if there's still a blank left in this row somewhere to the left:
            if [square for square in row.empty_squares() if square < index]:
                # then mark that next empty square as the one to play a tile in next:
                next_empty_square = [square for square in row.empty_squares() if square < index][-1]
                # if that square happens to be a hook, we'll have already formed all the words extending from it:
                if not row.hook_squares[next_empty_square]:
                    valid_moves.extend(self.play_on_square(row, next_empty_square, played_tiles, rack))
        return valid_moves

    @staticmethod
    def permute_blanks(move):
        """ takes the argument move containing a blank, and returns a list of moves containing
        all permutations of this move with the blank in different positions
        (this will only result in additional moves if the word contains another tile with the
        same letter as has been assigned to the blank)"""

        moves = [move]

        for i in range(0, len(move.tiles)):
            if move.tiles[i].islower():
                for j in range(0, len(move.tiles)):
                    if j != i and move.tiles[i].upper() == move.tiles[j]:
                        reordered_tiles = list(move.tiles)
                        reordered_tiles[i],reordered_tiles[j] = reordered_tiles[j], reordered_tiles[i]
                        moves.append(Move(move.row, move.is_valid, reordered_tiles))
        return moves

    def check_blank_permutations(self):
        """ this needs to see if any moves use the same letter on a blank as an existing
        character, and if so generate extra moves by swapping them """
        pass
        # if any(type(tile) is BlankTile for tile in played_tiles):
        #    # check for playing the blank in different spaces:
        #    valid_moves.extend(self.permute_blanks(new_move))
        #else:
        #pass

