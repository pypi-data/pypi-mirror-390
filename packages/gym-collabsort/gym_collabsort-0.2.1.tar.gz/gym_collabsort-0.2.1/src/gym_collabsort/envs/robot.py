"""
Implementation of robot policy.
"""

import numpy as np

from ..board.arm import Arm
from ..board.board import Board
from ..board.object import Object
from ..config import Action


class Robot:
    def __init__(
        self,
        board: Board,
        arm: Arm,
        rewards: np.ndarray,
    ) -> None:
        self.board = board
        self.arm = arm
        self.rewards = rewards

        # Location of current target (an object or the arm base)
        self.target_location: tuple[int, int] = None

    def choose_action(self) -> Action:
        """Return the chosen action"""

        action = Action.NONE

        if self.arm.is_retracted():
            # Search for the next target object
            next_target = self._get_next_target()

            if next_target is not None:
                next_target_coords = next_target.coords

                if (next_target_coords.col - self.arm.gripper.coords.col) == abs(
                    next_target_coords.row - self.arm.gripper.coords.row
                ):
                    # Target is pickable if movement starts now
                    action = (
                        Action.PICK_LOWER
                        if next_target_coords.row
                        == self.board.config.lower_treadmill_row
                        else Action.PICK_UPPER
                    )

        return action

    def _get_next_target(self) -> Object | None:
        """Return the next object target (the most rewarding of the objects reachable in the future)"""

        reachable_objects: list[Object] = []

        # Exclude objects impossible to pick because they are already too close to the arm column
        reachable_objects = [
            obj
            for obj in self.board.objects
            if (obj.coords.col - self.arm.gripper.coords.col)
            >= abs(obj.coords.row - self.arm.gripper.coords.row)
        ]

        if len(reachable_objects) > 0:
            # Sort reachable objects by descending reward
            reachable_objects.sort(
                key=lambda o: o.get_reward(rewards=self.rewards), reverse=True
            )

            # Return the reachable object with the highest reware
            return reachable_objects[0]

        # No reachable object
        return None
