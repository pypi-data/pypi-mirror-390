"""Base Environment class for RL Arena."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional
import numpy as np
import gymnasium as gym
from rl_arena.core.types import ObservationType, ActionType, RewardType
from rl_arena.core.renderer import Renderer


class Environment(ABC):
    """
    Abstract base class for all RL Arena environments.

    This class defines the interface that all environments must implement.
    It follows the Gymnasium (OpenAI Gym) API pattern for compatibility.

    Attributes:
        num_players: Number of players/agents in the environment
        action_space: The action space for each player
        observation_space: The observation space for each player
        metadata: Environment metadata (render modes, etc.)
    """

    metadata: Dict[str, Any] = {"render_modes": ["human", "rgb_array", "ansi", "ipython", "html"]}

    def __init__(self, configuration: Optional[Dict[str, Any]] = None):
        """
        Initialize the environment.

        Args:
            configuration: Optional dictionary of configuration parameters
        """
        self.configuration = configuration or {}
        self._num_players: int = 2  # Default to 2-player games
        self._current_step: int = 0
        self._done: bool = False
        self._np_random: Optional[np.random.Generator] = None
        self._seed: Optional[int] = None
        self._renderer: Optional[Renderer] = None
        self._render_mode: Optional[str] = self.configuration.get("render_mode")
        self._state_history: List[Dict[str, Any]] = []
        self._record_states: bool = False

    @property
    @abstractmethod
    def num_players(self) -> int:
        """Return the number of players in the environment."""
        pass

    @property
    @abstractmethod
    def action_space(self) -> gym.Space:
        """
        Return the action space for the environment.

        For multi-agent environments, this typically returns the action space
        for a single agent (assuming all agents have the same action space).
        """
        pass

    @property
    @abstractmethod
    def observation_space(self) -> gym.Space:
        """
        Return the observation space for the environment.

        For multi-agent environments, this typically returns the observation
        space for a single agent.
        """
        pass

    @abstractmethod
    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ObservationType], Dict[str, Any]]:
        """
        Reset the environment to an initial state.

        Args:
            seed: Random seed for reproducibility
            options: Optional reset parameters

        Returns:
            observations: List of initial observations for each player
            info: Dictionary with auxiliary information

        Example:
            >>> observations, info = env.reset(seed=42)
            >>> print(len(observations))  # Should equal num_players
            2
        """
        pass

    @abstractmethod
    def step(
        self, actions: List[ActionType]
    ) -> Tuple[List[ObservationType], List[RewardType], bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.

        Args:
            actions: List of actions, one for each player

        Returns:
            observations: List of observations for each player after the step
            rewards: List of rewards for each player
            terminated: Whether the episode has ended (win/loss condition)
            truncated: Whether the episode was cut off (time limit, etc.)
            info: Dictionary with auxiliary information

        Example:
            >>> observations, rewards, terminated, truncated, info = env.step([action1, action2])
            >>> if terminated:
            ...     print(f"Game ended! Rewards: {rewards}")
        """
        pass

    def render(self, mode: Optional[str] = None) -> Optional[Any]:
        """
        Render the environment.

        Args:
            mode: Rendering mode (overrides render_mode set in constructor)
                - 'human': Render to the current display or terminal
                - 'rgb_array': Return an RGB array (numpy array)
                - 'ansi': Return a string (ANSI) representation
                - 'ipython': Display inline in Jupyter notebook
                - 'html': Return HTML5 animation (requires state history)

        Returns:
            Depends on mode:
                - None for 'human' and 'ipython' mode
                - numpy array for 'rgb_array' mode
                - string for 'ansi' and 'html' mode
        """
        mode = mode or self._render_mode
        if mode is None:
            raise ValueError("No render mode specified")

        if mode not in self.metadata["render_modes"]:
            raise ValueError(f"Unsupported render mode: {mode}")

        # Create renderer if needed
        if self._renderer is None:
            self._renderer = self._create_renderer()

        # Get current render state
        state = self._get_render_state()

        # Render based on mode
        if mode == "human":
            self._renderer.render_human(state)
            return None
        elif mode == "rgb_array":
            return self._renderer.render_frame(state)
        elif mode == "ansi":
            if hasattr(self._renderer, "render_ansi"):
                return self._renderer.render_ansi(state)
            return str(state)
        elif mode == "ipython":
            self._renderer.render_ipython(state)
            return None
        elif mode == "html":
            if not self._state_history:
                raise ValueError(
                    "No state history available for HTML rendering. Enable state recording first."
                )
            return self._renderer.render_html(self._state_history)

        return None

    @abstractmethod
    def _create_renderer(self) -> Renderer:
        """
        Create and return a renderer instance for this environment.

        Subclasses must implement this method to provide their specific renderer.

        Returns:
            Renderer instance for this environment
        """
        pass

    @abstractmethod
    def _get_render_state(self) -> Dict[str, Any]:
        """
        Get the current state in a format suitable for rendering.

        Subclasses must implement this to extract renderable information
        from their internal state.

        Returns:
            Dictionary containing all information needed for rendering
        """
        pass

    def enable_state_recording(self, enabled: bool = True) -> None:
        """
        Enable or disable state recording for replay functionality.

        When enabled, the environment will store state snapshots at each step,
        which can be used for HTML replay generation.

        Args:
            enabled: Whether to enable state recording
        """
        self._record_states = enabled
        if enabled and not self._state_history:
            self._state_history = []

    def get_state_history(self) -> List[Dict[str, Any]]:
        """
        Get the recorded state history.

        Returns:
            List of state dictionaries, one per step
        """
        return self._state_history.copy()

    def clear_state_history(self) -> None:
        """Clear the recorded state history."""
        self._state_history = []

    def _record_state(self) -> None:
        """Record current state if recording is enabled."""
        if self._record_states:
            state = self._get_render_state()
            state["step"] = self._current_step
            self._state_history.append(state)

    @abstractmethod
    def get_observation(self, player_id: int) -> ObservationType:
        """
        Get the current observation for a specific player.

        This method is useful for partially observable environments where
        each player sees a different view of the game state.

        Args:
            player_id: The ID of the player (0-indexed)

        Returns:
            The observation for the specified player

        Raises:
            ValueError: If player_id is invalid
        """
        pass

    def close(self) -> None:
        """
        Clean up environment resources.

        Override this method if your environment needs cleanup
        (e.g., closing windows, disconnecting from servers).
        """
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None

    def seed(self, seed: Optional[int] = None) -> List[int]:
        """
        Set the random seed for the environment.

        Args:
            seed: The random seed

        Returns:
            List of seeds used by the environment's random number generators

        Example:
            >>> env.seed(42)
            [42]
            >>> # Now all random operations in the environment will be reproducible
        """
        self._seed = seed
        self._np_random = np.random.default_rng(seed)
        return [seed] if seed is not None else []

    @property
    def np_random(self) -> np.random.Generator:
        """
        Get the numpy random number generator for this environment.

        This ensures lazy initialization of the RNG. If seed() hasn't been called,
        it initializes with None (non-deterministic).

        Returns:
            numpy random number generator

        Example:
            >>> # Use in subclasses for reproducible randomness
            >>> random_value = self.np_random.random()
            >>> random_int = self.np_random.integers(0, 10)
        """
        if self._np_random is None:
            self._np_random = np.random.default_rng(self._seed)
        return self._np_random

    @property
    def current_step(self) -> int:
        """Return the current step number."""
        return self._current_step

    @property
    def is_done(self) -> bool:
        """Return whether the episode is done."""
        return self._done

    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration of the environment.

        Returns:
            Dictionary of configuration parameters
        """
        return self.configuration.copy()
