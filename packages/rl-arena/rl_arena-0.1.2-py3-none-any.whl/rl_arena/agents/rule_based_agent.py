"""Rule-based agent using simple heuristics."""

import numpy as np
from rl_arena.core.agent import Agent


class RuleBasedAgent(Agent):
    """
    Simple rule-based agent for Pong.

    Strategy:
    - Move paddle towards the ball's y position
    - Add some reaction delay for realism
    """

    def __init__(self, reaction_speed: float = 0.8):
        """
        Initialize rule-based agent.

        Args:
            reaction_speed: How quickly to react (0.0-1.0)
                0.0 = no movement, 1.0 = perfect tracking
        """
        super().__init__()
        self.reaction_speed = reaction_speed
        self.rng = np.random.RandomState(42)

    def act(self, observation, info=None):
        """
        Select action based on ball position.

        Observation format (Pong):
            [paddle_y, ball_x, ball_y, ball_vx, ball_vy]

        Args:
            observation: Current observation
            info: Additional info (ignored)

        Returns:
            Action: 0 (UP), 1 (STAY), or 2 (DOWN)
        """
        # Parse observation
        paddle_y = observation[0]
        ball_y = observation[2]

        # Calculate distance to ball
        distance = ball_y - paddle_y

        # Add some noise for realism
        if self.rng.random() > self.reaction_speed:
            return 1  # STAY (missed reaction)

        # Move towards ball
        threshold = 0.05  # Dead zone
        if distance > threshold:
            return 2  # DOWN
        elif distance < -threshold:
            return 0  # UP
        else:
            return 1  # STAY
