from typing import Optional

import numpy as np

from .. import constants


class Fractal:
    """The class that implement different type of fractal functions."""

    def __init__(
        self,
        func_type=constants.BURNING_SHIP,
        x_min=-2.0,
        x_max=0.5,
        y_min=-1.25,
        y_max=1.25,
        width=512,
        height=512,
        max_iters=100,
    ) -> None:
        self.func_type = func_type
        self.x_min: float = x_min
        self.x_max: float = x_max
        self.y_min: float = y_min
        self.y_max: float = y_max
        self.width: int = width
        self.height: int = height
        self.max_iters: int = max_iters

        self._image_pixels: Optional[np.array] = None

    @property
    def image_pixels(self):
        return self._image_pixels

    @image_pixels.setter
    def image_pixels(self, pixles):
        self._image_pixels = pixles

    def update(
        self,
        func_type=None,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None,
        width=None,
        height=None,
        max_iters=None,
    ):
        x_min = self.x_min if x_min is None else x_min
        x_max = self.x_max if x_max is None else x_max
        y_min = self.y_min if y_min is None else y_min
        y_max = self.y_max if y_max is None else y_max
        width = self.width if width is None else width
        height = self.height if height is None else height
        max_iters = self.max_iters if max_iters is None else max_iters
        func_type = self.func_type if func_type is None else func_type

        if func_type in constants.FRACTAL_FUNCTIONS:
            if hasattr(self, f"{func_type}_set"):
                func = getattr(self, f"{func_type}_set")
                pixels = func(
                    x_min,
                    x_max,
                    y_min,
                    y_max,
                    width,
                    height,
                    max_iters,
                )
                self.image_pixels = pixels
            else:
                raise AttributeError(f"{func_type} has no implementation yet.")
        else:
            raise ValueError(f"{func_type} does not supported.")

    def burningship_set(
        self, x_min, x_max, y_min, y_max, width=512, height=512, max_iters=100
    ):
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)

        pixels = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                c = x[j] + y[i] * 1j
                z = c
                for n in range(max_iters):
                    if abs(z) > 2**2:
                        pixels[i, j] = n
                        break
                    z = (abs(z.real) + 1j * abs(z.imag)) ** 2 + c
                else:
                    pixels[i, j] = 0
        return pixels

    def mandelbrot_set(
        self, x_min, x_max, y_min, y_max, width=512, height=512, max_iters=100
    ):
        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)

        pixels = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                c = x[j] + y[i] * 1j
                z = c
                for n in range(max_iters):
                    if abs(z) > 2**2:
                        pixels[i, j] = n
                        break
                    z = z ** 2 + c
                else:
                    pixels[i, j] = max_iters
        return pixels
