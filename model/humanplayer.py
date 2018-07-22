from model.player import Player
from model.bag import Bag
from view.view import View


class HumanPlayer(Player):
    """ represents a human-controlled player """

    def __init__(self, bag: Bag, gui: View, name: str):
        """ Create a new game move """
        super().__init__(bag, gui, name)

    def get_move(self):
        return self.view.get_move()

    def get_starting_move(self):
        return self.get_move()
