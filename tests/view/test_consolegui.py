from view.consolegui import ConsoleGui
from controller.game import GameController
from controller.game import GameController
from view.consolegui import ConsoleGui
from model.humanplayer import HumanPlayer
from model.bag import Bag




import re
from controller.game import GameController
from model.move import Move
from model.config import BOARD_SIZE, Direction
from model.movevalidator import MoveValidationError
from model.tile import Tile
from view.view import View



def test_create_gui():
    players = [None, None]
    bag = Bag()
    game = GameController(players, bag)
    gui = ConsoleGui(game)

def test_parseMovestring():
    bag = Bag()
    game = GameController([None, None], bag)
    gui = ConsoleGui(game)
    player1 = HumanPlayer(bag, gui, "Player 1")
    player2 = HumanPlayer(bag, gui, "Player 2")
    game.players = [player1, player2]
    game.active_player = player1
    player1.rack.rack_tiles[0] = Tile('A')
    player1.rack.rack_tiles[1] = Tile('C')
    player1.rack.rack_tiles[2] = Tile('T')
    move = gui.parse_move_string('F8HCAT')





#
#     # delete anything other than alphanumeric characters or '?':
#     input_string = self.strip_invalid_characters(input_string)
#
#     if not input_string:
#         return self.passing_move()
#
#     if not self.contains_digits(input_string):
#         return self.tile_exchange_move(input_string)
#
#     # if we got this far we're trying to do a standard move:
#     # reject strings not long enough to have square+direction+at least 1 tile,
#     # or with no character following a blankChar
#     if len(input_string) < 4 or input_string.endswith("?"):
#         raise MoveValidationError("Invalid number of tiles")
#
#     # make a list to store tiles for the move:
#     tiles_to_play = []
#     # get starting square:
#     x = ord(input_string[0]) - 64
#     y = self.digits_in_string(input_string)
#
#     # now strip digits out:
#     input_string = self.letters_in_string(input_string)
#
#     # get direction. This should be at index 1 now we've removed numbers:
#     if input_string[1] == 'H':
#         direction = Direction.HORIZONTAL
#         row = self.board.get_row(y, Direction.HORIZONTAL)
#         starting_square = x
#     elif input_string[1] == 'V':
#         direction = Direction.VERTICAL
#         row = self.board.get_row(x, Direction.VERTICAL)
#         starting_square = y
#     else:
#         raise ValueError("Direction invalid")
#
#     # remove digits then lop off square and direction, to leave actual letters for move
#     input_string = input_string[2:]
#     # process blanks:
#     first_blank_index = -1
#     while "?" in input_string:
#         first_blank_index = input_string.index('?')
#         blankChar = input_string[first_blank_index + 1]
#         # process tiles up to and including blankChar:
#         try:
#             tiles_to_play.extend(
#                 self.game.active_player.rack
#                     .getTiles(input_string[:first_blank_index + 1])
#             )
#         except ValueError as ex:
#             print(str(ex))
#             return None
#
#         # get the blankChar from the end of the list of tiles, and set to desired letter:
#         blankTile = tiles_to_play[-1]
#         blankTile.letter = blankChar
#
#         # delete processed tiles from input:
#         input_string = input_string[(first_blank_index + 2):]
#
#     # now do tiles after blank:
#     try:
#         tiles_to_play.extend(
#             self.game.active_player.rack
#                 .get_tiles(input_string[first_blank_index + 1:])
#         )
#     except ValueError as ex:
#         print(str(ex))
#         return None
#
#
#     return Move(row, starting_square, tiles_to_play)
#
# def strip_invalid_characters(self, input_string):
#     return re.sub("[^A-Z0-9?]", "", input_string.upper())
#
# def letters_in_string(self, input_string):
#     return ''.join([c for c in input_string if not c.isdigit()])
#
# def digits_in_string(self, input_string: str):
#     return int(''.join([c for c in input_string if c.isdigit()]))
#
# def passing_move(self):
#     return Move(None, None, None)  # will execute a pass
#
# def tile_exchange_move(self, input_string: str):
#     try:
#         tiles_to_play = self.game.active_player.rack.get_tiles(input_string)
#     except ValueError as ex:
#         print(str(ex))
#         return None
#     return Move(None, None, tiles_to_play)
#
# def contains_digits(self, input_string: str):
#     return re.match(".*\\d.*", input_string)
