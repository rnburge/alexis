import sys
sys.path.append(',,')

from controller.game import GameController
from view.consolegui import ConsoleGui
from model.aiplayer import AiPlayer
from model.bag import Bag
from model.config import Direction
from model.row import Row
import numpy as np
import os
import copy
from model.config import LETTER_VALUES, NO_CROSS_WORD, RACK_SIZE, BONUS

players = [None, None]
bag = Bag()
game = GameController(players, bag)
gui = ConsoleGui(game)

path = '../gcg/'

print(os.listdir())


# later we'll loop through with:
# files = os.listdir('gcg')