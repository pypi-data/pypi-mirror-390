"""Pong environment implementation."""

from typing import Any, Dict, List, Tuple, Optional
import numpy as np
import gymnasium as gym
from pathlib import Path
import yaml

from rl_arena.core.environment import Environment
from rl_arena.core.types import ObservationType, ActionType, RewardType
from rl_arena.core.exceptions import InvalidActionError, InvalidPlayerError, GameEndedError
from rl_arena.envs.registry import register_environment
from rl_arena.envs.pong.renderer import PongRenderer
from rl_arena.core.renderer import Renderer


@register_environment("pong")
class PongEnvironment(Environment):
    """
    A 2-player competitive Pong environment.

    State space:
        - Ball position (x, y): continuous values in [0, 1]
        - Ball velocity (vx, vy): continuous values
        - Paddle positions (y1, y2): continuous values in [0, 1]
        - Scores (score1, score2): discrete values

    Action space:
        Discrete(3) per player:
        - 0: Move UP
        - 1: STAY
        - 2: Move DOWN

    Rewards:
        - +1 for scoring a point
        - -1 for conceding a point
        - 0 otherwise

    Episode ends when:
        - A player reaches the winning score (default: 11)
        - Maximum steps reached (default: 1000)
    """

    metadata = {
        "render_modes": ["human", "rgb_array", "ansi", "ipython", "html"],
        "render_fps": 60,
    }

    # Action constants
    ACTION_UP = 0
    ACTION_STAY = 1
    ACTION_DOWN = 2

    def __init__(self, configuration: Optional[Dict[str, Any]] = None):
        """
        Initialize the Pong environment.

        Args:
            configuration: Optional configuration dictionary with keys:
                - width: Field width (default: 1.0)
                - height: Field height (default: 1.0)
                - paddle_height: Paddle height (default: 0.2)
                - paddle_speed: Paddle movement speed (default: 0.05)
                - ball_speed: Initial ball speed (default: 0.02)
                - ball_radius: Ball radius (default: 0.02)
                - winning_score: Score needed to win (default: 11)
                - max_steps: Maximum steps per episode (default: 1000)
        """
        super().__init__(configuration)

        # Load default configuration
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, "r") as f:
            default_config = yaml.safe_load(f)

        # Merge with provided configuration
        self.config = {**default_config, **self.configuration}

        # Environment parameters
        self.width = self.config["width"]
        self.height = self.config["height"]
        self.paddle_height = self.config["paddle_height"]
        self.paddle_speed = self.config["paddle_speed"]
        self.ball_speed = self.config["ball_speed"]
        self.ball_radius = self.config["ball_radius"]
        self.winning_score = self.config["winning_score"]
        self.max_steps = self.config["max_steps"]

        # Game state
        self.ball_pos = np.array([0.5, 0.5], dtype=np.float32)
        self.ball_vel = np.array([0.0, 0.0], dtype=np.float32)
        self.paddle1_y = 0.5
        self.paddle2_y = 0.5
        self.score1 = 0
        self.score2 = 0

        self._num_players = 2
        self._current_step = 0
        self._done = False

    @property
    def num_players(self) -> int:
        """Return the number of players (always 2 for Pong)."""
        return 2

    @property
    def action_space(self) -> gym.Space:
        """Return the action space (Discrete(3))."""
        return gym.spaces.Discrete(3)

    @property
    def observation_space(self) -> gym.Space:
        """
        Return the observation space.

        Observation is a vector of:
        [ball_x, ball_y, ball_vx, ball_vy, paddle1_y, paddle2_y, score1, score2]
        """
        return gym.spaces.Box(
            low=np.array([0.0, 0.0, -1.0, -1.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32),
            high=np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 100.0, 100.0], dtype=np.float32),
            dtype=np.float32,
        )

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ObservationType], Dict[str, Any]]:
        """Reset the environment to initial state."""
        # Set the seed using parent class method
        if seed is not None:
            super().seed(seed)

        # Reset game state
        self.ball_pos = np.array([0.5, 0.5], dtype=np.float32)

        # Random initial ball direction using the environment's RNG
        angle = self.np_random.uniform(-np.pi / 4, np.pi / 4)
        direction = 1 if self.np_random.random() < 0.5 else -1
        self.ball_vel = np.array(
            [direction * self.ball_speed * np.cos(angle), self.ball_speed * np.sin(angle)],
            dtype=np.float32,
        )

        self.paddle1_y = 0.5
        self.paddle2_y = 0.5
        self.score1 = 0
        self.score2 = 0
        self._current_step = 0
        self._done = False

        obs = self._get_observation_array()
        observations = [obs.copy(), obs.copy()]

        return observations, {"scores": [self.score1, self.score2]}

    def step(
        self, actions: List[ActionType]
    ) -> Tuple[List[ObservationType], List[RewardType], bool, bool, Dict[str, Any]]:
        """Execute one step in the environment."""
        if self._done:
            raise GameEndedError("Cannot step in an environment that has already ended")

        if len(actions) != 2:
            raise ValueError(f"Expected 2 actions, got {len(actions)}")

        # Validate and apply actions
        for i, action in enumerate(actions):
            if not self.action_space.contains(action):
                raise InvalidActionError(action, i)

        # Move paddles
        if actions[0] == self.ACTION_UP:
            self.paddle1_y = max(0.0, self.paddle1_y - self.paddle_speed)
        elif actions[0] == self.ACTION_DOWN:
            self.paddle1_y = min(1.0, self.paddle1_y + self.paddle_speed)

        if actions[1] == self.ACTION_UP:
            self.paddle2_y = max(0.0, self.paddle2_y - self.paddle_speed)
        elif actions[1] == self.ACTION_DOWN:
            self.paddle2_y = min(1.0, self.paddle2_y + self.paddle_speed)

        # Move ball
        self.ball_pos += self.ball_vel

        # Ball collision with top/bottom walls
        if self.ball_pos[1] <= 0.0 or self.ball_pos[1] >= 1.0:
            self.ball_vel[1] *= -1
            self.ball_pos[1] = np.clip(self.ball_pos[1], 0.0, 1.0)

        # Ball collision with paddles
        rewards = [0.0, 0.0]

        # Left paddle (player 1)
        if (
            self.ball_pos[0] - self.ball_radius <= 0.05
            and abs(self.ball_pos[1] - self.paddle1_y) <= self.paddle_height / 2
        ):
            self.ball_vel[0] = abs(self.ball_vel[0])
            # Add some randomness to the bounce
            self.ball_vel[1] += self.np_random.uniform(-0.01, 0.01)

        # Right paddle (player 2)
        if (
            self.ball_pos[0] + self.ball_radius >= 0.95
            and abs(self.ball_pos[1] - self.paddle2_y) <= self.paddle_height / 2
        ):
            self.ball_vel[0] = -abs(self.ball_vel[0])
            # Add some randomness to the bounce
            self.ball_vel[1] += self.np_random.uniform(-0.01, 0.01)

        # Check for scoring
        if self.ball_pos[0] <= 0.0:
            # Player 2 scores
            self.score2 += 1
            rewards = [-1.0, 1.0]
            self._reset_ball()
        elif self.ball_pos[0] >= 1.0:
            # Player 1 scores
            self.score1 += 1
            rewards = [1.0, -1.0]
            self._reset_ball()

        self._current_step += 1

        # Record state if recording is enabled
        self._record_state()

        # Check for episode end
        terminated = self.score1 >= self.winning_score or self.score2 >= self.winning_score
        truncated = self._current_step >= self.max_steps
        self._done = terminated or truncated

        obs = self._get_observation_array()
        observations = [obs.copy(), obs.copy()]

        info = {
            "scores": [self.score1, self.score2],
            "ball_pos": self.ball_pos.copy(),
            "paddle_positions": [self.paddle1_y, self.paddle2_y],
        }

        return observations, rewards, terminated, truncated, info

    def _create_renderer(self) -> Renderer:
        """Create and return a PongRenderer instance."""
        return PongRenderer(width=800, height=600)

    def _get_render_state(self) -> Dict[str, Any]:
        """Get the current state in a format suitable for rendering."""
        return {
            "ball": {"x": float(self.ball_pos[0]), "y": float(self.ball_pos[1])},
            "paddle1": {"y": float(self.paddle1_y)},
            "paddle2": {"y": float(self.paddle2_y)},
            "paddle_height": self.paddle_height,
            "score": [self.score1, self.score2],
        }

    def get_observation(self, player_id: int) -> ObservationType:
        """Get observation for a specific player."""
        if player_id not in [0, 1]:
            raise InvalidPlayerError(player_id, self.num_players)

        # In Pong, both players see the same state
        return self._get_observation_array()

    def close(self) -> None:
        """Clean up resources."""
        super().close()  # This will clean up the renderer

    def _get_observation_array(self) -> np.ndarray:
        """Get the current observation as a numpy array."""
        return np.array(
            [
                self.ball_pos[0],
                self.ball_pos[1],
                self.ball_vel[0],
                self.ball_vel[1],
                self.paddle1_y,
                self.paddle2_y,
                float(self.score1),
                float(self.score2),
            ],
            dtype=np.float32,
        )

    def _reset_ball(self) -> None:
        """Reset ball to center with random direction."""
        self.ball_pos = np.array([0.5, 0.5], dtype=np.float32)

        angle = self.np_random.uniform(-np.pi / 4, np.pi / 4)
        direction = 1 if self.np_random.random() < 0.5 else -1
        self.ball_vel = np.array(
            [direction * self.ball_speed * np.cos(angle), self.ball_speed * np.sin(angle)],
            dtype=np.float32,
        )
