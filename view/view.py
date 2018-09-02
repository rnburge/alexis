from controller.game import GameController

class View:
    """ a headless user interface. Normally you would use a subclass such as ConsoleGui,
     although this one is helpful for AI players not requiring game progress to be displayed """

    def __init__(self, game: GameController):
        self.game = game
        self.board = game.board

    def update_view(self):
        pass

