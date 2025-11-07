"""
Base types and configuration values.
"""

import math
from dataclasses import dataclass
from enum import Enum

import numpy as np


class Color(Enum):
    """Possible colors for an object"""

    RED = 0
    BLUE = 1
    YELLOW = 2


def get_color_name(color: Color) -> str:
    """Return the name associated to a color"""

    if color == Color.RED:
        return "red"
    elif color == Color.BLUE:
        return "blue"
    elif color == Color.YELLOW:
        return "yellow"


class Shape(Enum):
    """Possible shapes for an object"""

    SQUARE = 0
    CIRCLE = 1
    TRIANGLE = 2


class Action(Enum):
    """Possible actions for agent and robot"""

    # Stand still or continue a previously initiated movement
    NONE = 0
    # Start movement to pick an object on the uppoer treadmill
    PICK_UPPER = 1
    # Start movement to pick an object on the lower treadmill
    PICK_LOWER = 2


@dataclass
class Config:
    """Configuration class with default values"""

    # Frames Per Second for environment rendering
    render_fps: int = 5

    # ---------- Window and board ----------

    # Number of board rows
    n_rows: int = 10

    # Number of board columns
    n_cols: int = 16

    # Size of a square board cell in pixels
    board_cell_size: int = 50

    @property
    def board_height(self) -> int:
        """Return the height of the board in pixels"""

        return self.n_rows * self.board_cell_size

    @property
    def board_width(self) -> int:
        """Return the width of the board in pixels"""

        return self.n_cols * self.board_cell_size

    # Width in pixels of delimitation line between score bar and board
    scorebar_line_thickness: int = 3

    # Margin around score bar content in pixels
    scorebar_margin: int = 3

    @property
    def scorebar_height(self) -> int:
        """Return the height of the score bar (which is an offset for vertical coordinates)"""

        return self.board_cell_size + self.scorebar_margin

    @property
    def window_dimensions(self) -> tuple[int, int]:
        """Return the dimensions (width, height) of the main window in pixels"""

        # Add heights of scorebars for robot and agent
        return (
            self.board_width,
            self.board_height + self.scorebar_height * 2,
        )

    # Title of the main window
    window_title = "gym-collabsort - Collaborative sorting task"

    # Background color of the window
    background_color: str = "white"

    # ---------- Treadmills ----------

    # Board row for the uppoer treadmill
    upper_treadmill_row = 4

    # Board row for the lower treadmill
    lower_treadmill_row = 7

    def get_target_coords(self, action: Action) -> tuple[int, int]:
        """Convert an action to the coordinates (row, col) of its target"""

        col = self.arm_base_col

        if action == Action.PICK_UPPER:
            row = self.upper_treadmill_row
        elif action == Action.PICK_LOWER:
            row = self.lower_treadmill_row
        else:
            raise Exception(f"Unable to convert action {action} to target coordinates")

        return row, col

    # Thickness of treadmill delimitation lines in pixels
    treadmill_line_thickness: int = 1

    # ---------- Objects ----------

    # Maximum number of objects. If 0, new objects will be added indefinitely
    n_objects: float = math.inf

    # Probability of adding a new object at each time step
    new_object_proba = 0.25

    # ---------- Agent and robot arms ----------

    # Board column where arm bases are placed
    arm_base_col: int = 4

    # Thickness of arm base lines in pixels
    arm_base_line_thickness: int = 5

    # Background color for arm base while in penalty mode
    arm_base_penalty_color: str = "orange"

    # Thickness of the line between arm base and gripper in pixels
    arm_line_thickness: int = 7

    # Size (height & width) of the agent and robot grippers in pixels
    arm_gripper_size: int = board_cell_size // 2

    # ---------- Rewards ----------

    # Duration in time steps of movement penalty after a collision.
    # Includes the steps needed to move grippers back to their base
    collision_penalty_steps: int = 20

    # Base step reward
    step_reward: float = 0

    @property
    def agent_rewards(self) -> np.ndarray[np.float64]:
        """Return the rewards array associated to object properties for the agent"""

        # Rows are indiced by object color, columns by object shape
        return np.array([[8, 7, 6], [5, 4, 3], [2, 1, 0]])

    @property
    def robot_rewards(self) -> np.ndarray[np.float64]:
        """Return the rewards array associated to object properties for the robot"""

        # Rows are indiced by object color, columns by object shape
        return np.array([[5, 4, 3], [8, 7, 6], [2, 1, 0]])
