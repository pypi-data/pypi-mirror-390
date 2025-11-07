"""
Package definition file.
"""

import importlib.metadata

from gymnasium.envs.registration import register

# Register the environment with Gymnasium
register(id="CollabSort-v0", entry_point="gym_collabsort.envs.env:CollabSortEnv")


# Make the version accessible within the package
try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development mode
