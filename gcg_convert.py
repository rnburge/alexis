from controller.game import GameController
from view.consolegui import ConsoleGui
from model.aiplayer import AiPlayer
from model.bag import Bag
from model.config import Direction
from model.move import Move
from model.row import Row
import numpy as np
import os
import copy
from model.config import LETTER_VALUES, NO_CROSS_WORD, RACK_SIZE, BONUS
from random import choices
from PIL import Image
from IPython.display import display
from threading import Thread

gcg_path = './gcg/'
img_path = './images/'


def process_game(lines, k):
    players = [None, None]
    game = GameController(players, Bag())
    gui = ConsoleGui(game)
    movelist = [line.split() for line in lines]
    player1 = AiPlayer(game, gui, movelist.pop(0)[1])
    player2 = AiPlayer(game, gui, movelist.pop(0)[1])
    game.players = [player1, player2]
    game.active_player = player1 if player1.name == movelist[0][0][1:-1] else player2

    j = 0  # current move
    while movelist:
        j += 1
        current_move_info = movelist.pop(0)

        # if there are things in brackets, they are score adjustments so we've
        # finished all the moves:
        if '(' in current_move_info[1]:
            return

        # we use '@' for blank for pragmatic reasons (it's the ASCII character before 'A')
        # GCG uses '?', so let's fix that:
        game.active_player.rack.rack_tiles = list(current_move_info[1].replace('?', '@'))

        # Now we have the correct tiles in the rack and the board is advanced to the correct position,
        # let's get a list of all the moves ALexIS can come up with:
        alexis_moves = game.active_player.generate_all_moves()
        alexis_moves.sort(key=lambda x: x.score, reverse=True)  # Sort if with highest scores first

        # put any blanks back to having letter un-assigned, ready for parsing Quackle move
        game.active_player.rack.reset_blanks()

        # Now let's move onto getting our 'good' move from the GCG file:

        # GCG has digit(s) followed by letter for horizontal move, or vice versa for vertical,
        # wheras we are expecting digit, then letter, then 'H' or 'V', so let's fix that:

        start_square = current_move_info[2]

        if start_square.startswith('-'):
            tiles = ''
            if len(start_square)>1:
                tiles = start_square[1]
            start_square = ''
        else:
            if start_square[0].isdigit():
                start_square = start_square[-1] + start_square[:-1] + 'H'
            else:
                start_square += 'V'
            # lowercase letters in the GCG represent blanks. We're expecting a question mark for a blank,
            # followed by the desired letter, so replace 'a' with '?A', etc:
            tiles = ''.join(['?' + letter.upper() if letter.islower() else letter for letter in current_move_info[3]])

        # GCG gives the start square as the first letter in the word,
        # and uses '.' as a placeholder for any tile already on the board,
        # whereas we list the first square we're actually playing on, and
        # just the tiles actually played, so let's strip out '.' and adjust the
        # starting square if necessary:

        if '.' in tiles:
            start_square = list(start_square)  # treat string as char list
            x = 0
            while tiles[x] == '.':  # whilst there's a dot at the start
                if start_square[-1] == 'V':
                    start_square[-2] = str(int(start_square[-2]) + 1)  # increase the row if playing vertical
                else:
                    start_square[0] = chr(ord(start_square[0]) + 1)  # or the column if horizontal
                x += 1
            start_square = ''.join(start_square)  # make a string again
            tiles = tiles.replace('.', '')  # strip out any dot in the middle of the word

        # save the rack for later:
        cached_rack = copy.deepcopy(game.active_player.rack)

        # This will get a move and remove tiles from rack:
        quackle_move = gui.parse_move_string(start_square + tiles)

        if quackle_move.direction is not Direction.NOT_APPLICABLE:
            # validator will place tiles onto row in course of validation,
            # so first we'll copy the row so as not to mess up the board:
            quackle_move.row = copy.deepcopy(quackle_move.row)
            game.validator.is_valid(quackle_move)

            # this will calculate score (but only if tiles are already played on row):
            quackle_move.calculate_score()

        # now choose some moves. If we do data augmentation by transposing the 'correct' Quackle-derived moves,
        # we'll have 2 correct moves, so picking six of these would give us multiples of 8 moves.
        # Picking the top couple and randomly picking the rest would analyse a couple of 'good' moves
        # but still allow a little exploration (c.f. Q learning)

        if quackle_move in alexis_moves:
            alexis_moves.remove(quackle_move)  # don't process the quackle move as one of the wrong ones

        # just in case it's the end game:
        while len(alexis_moves) < 6:
            # add a pass:
            alexis_moves.append(Move(None, None, None))

        wrong_moves = []
        wrong_moves.append(alexis_moves.pop(0))
        wrong_moves.append(alexis_moves.pop(0))

        # add 4 randomly chosen moves:
        wrong_moves.extend(choices(alexis_moves, k=4))

        for k in range(len(wrong_moves)):
            base_layer = copy.deepcopy(game.board.existing_letters[:-1, :-1])  # slice off last sentinel
            # set first sentinel squares to zero instead of sentinel value:
            base_layer[0, :] = 0
            base_layer[:, 0] = 0

            move_layer = np.zeros([16, 16], dtype='int')
            # put rack tiles we're playing from in first row:
            move_layer[0][0:len(cached_rack)] = [ord(t) - 64 for t in cached_rack.rack_tiles]

            # set first sentinel squares to zero instead of sentinel value:
            word_mult = np.where(game.board.word_multipliers > 1, game.board.word_multipliers * 8, 0)
            letter_mult = np.where(game.board.letter_multipliers > 1, game.board.letter_multipliers * 2, 0)
            score_layer = np.where(game.board.existing_letter_scores > 0, game.board.existing_letter_scores * 2,
                                   word_mult + letter_mult)
            score_layer = score_layer[:-1, :-1]  # slice off last sentinel
            # set first sentinel squares to zero instead of sentinel value:
            score_layer[0, :] = 0
            score_layer[:, 0] = 0

            move = wrong_moves[k]
            move_tiles = move.tiles if move.tiles else []

            if move.direction == Direction.NOT_APPLICABLE:  # pass or exchange
                # put rack tiles we're exchanging in first row:
                if move.tiles: # unless it's a pass with no tiles
                    move_layer[0][0:len(move_tiles)] = [ord(t) - 64 for t in move.tiles]

            else:  # regular move
                row = move_layer[move.row.rank, :] if move.direction == Direction.HORIZONTAL else move_layer[:,
                                                                                                  move.row.rank]
                # put rack tiles we're playing on board:
                row[move.played_squares] = [ord(t) - 64 for t in move.tiles]
                # change score of square containing blank to zero:
                score_layer = np.where(move_layer <= 26, score_layer, 0)
                # change blanks to normal letter ordinal (by subtracting 32)
                move_layer = np.where(move_layer <= 26, move_layer, move_layer - 32)

            # flatten arrays and convert int8 to int so values aren't clipped at 128:
            rgb = zip((base_layer.astype(int)).flatten() * 9, (score_layer.astype(int)).flatten() * 9,
                      (move_layer.astype(int)).flatten() * 9)
            # put in a list:
            rgb = [pixel for pixel in rgb]

            # convert to an image, and resize so things like
            # max pooling layers won't lose all the information in the image:
            img = Image.new('RGB', (16, 16))
            img.putdata(rgb)
            img = img.resize((256, 256), Image.NEAREST)

            # save the image
            img.save(img_path + 'alexis_game' + str(i).zfill(4)
                     + '_move' + str(j).zfill(2)
                     + '_option' + str(k + 1) + '.png')

            # add a little feedback to the console:
            print("i,j,k:" + str((i, j, k)))

        # now process the Quackle move:
        base_layer = copy.deepcopy(game.board.existing_letters[:-1, :-1])  # slice off last sentinel
        # set first sentinel squares to zero instead of sentinel value:
        base_layer[0, :] = 0
        base_layer[:, 0] = 0

        move_layer = np.zeros([16, 16], dtype='int')
        # put rack tiles we're playing from in first row:
        move_layer[0][0:len(cached_rack)] = [ord(t) - 64 for t in cached_rack.rack_tiles]

        # set first sentinel squares to zero instead of sentinel value:
        word_mult = np.where(game.board.word_multipliers > 1, game.board.word_multipliers * 8, 0)
        letter_mult = np.where(game.board.letter_multipliers > 1, game.board.letter_multipliers * 2, 0)
        score_layer = np.where(game.board.existing_letter_scores > 0, game.board.existing_letter_scores * 2,
                               word_mult + letter_mult)
        score_layer = score_layer[:-1, :-1]  # slice off last sentinel
        # set first sentinel squares to zero instead of sentinel value:
        score_layer[0, :] = 0
        score_layer[:, 0] = 0

        move = quackle_move
        move_tiles = move.tiles if move.tiles else []

        if move.direction == Direction.NOT_APPLICABLE:  # pass or exchange
            # put rack tiles we're exchanging in first row:
            if move_tiles:
                move_layer[0][0:len(move_tiles)] = [ord(t) - 64 for t in move.tiles]

        else:  # regular move
            row = move_layer[move.row.rank, :] if move.direction == Direction.HORIZONTAL else move_layer[:,
                                                                                              move.row.rank]
            # put rack tiles we're playing on board:
            row[move.played_squares] = [ord(t) - 64 for t in move.tiles]
            # change score of square containing blank to zero:
            score_layer = np.where(move_layer <= 26, score_layer, 0)
            # change blanks to normal letter ordinal (by subtracting 32)
            move_layer = np.where(move_layer <= 26, move_layer, move_layer - 32)

        # flatten arrays and convert int8 to int so values aren't clipped at 128:
        rgb = zip((base_layer.astype(int)).flatten() * 9, (score_layer.astype(int)).flatten() * 9,
                  (move_layer.astype(int)).flatten() * 9)
        # put in a list:
        rgb = [pixel for pixel in rgb]

        # convert to an image, and resize so things like
        # max pooling layers won't lose all the information in the image:
        img = Image.new('RGB', (16, 16))
        img.putdata(rgb)
        img = img.resize((256, 256), Image.NEAREST)

        # save the image
        img.save(img_path + 'quackle_game' + str(i).zfill(4)
                 + '_move' + str(j).zfill(2)
                 + '_option1.png')

        # now do data augmentation by transposing the board:
        base_layer[1:16, 1:16] = base_layer[1:16, 1:16].T
        move_layer[1:16, 1:16] = move_layer[1:16, 1:16].T
        score_layer[1:16, 1:16] = score_layer[1:16, 1:16].T

        # save the transposed version:
        rgb = zip((base_layer.astype(int)).flatten() * 9, (score_layer.astype(int)).flatten() * 9,
                  (move_layer.astype(int)).flatten() * 9)
        rgb = [pixel for pixel in rgb]
        img = Image.new('RGB', (16, 16))
        img.putdata(rgb)
        img = img.resize((256, 256), Image.NEAREST)
        img.save(img_path + 'quackle_game' + str(i).zfill(4)
                 + '_move' + str(j).zfill(2)
                 + '_option2.png')

        # now actually execute the move to prepare the board for the next move:

        # we've probably fake-played all the tiles so put them back in the rack:
        game.active_player.rack = cached_rack

        # only bother playing the move if it actually changes the board,
        # since we're not tracking what's in the bag, or what the current scores are:
        if quackle_move.direction is not Direction.NOT_APPLICABLE:
            # ensure the row we're using is a slice of the board, not a copy:
            if quackle_move.row:
                quackle_move.row = game.board.get_row(quackle_move.row.rank, quackle_move.row.direction)

            # clear move validation and re-validate the move, in doing so play it onto the correct row:
            quackle_move.is_valid = None
            game.validator.is_valid(quackle_move)

            game.execute_move(quackle_move)


for i in range(205, 2567):
    path = gcg_path + 'game_' + str(i).zfill(4) + '.gcg'
    with open(path, 'r') as f:
        lines = f.readlines()
        process_game(lines, i)



#