import re
import os
from controller.game import GameController, GameState
from model.move import Move
from model.config import Direction
from model.movevalidator import MoveValidationError
from util.bit_twiddling import bool_array_from_uint32, read_bit
from view.view import View


class ConsoleGui(View):
    """ a text based user interface """

    def __init__(self, game: GameController):
        super().__init__(game)

    def update_view(self):
        self.cls()
        print(self.scores_as_string() + self.board_as_string() + self.rack_as_string())

    def scores_as_string(self):
        scores = "Score: "
        for player in self.game.players:
            scores += "[" + player.name + ": " + str(player.score) + "]"
        scores += "\n\n"
        return scores

    def rack_as_string(self):
        return "\n" \
               + self.game.active_player.name \
               + " rack: " \
               + str(self.game.active_player.rack) \
               + "\n"

    def board_as_string(self):
        return str(
            self.board) if self.game.game_state is not GameState.FIRST_MOVE else self.board.board_string_with_hooks()

    def get_move(self):
        print(self.game.active_player.name + """ to move
(format: <startSquare><H/V><Tiles>,
e.g. C8VDOG plays 'DOG' vertically from square C8
Use ?<Tile> for blank followed by desired letter,
e.g. C8VDO?G plays blank as 'G'
Enter <Tiles> only to exchange, nothing to pass, 
'exit()' to quit: """)
        move = None
        while move is None:
            # read user input
            user_input = input("")
            # exit, if user types 'exit'
            if user_input.upper() == "EXIT()":
                self.game.game_state = GameState.ENDED
            else:
                move = self.parse_move_string(user_input)
        return move

    def parse_move_string(self, input_string: str):
        # delete anything other than alphanumeric characters or '?':
        input_string = self.strip_invalid_characters(input_string)

        if not input_string:
            return self.passing_move()

        if not self.contains_digits(input_string):
            return self.tile_exchange_move(input_string)

        # if we got this far we're trying to do a standard move:
        # reject strings not long enough to have square+direction+at least 1 tile,
        # or with no character following a blankChar
        if len(input_string) < 4 or input_string.endswith("?"):
            '''DEBUG'''
            self.describe_square(input_string)
            '''DEBUG'''

            raise MoveValidationError("Invalid number of tiles")

        # get starting square:
        x = ord(input_string[0]) - 64
        y = self.digits_in_string(input_string)

        # now strip digits out:
        input_string = self.letters_in_string(input_string)

        # get direction. This should be at index 1 now we've removed numbers:
        if input_string[1] == 'H':
            row = self.board.get_row(y, Direction.HORIZONTAL)
            starting_square = x
        elif input_string[1] == 'V':
            row = self.board.get_row(x, Direction.VERTICAL)
            starting_square = y
        else:
            raise MoveValidationError("Direction invalid")

        # remove digits then lop off square and direction, to leave actual letters for move
        input_string = input_string[2:]

        # process blanks (converts ?A to a, ?B to b, etc):
        input_string = re.sub(r'\?.', lambda m: m.group(0).lower()[-1], input_string)

        if input_string not in self.game.active_player.rack:
            raise MoveValidationError("No such tiles in rack")

        tiles_to_play = self.game.active_player.rack.get_tiles(input_string)

        return Move(row, starting_square, tiles_to_play)

    @staticmethod
    def strip_invalid_characters(input_string):
        return re.sub("[^A-Z0-9?]", "", input_string.upper())

    @staticmethod
    def letters_in_string(input_string):
        return ''.join([c for c in input_string if not c.isdigit()])

    @staticmethod
    def digits_in_string(input_string: str):
        return int(''.join([c for c in input_string if c.isdigit()]))

    @staticmethod
    def passing_move():
        return Move(None, None, None)  # will execute a pass

    def tile_exchange_move(self, input_string: str):
        try:
            tiles_to_play = self.game.active_player.rack.get_tiles(input_string)
        except ValueError as ex:
            print(str(ex))
            return None
        return Move(None, None, tiles_to_play)

    @staticmethod
    def contains_digits(input_string: str):
        return re.match(".*\\d.*", input_string)

    @staticmethod
    def cls():
        os.system('cls' if os.name == 'nt' else 'clear')

    def describe_square(self, input_string):
        i = ord(input_string[0]) - 64
        row = self.board.get_row(self.digits_in_string(input_string), Direction.HORIZONTAL)

        print('hook_squares:               ' + str(row.hook_squares[i]))
        print('word_multiplier:            ' + str(row.word_multipliers[i]))
        print('letter_multiplier:          ' + str(row.letter_multipliers[i]))
        print('existing_letters:           ' + (
            'none' if not row.existing_letters[i] else chr(64 + (row.existing_letters[i]))))
        print('existing_letter_scores:     ' + str(row.existing_letter_scores[i]))
        print('this_row_crosschecks:       ' + str(bool_array_from_uint32(row.this_row_crosschecks[i]).astype(int)))
        print('this_row_crosschecks:       ' + ''.join(
            [chr(64 + j) for j in range(1, 27) if read_bit(row.this_row_crosschecks[i], j)]))
        print(
            'orthogonal_row_crosschecks: ' + str(bool_array_from_uint32(row.orthogonal_column_crosschecks[i]).astype(int)))
        print('orthogonal_row_crosschecks: ' + ''.join(
            [chr(64 + j) for j in range(1, 27) if read_bit(row.orthogonal_column_crosschecks[i], j)]))
        print('this_row_cross_scores:      ' + str(row.this_row_cross_scores[i]))
        print('column_play_scores:         ' + str(row.orthogonal_column_cross_scores[i]))
