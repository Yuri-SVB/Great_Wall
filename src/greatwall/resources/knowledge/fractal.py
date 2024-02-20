from typing import Optional, Union

import numpy as np

from .. import constants


class Fractal:
    """The class that implement different type of fractal functions."""

    def __init__(
        self,
        func_type=constants.BURNING_SHIP,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None,
        p_param=None,
        width=None,
        height=None,
        max_iters=None,
    ) -> None:
        self.func_type = func_type
        self.x_min: Optional[float] = x_min
        self.x_max: Optional[float] = x_max
        self.y_min: Optional[float] = y_min
        self.y_max: Optional[float] = y_max
        self.p_param: Optional[float] = p_param
        self.width: Optional[int] = width
        self.height: Optional[int] = height
        self.max_iters: Optional[int] = max_iters

        self._image_pixels: Optional[np.array] = None

    def get_valid_parameter_from_value(self, value: Union[bytes, bytearray]):
        real_part = "2." + str(int.from_bytes(bytes(list(value)[0:2]), "big"))[::-1]
        imaginary_part = "0." + str(int.from_bytes(bytes(list(value)[2:4]), "big"))[::-1]

        return complex(float(real_part), float(imaginary_part))

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
        p_param=None,
        width=None,
        height=None,
        max_iters=None,
    ):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.p_param = p_param
        self.width = width
        self.height = height
        self.max_iters = max_iters
        self.func_type = func_type

        if func_type in constants.FRACTAL_FUNCTIONS:
            if hasattr(self, f"{func_type}_set"):
                fractal_func = getattr(self, f"{func_type}_set")
                self.image_pixels = fractal_func()
                return self.image_pixels
            else:
                raise AttributeError(f"{func_type} has no implementation yet.")
        else:
            raise ValueError(f"{func_type} does not supported.")

    def burningship_set(
        self,
        x_min=-2.5,
        x_max=2.0,
        y_min=-2,
        y_max=0.8,
        p_param=2.0,
        width=1024,
        height=1024,
        max_iters=22,
    ):
        x_min = x_min if self.x_min is None else self.x_min
        x_max = x_max if self.x_max is None else self.x_max
        y_min = y_min if self.y_min is None else self.y_min
        y_max = y_max if self.y_max is None else self.y_max
        p_param = p_param if self.p_param is None else self.p_param
        width = width if self.width is None else self.width
        height = height if self.height is None else self.height
        max_iters = max_iters if self.max_iters is None else self.max_iters

        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)

        pixels = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                c = x[j] + y[i] * 1j
                z = c
                for n in range(max_iters):
                    if abs(z) > 100:
                        pixels[i, j] = n
                        break
                    z = (abs(z.real) + (1j * abs(z.imag))) ** p_param + c
                else:
                    pixels[i, j] = max_iters
        return pixels

    def mandelbrot_set(
        self,
        x_min=-2.2,
        x_max=1,
        y_min=-1.2,
        y_max=1.2,
        p_param=2.0,
        width=1024,
        height=1024,
        max_iters=22,
    ):
        x_min = x_min if self.x_min is None else self.x_min
        x_max = x_max if self.x_max is None else self.x_max
        y_min = y_min if self.y_min is None else self.y_min
        y_max = y_max if self.y_max is None else self.y_max
        p_param = p_param if self.p_param is None else self.p_param
        width = width if self.width is None else self.width
        height = height if self.height is None else self.height
        max_iters = max_iters if self.max_iters is None else self.max_iters

        x = np.linspace(x_min, x_max, width)
        y = np.linspace(y_min, y_max, height)

        pixels = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                c = x[j] + y[i] * 1j
                z = c
                for n in range(max_iters):
                    if abs(z) > 100:
                        pixels[i, j] = n
                        break
                    z = z**p_param + c
                else:
                    pixels[i, j] = max_iters
        return pixels
