import random

from controller.game import GameController
from view.consolegui import ConsoleGui
from model.humanplayer import HumanPlayer
from model.aiplayer import AiPlayer
from model.bag import Bag


def main(args=None):
    """The main bootstrapping routine."""

    players = [None, None]
    bag = Bag()
    game = GameController(players, bag)
    gui = ConsoleGui(game)
    player1 = AiPlayer(game, gui, "AI Player 1")
    player2 = AiPlayer(game, gui, "AI Player 2")
    #player1 = HumanPlayer(bag, gui, "Player 1")
    #player2 = HumanPlayer(bag, gui, "Player 2")
    game.players = [player1, player2]
    game.start_game()


if __name__ == "__main__":
    main()
