import math
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw


class Shaper:
    def __init__(self, size: int = 101):
        self.size = size

        # Create a new image with a black background
        self.image = Image.new("RGB", (size, size), "black")
        self.draw = ImageDraw.Draw(self.image)

    @staticmethod
    def get_first_digit(number: bytes):
        bytes_1st_digit = int(str(number[0]))
        integer_1st_digit = str(bytes_1st_digit)[0]
        return int(integer_1st_digit)

    def draw_regular_shape(self, sides: Union[int, bytes, bytearray] = 3):
        if isinstance(sides, bytes) or isinstance(sides, bytearray):
            # If sides is given as bytes it will get the int of the first digit with an offset of 2
            sides = self.get_first_digit(sides) + 2
        size = self.size

        # Calculate the coordinates for the polygon points
        center_x, center_y = size // 2, size // 2

        # Calculate the angle step in radians for each vertex
        angle = 2 * math.pi / sides

        # Calculate the vertices
        vertices = [
            (
                int(center_x * math.sin(angle * i)) + center_x,
                -int(center_y * math.cos(angle * i)) + center_y,
            )
            for i in range(sides)
        ]

        # Draw the polygon
        self.draw.polygon(vertices, outline="white")
        # Showing for debugging purpose
        # self.image.show()
        return self.save_image(sides)

    def save_image(self, name):
        parent_path = Path(__file__).parent
        icons_folder_name = f"Icons"
        filename = f"s{name}-polygon.png"
        file_path = parent_path / Path(icons_folder_name) / Path(filename)
        self.image.save(file_path, format="png")
        return file_path
