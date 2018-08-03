from model.bag import Bag
from model.config import LETTER_VALUES
from model.rack import Rack


class Player:
    """ Represents a player. """

    def __init__(self, bag: Bag, view, name: str):
        """ Create a new game player """
        self.view = view
        self.score = 0
        self.pass_counter = 0
        self.name = name
        self.rack = Rack(bag)

    def get_move(self):
        """ Get the player to submit an attempted move.
            :return the prospective move the player has entered through the GUI.
        """
        raise NotImplementedError

    def notify_move_executed(self):
        """ Executed after the game controller indicates a move has been played
            (either by this player or an opponent), so that this player client knows
            that housekeeping should take place. This method takes care of updating
            the display to show the new move.
        """
        self.view.update_view()



