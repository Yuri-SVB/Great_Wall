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
        real_p=None,
        imag_p=None,
        width=None,
        height=None,
        max_iters=None,
    ) -> None:
        self.func_type = func_type
        self.x_min: Optional[float] = x_min
        self.x_max: Optional[float] = x_max
        self.y_min: Optional[float] = y_min
        self.y_max: Optional[float] = y_max
        self.real_p: Optional[float] = real_p
        self.imag_p: Optional[float] = imag_p
        self.width: Optional[int] = width
        self.height: Optional[int] = height
        self.max_iters: Optional[int] = max_iters

        self._image_pixels: Optional[np.array] = None

    def get_valid_real_p_from(self, value: Union[bytes, bytearray]):
        # NOTE: We inverting the order of digits by operation [::-1] on string,
        # to minimize Benford's law bias.
        real_p = "2." + str(int.from_bytes(value, "big"))[::-1]
        return float(real_p)

    def get_valid_imag_p_from(self, value: Union[bytes, bytearray]):
        # NOTE: We inverting the order of digits by operation [::-1] on string,
        # to minimize Benford's law bias.
        imag_p = "0." + str(int.from_bytes(value, "big"))[::-1]
        return float(imag_p)

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
        real_p=None,
        imag_p=None,
        width=None,
        height=None,
        max_iters=None,
    ):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.real_p = real_p
        self.imag_p = imag_p
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
        real_p=2.0,
        imag_p=0.0,
        width=1024,
        height=1024,
        max_iters=22,
    ):
        x_min = x_min if self.x_min is None else self.x_min
        x_max = x_max if self.x_max is None else self.x_max
        y_min = y_min if self.y_min is None else self.y_min
        y_max = y_max if self.y_max is None else self.y_max
        real_p = real_p if self.real_p is None else self.real_p
        imag_p = imag_p if self.imag_p is None else self.imag_p
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
                    exponent = complex(real_p, imag_p)
                    z = (abs(z.real) + (1j * abs(z.imag))) ** exponent + c
                else:
                    pixels[i, j] = max_iters
        return pixels

    def mandelbrot_set(
        self,
        x_min=-2.2,
        x_max=1,
        y_min=-1.2,
        y_max=1.2,
        real_p=2.0,
        imag_p=0.0,
        width=1024,
        height=1024,
        max_iters=22,
    ):
        x_min = x_min if self.x_min is None else self.x_min
        x_max = x_max if self.x_max is None else self.x_max
        y_min = y_min if self.y_min is None else self.y_min
        y_max = y_max if self.y_max is None else self.y_max
        real_p = real_p if self.real_p is None else self.real_p
        imag_p = imag_p if self.imag_p is None else self.imag_p
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
                    z = z ** complex(real_p, imag_p) + c
                else:
                    pixels[i, j] = max_iters
        return pixels
