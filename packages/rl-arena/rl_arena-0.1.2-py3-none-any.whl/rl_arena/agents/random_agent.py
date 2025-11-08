"""Random agent that takes random actions."""

from typing import Optional
import numpy as np
from rl_arena.core.agent import Agent


class RandomAgent(Agent):
    """Agent that selects actions uniformly at random."""

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize random agent.

        Args:
            seed: Random seed for reproducibility
        """
        super().__init__()
        self.rng = np.random.RandomState(seed)

    def act(self, observation, info=None):
        """
        Select random action.

        Args:
            observation: Current observation (ignored)
            info: Additional info (ignored)

        Returns:
            Random action from [0, 1, 2] (UP, STAY, DOWN)
        """
        return self.rng.randint(0, 3)
