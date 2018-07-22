import numpy as np
from enum import Enum

# value of tiles starting with blank, then A-Z
LETTER_VALUES = [
    0, 1, 3, 3, 2, 1, 4, 2,
    4, 1, 8, 5, 1, 3, 1, 1,
    3, 10, 1, 1, 1, 1, 4, 4,
    8, 4, 10
]

# number of instances of tiles, starting with blank, then A-Z
LETTER_DISTRIBUTIONS = [
    2, 9, 2, 2, 4, 12, 2, 3,
    2, 9, 1, 1, 4, 2, 6, 8,
    2, 1, 6, 4, 6, 4, 2, 2,
    1, 2, 1
]

# no of tiles that must be left in the bag to allow exchanging letters
EXCHANGE_LIMIT = 1

# number of consecutive passes before game over
PASS_LIMIT = 2

# bonus points for playing entire full rack
BONUS = 50

# grid dimensions (NB, zero indexed and includes 2 sentinel squares)
BOARD_SIZE = 16

# number of tiles in a full rack
RACK_SIZE = 7


class Direction(Enum):
    NOT_APPLICABLE = -1
    HORIZONTAL = 0
    VERTICAL = 1

    def __str__(self):
        return str(self._name_).capitalize()