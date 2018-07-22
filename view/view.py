from controller.game import GameController

class View:
    """ a user interface """

    def __init__(self, game: GameController):
        self.game = game
        self.board = game.board

