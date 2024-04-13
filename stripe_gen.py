from typing import List
from PIL import Image
import numpy as np
import random as r

from image_utils import Square, image_from_squares


def generate_striped_static(width: int, height: int, square_side: int, colors: List[str]) -> Image:
    """Generates an image. In each row, it puts strips of squares with random length and color.

    Args:
        width (int): width of the image
        height (int): height of the image
        square_side (int): the size of each square comprising the image
        colors (List): the colors from which the generator will choose to color the strips of squares
    """
    per_row = height // square_side
    per_col = width // square_side
    strip_lengths = range(2, 10)
    sum_of_squares = 0

    squares = np.array([Square] * per_row * per_col).reshape(per_row, per_col)

    i = j = 0
    while i < per_row:
        j = sum_of_squares = 0
        while j < per_col:
            color = r.choice(colors)

            while True:
                strip_len = r.choice(strip_lengths)
                sum_of_squares += strip_len

                if sum_of_squares <= per_col:
                    break
                else:
                    sum_of_squares -= strip_len
                    if sum_of_squares >= per_col - 1:
                        break

            # color the strip
            for k in range(strip_len):
                # break if the square at index (j + k) is out of bounds
                if j + k >= per_col:
                    break
                squares[i, j + k] = Square(square_side, color)

            # move the index to the end of the strip
            j += strip_len

        # if the last two sqaures' colors don't match, recolor the last
        # square to avoid a single colored square at the end of the row
        if squares[i, -1].color != squares[i, -2].color:
            squares[i, -1].recolor(squares[i, -2].color)
        #
        i += 1

    return image_from_squares(per_row, per_col , square_side, squares)