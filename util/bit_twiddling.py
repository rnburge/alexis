import numpy as np


def read_bit(x: int, place: int):
    """ return: True if the bit of x at 'place' is set to 1."""
    bit_mask = 1 << place
    return (x & bit_mask) != 0


def set_bit(x: int, place: int):
    """ return: an integer with the bit at 'place' set to 1."""
    bit_mask = 1 << place
    return x | bit_mask


def clear_bit(x: int, place: int):
    """ return: an integer with the bit at 'place' cleared."""
    bit_mask = ~(1 << place)
    return x & bit_mask


def flip_bit(x: int, place: int):
    """ return: an integer with the bit at 'place' flipped."""
    bit_mask = 1 << place
    return x ^ bit_mask


def bool_array_from_uint32(x: int):
    return np.unpackbits(np.array([x], dtype='uint32').byteswap().view('uint8'))[::-1].view('bool')


def uint32_from_bool_array(x: np.ndarray):
    if len(x) == 26:
        x = x = np.pad(x, (1, 5), 'constant', constant_values=(True, True))
    return np.packbits(x[::-1]).view('uint32').byteswap()[0]
