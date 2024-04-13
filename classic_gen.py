from typing import List
from PIL import Image
import numpy as np
import random as r

from image_utils import Square, image_from_squares


def generate_classic_static(width: int, height: int, square_size: int, colors: List[str]) -> Image:
    # how many squares per row and column we need
    per_row = height // square_size
    per_col = width // square_size

    squares = np.array([Square] * per_row * per_col).reshape(per_row, per_col)

    for i in range(per_row):
        for j in range(per_col):
            color = r.choice(colors)
            squares[i, j] = Square(square_size, color)
        #
    #
    return image_from_squares(per_row, per_col , square_size, squares)