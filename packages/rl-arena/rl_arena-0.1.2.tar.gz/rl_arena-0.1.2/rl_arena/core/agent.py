"""Agent interface for RL Arena."""

from abc import ABC, abstractmethod
from typing import Any
from rl_arena.core.types import ObservationType, ActionType


class Agent(ABC):
    """
    Abstract base class for agents that can play in RL Arena environments.

    This interface defines the minimal contract that an agent must fulfill
    to participate in RL Arena competitions.
    """

    def __init__(self, player_id: int = 0):
        """
        Initialize the agent.

        Args:
            player_id: The player ID assigned to this agent (0-indexed)
        """
        self.player_id = player_id

    @abstractmethod
    def act(self, observation: ObservationType) -> ActionType:
        """
        Choose an action based on the current observation.

        This is the main method that must be implemented by all agents.

        Args:
            observation: The current observation from the environment

        Returns:
            The action to take

        Example:
            >>> agent = MyAgent(player_id=0)
            >>> action = agent.act(observation)
            >>> print(action)
            1  # Action chosen by the agent
        """
        pass

    def reset(self) -> None:
        """
        Reset the agent's internal state (if any).

        This method is called at the start of each episode.
        Override this if your agent maintains internal state.
        """
        pass

    def save(self, path: str) -> None:
        """
        Save the agent's state to disk.

        Args:
            path: Path where to save the agent

        Note:
            Override this method if your agent needs to be saved/loaded.
        """
        raise NotImplementedError("This agent does not support saving")

    @classmethod
    def load(cls, path: str) -> "Agent":
        """
        Load an agent from disk.

        Args:
            path: Path to the saved agent

        Returns:
            The loaded agent instance

        Note:
            Override this method if your agent needs to be saved/loaded.
        """
        raise NotImplementedError("This agent does not support loading")


class RandomAgent(Agent):
    """
    A simple random agent for testing and baseline purposes.

    This agent selects actions uniformly at random from the action space.
    """

    def __init__(self, action_space: Any, player_id: int = 0):
        """
        Initialize the random agent.

        Args:
            action_space: The action space (Gymnasium Space object)
            player_id: The player ID assigned to this agent
        """
        super().__init__(player_id)
        self.action_space = action_space

    def act(self, observation: ObservationType) -> ActionType:
        """
        Select a random action.

        Args:
            observation: The current observation (unused for random agent)

        Returns:
            A random action sampled from the action space
        """
        return self.action_space.sample()
