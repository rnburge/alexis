from controller.game import GameController
from model.board import GameBoard
from model.config import Direction
from model.move import Move
from model.tile import Tile
from view.consolegui import ConsoleGui
from model.aiplayer import AiPlayer
from model.bag import Bag


def test_init():
    players = [None, None]
    bag = Bag()
    game = GameController(players, bag)
    gui = ConsoleGui(game)
    player1 = AiPlayer(game, gui, "AI Player 1")
    player2 = AiPlayer(game, gui, "AI Player 2")
    game.players = [player1, player2]


def test_get_move():
    game, player1 = setup()
    move = player1.get_move()
    assert type(move) is Move


def test_generate_all_moves():
    game, player1 = setup()
    moves = player1.generate_all_moves()
    assert len(moves) > 0
    assert len(player1.rack) == 7


def test_best_move():
    game, player1 = setup()
    moves = player1.generate_all_moves()
    best_move = player1.best_move(moves)
    assert best_move == moves[0]
    assert len(moves) > 0
    assert best_move.score > 0


def test_moves_for_row():
    game, player1 = setup()
    row = game.board.get_row(8, Direction.HORIZONTAL)

    assert type(game) is GameController
    assert type(player1) is AiPlayer

    """ returns a list of all possible moves """
    valid_moves = []

    # grab a COPY of all the rows which have start squares/hooks in them:
    rows_to_consider = [player1.board.get_row(i, Direction.HORIZONTAL) for i in range(1, 16) if any(player1.board.hook_squares[i, :])]
    # now add columns:
    rows_to_consider.extend([player1.board.get_row(i, Direction.VERTICAL) for i in range(1, 16) if any(player1.board.hook_squares[:, i])])

    assert len(rows_to_consider) > 0
    print(len(rows_to_consider))
    valid_moves.extend(player1.moves_for_row(row))
    assert len(valid_moves) > 0


def test_play_on_square():
    pass


def test_extend_right():
    pass


def test_extend_left():
    pass


def test_permute_blanks():
    pass


def test_check_blank_permutations():
    pass


def setup() -> (GameController, AiPlayer):
    players = [None, None]
    bag = Bag()
    game = GameController(players, bag)
    gui = ConsoleGui(game)
    player1 = AiPlayer(game, gui, "AI Player 1")
    player2 = AiPlayer(game, gui, "AI Player 2")
    player1.rack.rack_tiles.clear()
    player1.rack.add_tiles([Tile('U'), Tile('Z'), Tile('Q'), Tile('X'), Tile('J'), Tile('V'), Tile('V')])
    game.players = [player1, player2]
    return (game, player1)
