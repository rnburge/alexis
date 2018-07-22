from controller.game import GameController, GameState
from model.bag import Bag
from model.humanplayer import HumanPlayer
from view.consolegui import ConsoleGui

def test_init():
    players = [None, None]
    bag = Bag()
    game = GameController(players, bag)
    gui = ConsoleGui(game)
    player1 = HumanPlayer(bag, gui, "Player 1")
    player2 = HumanPlayer(bag, gui, "Player 2")
    game.players = [player1, player2]
    assert game.game_state == GameState.PENDING

def test_start_game():
    pass

def test_wait_for_move():
    pass

def test_update_players():
    pass

def test_add_player():
    pass

def test_change_active_player():
    players = [None, None]
    bag = Bag()
    game = GameController(players, bag)
    gui = ConsoleGui(game)
    player1 = HumanPlayer(bag, gui, "Player 1")
    player2 = HumanPlayer(bag, gui, "Player 2")
    game.players = [player1, player2]
    game.active_player = player1
    assert game.active_player == player1
    game.change_active_player()
    assert game.active_player == player2

def test_execute_move():
    pass

def test_execute_tile_exchange_move():
    pass

def test_execute_passing_move():
    pass

def test_execute_standard_move():
    pass

def test_adjust_final_scores():
    pass

def test_clean_up_invalid_move():
    pass
