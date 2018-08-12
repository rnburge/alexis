from enum import Enum
import random
from model.board import GameBoard
from model.bag import Bag
from model.lexicon import Lexicon
from model.move import Move, Direction
from model.movevalidator import MoveValidator, MoveValidationError
from model.config import PASS_LIMIT
from typing import List
from model.player import Player


class GameState(Enum):
    PENDING = -1
    ENDED = 0
    FIRST_MOVE = 1
    RUNNING = 2


class GameController:
    """ Represents a game. """

    def __init__(self, players: List[Player], bag: Bag):
        """
        A class representing a crossword game.
        :param players: A list of players to participate in this game.
        'None' should be used in this List as a placeholder for any player clients yet to join.
        """
        self.players = players
        self.bag = bag
        self.active_player = None
        self.board = GameBoard()
        self.lexicon = Lexicon()
        self.validator = MoveValidator(self.lexicon, self.board)
        self.game_state = GameState.PENDING
        self.record_of_moves = {}
        self.move_number = 0

    def start_game(self):
        # check if all players are ready
        print("Waiting for players")
        while None in self.players:
            print("players: " + str(self.players))
            # time.sleep(0)

        # set start player
        random.shuffle(self.players)
        self.active_player = self.players[0]

        # start game flow
        print("Starting game")
        self.update_players()
        self.game_state = GameState.FIRST_MOVE

        while self.game_state is GameState.FIRST_MOVE:
            self.wait_for_first_move()

        while self.game_state is not GameState.ENDED:
            self.wait_for_move()

        self.adjust_final_scores()

        print("Game ended:")
        print("Final scores:\n")

        for player in self.players:
            print(player.name + " scored "
                  + str(player.score))

        print("\nMove list:")
        for key in self.record_of_moves:
            print("Move " + str(key) + ": "
                  + str(self.record_of_moves[key][0]
                        + " - rack leave: "
                        + str(self.record_of_moves[key][1])
                        + ", made word: "
                        + str(self.record_of_moves[key][2])
                        + " - "
                        + str(self.record_of_moves[key][3])))

    def wait_for_first_move(self):
        move = None

        try:
            while self.game_state is GameState.FIRST_MOVE and (move is None or not self.validator.is_valid(move)):
                move = self.active_player.get_starting_move()
                try:
                    self.validator.is_valid(move)
                except MoveValidationError:
                    continue

            if move.direction is not Direction.NOT_APPLICABLE:
                self.game_state = GameState.RUNNING

            if self.game_state is not GameState.ENDED:
                self.execute_move(move)
                self.change_active_player()
                self.update_players()

        except MoveValidationError as ex:
            print("Move invalid: " + str(ex))
            self.clean_up_invalid_move(move)
            return

        if move.direction is not Direction.NOT_APPLICABLE:
            self.game_state = GameState.RUNNING

    def wait_for_move(self):
        move = None

        try:
            while self.game_state is not GameState.ENDED and (move is None or not self.validator.is_valid(move)):
                move = self.active_player.get_move()
                try:
                    self.validator.is_valid(move)
                except MoveValidationError as ex:
                    print("something went wrong: " + str(ex))
                    continue

            if self.game_state is not GameState.ENDED:
                self.execute_move(move)
                self.change_active_player()
                self.update_players()

        except MoveValidationError as ex:
            print("Move invalid: " + str(ex))
            self.clean_up_invalid_move(move)
            return

    def update_players(self):
        """ notifies players that the view may have changed and
        so they should perform housekeeping """
        for player in self.players:
            player.notify_move_executed()

    def add_player(self, player: Player):
        if None in self.players:
            self.players.remove(None)
            self.players.append(player)

    def change_active_player(self):
        """ get the next player in the list of players, wrapping around the end of the list: """
        self.active_player = self.players[(self.players.index(self.active_player) + 1) % len(self.players)]

    def execute_move(self, move: Move):
        """ execute a previously validated move.
        :param move: the move to be executed
        """
        name = self.active_player.name
        rack_leave = str(self.active_player.rack) if self.active_player.rack else '-'
        word = move.row.word_at(move.start_index)

        if move.direction == Direction.NOT_APPLICABLE:
            if not move.tiles:
                self.execute_passing_move()
            else:  # we must be swapping letters
                self.execute_tile_exchange_move(move)
        else:
            self.execute_standard_move(move)

        self.move_number += 1
        self.record_of_moves[self.move_number] = (name, rack_leave, word, move)

    def execute_tile_exchange_move(self, move):
        new_tiles = self.bag.get_tiles(len(move.tiles))
        if len(new_tiles) < len(move.tiles):
            self.bag.add_tiles(new_tiles)  # put drawn tiles back, we won't be using them
            raise MoveValidationError(
                "Not enough tiles left in bag to perform exchange (only "
                + len(new_tiles) + " are left).")
        self.bag.add_tiles(move.tiles)
        self.active_player.pass_counter = 0  # reset consecutive passes
        self.active_player.rack.add_tiles(new_tiles)

    def execute_passing_move(self):
        self.active_player.pass_counter += 1

        game_ended_by_passing = all(player.pass_counter >= PASS_LIMIT for player in self.players)
        if game_ended_by_passing:
            print("Both players passed")
            self.game_state = GameState.ENDED
        return

    def execute_standard_move(self, move: Move):
        """ Play a previously validated move on the board.
        :param move: The move to be played.
        """
        self.validator.update_affected_squares(move)

        self.active_player.score += move.score
        self.active_player.pass_counter = 0  # reset consecutive passes
        self.active_player.rack.replenish_tiles()
        if not self.active_player.rack:
            self.game_state = GameState.ENDED

    def adjust_final_scores(self):
        # adjusts final scores based on letters left in rack

        adjustment = 0

        # deduct the value of any tiles left from each player's hand
        player_who_played_out = None

        for player in self.players:
            if len(player.rack) == 0:
                player_who_played_out = player
                continue
            remaining_tile_score = player.rack.score_of_remaining_tiles()
            self.move_number += 1
            self.record_of_moves[self.move_number] = \
                (player.name, player.rack, "n/a",
                 "Final score adjustment: -" + str(remaining_tile_score))
            player.score -= remaining_tile_score
            adjustment += remaining_tile_score

        # if the last player played out,
        # add the value of everyone else's tiles to their score
        if player_who_played_out:
            player_who_played_out.score += adjustment
            self.move_number += 1
            self.record_of_moves[self.move_number] = \
                (player_who_played_out.name,
                 player_who_played_out.rack, "n/a", "Final score adjustment: +" + str(adjustment))

    def clean_up_invalid_move(self, move: Move):
        try:
            self.active_player.rack.add_tiles(move.tiles)
        except AttributeError:
            pass
