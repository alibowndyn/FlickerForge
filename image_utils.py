from PIL import Image, ImageFilter

class Square():
    """A class that implements a square image with a given side length and color"""
    def __init__(self, side: int, color: str):
        self.side = side
        self.color = color
        self.image = Image.new(mode="RGB", size=(self.side, self.side), color=self.color)


    def recolor(self, new_color: str) -> None:
        """Recolors the square with the given color"""
        self.color = new_color
        self.image = Image.new(mode="RGB", size=(self.side, self.side), color=self.color)


def generate_gif(width: int, height: int, square_side=2, colors=[], blur=2, update_ui=None, generator=None, frames=10) -> None:
    """Generates multiple static images and saves them as a GIF file

    Args:
        update_ui (function): A callback function which updates the progress bar on the UI.
        generator (function): The function that will generate the static image.
    """
    images = []
    progress_counter = 0
    increment = 100 // frames
    blur_amount = blur

    for _ in range(frames):
        frame = generator(width, height, square_side, colors)

        # applying blur to the generated image
        frame = frame.filter(ImageFilter.BoxBlur(blur_amount))
        images.append(frame.copy())
        frame.close()

        # updating the progress
        progress_counter += increment
        update_ui(progress_counter)

    # saving the list of images as a GIF file
    images[0].save('static.gif',
                save_all=True,
                append_images=images[1:],
                duration=50,
                loop=0)

    # freeing resources
    # frame.close()
    # for image in images:
    #     image.close()
    #
#

def image_from_squares(squares_per_row, squares_per_column, square_side, square_matrix) -> Image:
    """Convert a matrix of squares to a single image"""
    w = squares_per_column * square_side
    h = squares_per_row * square_side

    canvas = Image.new(mode="RGB", size=(w, h))

    for i in range(squares_per_row):
        for j in range(squares_per_column):
            canvas.paste(
                im=square_matrix[i, j].image,
                box=(j * square_side, i * square_side, (j * square_side) + square_side, (i * square_side) + square_side))
        #
    #
    return canvas