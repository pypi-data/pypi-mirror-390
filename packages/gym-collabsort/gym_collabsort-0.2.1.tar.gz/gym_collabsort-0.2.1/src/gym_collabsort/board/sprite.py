"""
Base class for board elements.
"""

import math
from dataclasses import dataclass

import numpy as np
import pygame
from pygame.math import Vector2

from ..config import Config

"""
Sprites on the board (objects or arms) can be positioned either through their 2D coordinates (row, column)
on a imaginary matrix grid, or through the (x, y) location of their center relative to the top-left corner of the window.

Row and column indexes start at 1.
"""


@dataclass
class Coords:
    """2D coordinates of a sprite on the board"""

    row: int
    col: int

    def as_vector(self) -> np.ndarray:
        """Convert coordinates as a NumPy vector [row, col]"""

        return np.array((self.row, self.col))


def coords_from_tuple(coords: tuple[int, int]) -> Coords:
    """Create a Coords object from a tuple of 2D coordinates (row, col)"""

    return Coords(row=coords[0], col=coords[1])


class Sprite(pygame.sprite.Sprite):
    """Base class for board elements"""

    def __init__(
        self,
        location: Vector2,
        size: int,
        config: Config,
        transparent_background: bool = False,
    ):
        super().__init__()

        self.config = config

        # Init sprite image
        self.image = pygame.Surface(size=(size, size))
        self.image.fill(color=config.background_color)

        if transparent_background:
            # Make the rect pixels around the object shape transparent
            self.image.set_colorkey(config.background_color)

        # Define initial sprite location.
        self.location = location

    @property
    def location(self) -> Vector2:
        """Get location of sprite center, relative to board"""

        # Y is offsetted to take into account the placed objects line above the board
        return Vector2(
            self.rect.center[0],
            self.rect.center[1] - self.config.scorebar_height,
        )

    @location.setter
    def location(self, value: Vector2) -> None:
        """Center sprite around given relative location"""

        # Sprite location is relative to board.
        # Two lines above and below the board display the placed objects for each arm.
        # X is the same for relative and absolute locations.
        # Y is offsetted by the height of the robot score bar
        self.rect = self.image.get_rect(
            center=(value[0], value[1] + self.config.scorebar_height)
        )

    @property
    def location_abs(self) -> tuple[int, int]:
        """Get absolute location of sprite center"""

        return self.rect.center

    @location_abs.setter
    def location_abs(self, value: Vector2 | tuple[int, int]) -> None:
        """Center sprite around given absolute location"""

        self.rect = self.image.get_rect(center=value)

    @property
    def coords(self) -> Coords:
        """Return the 2D coordinates (row, col) of the sprite on the board"""

        # Col corresponds to x-axis (horizontal) location
        # Row corresponds to y-axis (vertical) location
        # Both values are round up since row and column indexes start at 1
        col = math.ceil(self.location[0] / self.config.board_cell_size)
        row = math.ceil(self.location[1] / self.config.board_cell_size)

        return Coords(row=row, col=col)

    def move(self, col_offset: int = 0, row_offset: int = 0) -> None:
        """Move sprite by the specified col (horizontal) and row (vertical) offsets"""

        # Compute absolute location of new sprite center
        new_center = Vector2(
            x=self.rect.center[0] + col_offset * self.config.board_cell_size,
            y=self.rect.center[1] + row_offset * self.config.board_cell_size,
        )
        self.location_abs = new_center
