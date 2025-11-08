"""
Interactive Play Mode for RL-Arena

This module allows users to:
1. Play against trained agents
2. Watch agent vs agent matches live
3. Use pre-trained built-in agents
4. Control agents with keyboard/mouse in real-time

Inspired by kaggle-environments interactive mode.
"""

import time
import numpy as np
from typing import Optional, Dict, Any, Callable, TYPE_CHECKING

# Import pygame lazily to avoid ImportError when not using interactive mode
pygame = None

from rl_arena import make
from rl_arena.core.agent import Agent


def _ensure_pygame():
    """Ensure pygame is imported. Raises ImportError if not available."""
    global pygame
    if pygame is None:
        try:
            import pygame as pg

            globals()["pygame"] = pg
        except ImportError:
            raise ImportError(
                "pygame is required for interactive mode. "
                "Install it with: pip install 'rl-arena[interactive]' or pip install pygame"
            )


class HumanAgent(Agent):
    """Agent controlled by human player via keyboard."""

    def __init__(self, control_keys: Optional[Dict[str, int]] = None):
        """
        Initialize human agent.

        Args:
            control_keys: Mapping of pygame keys to actions
                Default: Arrow keys for UP/DOWN, SPACE for STAY
        """
        super().__init__()
        _ensure_pygame()

        self.current_action = 1  # Default: STAY
        self.control_keys = control_keys or {
            pygame.K_UP: 0,  # UP
            pygame.K_SPACE: 1,  # STAY
            pygame.K_DOWN: 2,  # DOWN
        }

    def act(self, observation, info=None):
        """Return currently pressed action."""
        return self.current_action

    def update_action(self, keys):
        """Update action based on pressed keys."""
        for key, action in self.control_keys.items():
            if keys[key]:
                self.current_action = action
                return
        # Default to STAY if no keys pressed
        self.current_action = 1


class InteractivePlayer:
    """
    Interactive player for RL-Arena environments.

    Allows human vs agent, agent vs agent, or human vs human gameplay
    with live visualization.
    """

    def __init__(
        self,
        env_name: str = "pong",
        config: Optional[Dict[str, Any]] = None,
        fps: int = 30,
    ):
        """
        Initialize interactive player.

        Args:
            env_name: Name of environment to play
            config: Environment configuration
            fps: Frames per second for rendering
        """
        # Ensure pygame is available
        _ensure_pygame()

        # Create environment with human rendering
        config = config or {}
        config["render_mode"] = "rgb_array"
        self.env = make(env_name, config)
        self.fps = fps

        # Initialize pygame
        pygame.init()
        self.clock = pygame.time.Clock()

        # Get first frame to determine window size
        obs, _ = self.env.reset()
        frame = self.env.render()
        self.screen_width = frame.shape[1]
        self.screen_height = frame.shape[0] + 100  # Extra space for UI

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption(f"RL-Arena Interactive: {env_name}")

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)

        # Game state
        self.running = True
        self.paused = False
        self.scores = [0, 0]
        self.episode_count = 0

    def play(
        self,
        player1_agent: Optional[Agent] = None,
        player2_agent: Optional[Agent] = None,
        max_episodes: Optional[int] = None,
        show_observations: bool = False,
    ):
        """
        Start interactive play session.

        Args:
            player1_agent: Agent for player 1 (None = human control)
            player2_agent: Agent for player 2 (None = human control)
            max_episodes: Maximum episodes to play (None = infinite)
            show_observations: Display observation values on screen

        Controls:
            Player 1 (Left): W/S or Arrow Up/Down
            Player 2 (Right): Arrow Up/Down or I/K
            SPACE: Pause/Resume
            R: Reset episode
            Q/ESC: Quit
        """
        # Setup human agents if needed
        if player1_agent is None:
            player1_agent = HumanAgent(
                {
                    pygame.K_w: 0,  # UP
                    pygame.K_s: 2,  # DOWN
                    pygame.K_LSHIFT: 1,  # STAY
                }
            )

        if player2_agent is None:
            player2_agent = HumanAgent(
                {
                    pygame.K_UP: 0,  # UP
                    pygame.K_DOWN: 2,  # DOWN
                    pygame.K_RSHIFT: 1,  # STAY
                }
            )

        # Game loop
        observations, info = self.env.reset()
        terminated = False
        truncated = False

        while self.running:
            # Handle events
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        observations, info = self.env.reset()
                        terminated = False
                        truncated = False
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        self.running = False

            # Update human agents
            if isinstance(player1_agent, HumanAgent):
                player1_agent.update_action(keys)
            if isinstance(player2_agent, HumanAgent):
                player2_agent.update_action(keys)

            # Game step (if not paused)
            if not self.paused and not (terminated or truncated):
                # Get actions
                action1 = player1_agent.act(observations[0], info)
                action2 = player2_agent.act(observations[1], info)
                actions = [action1, action2]

                # Step environment
                observations, rewards, terminated, truncated, info = self.env.step(actions)

                # Update scores
                if "scores" in info:
                    self.scores = info["scores"]

                # Check episode end
                if terminated or truncated:
                    self.episode_count += 1
                    if max_episodes and self.episode_count >= max_episodes:
                        self.running = False
                    else:
                        # Auto-reset after 2 seconds
                        self._show_episode_end(rewards)
                        time.sleep(2)
                        observations, info = self.env.reset()
                        terminated = False
                        truncated = False

            # Render
            self._render_frame(observations, show_observations)

            # Control frame rate
            self.clock.tick(self.fps)

        pygame.quit()

    def _render_frame(self, observations, show_observations: bool):
        """Render current frame with UI."""
        # Get game frame
        frame = self.env.render()

        # Convert to pygame surface
        frame_surface = pygame.surfarray.make_surface(np.transpose(frame, (1, 0, 2)))

        # Draw game
        self.screen.fill((0, 0, 0))
        self.screen.blit(frame_surface, (0, 0))

        # Draw UI at bottom
        ui_y = frame.shape[0]
        pygame.draw.rect(self.screen, (40, 40, 40), (0, ui_y, self.screen_width, 100))

        # Draw scores
        score_text = self.font_large.render(
            f"{self.scores[0]}  -  {self.scores[1]}", True, (255, 255, 255)
        )
        score_rect = score_text.get_rect(center=(self.screen_width // 2, ui_y + 30))
        self.screen.blit(score_text, score_rect)

        # Draw controls
        controls_text = self.font_small.render(
            "SPACE: Pause | R: Reset | Q: Quit", True, (200, 200, 200)
        )
        controls_rect = controls_text.get_rect(center=(self.screen_width // 2, ui_y + 70))
        self.screen.blit(controls_text, controls_rect)

        # Draw paused indicator
        if self.paused:
            pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
            pause_rect = pause_text.get_rect(center=(self.screen_width // 2, frame.shape[0] // 2))
            # Draw background
            pygame.draw.rect(self.screen, (0, 0, 0, 128), pause_rect.inflate(40, 20))
            self.screen.blit(pause_text, pause_rect)

        # Show observations (debugging)
        if show_observations:
            self._draw_observations(observations, 10, 10)

        pygame.display.flip()

    def _draw_observations(self, observations, x: int, y: int):
        """Draw observation values on screen."""
        for i, obs in enumerate(observations):
            text = self.font_small.render(f"P{i+1}: {obs}", True, (255, 255, 255))
            self.screen.blit(text, (x, y + i * 25))

    def _show_episode_end(self, rewards):
        """Show episode end screen."""
        winner_text = ""
        if rewards[0] > rewards[1]:
            winner_text = "Player 1 Wins!"
            color = (100, 200, 255)
        elif rewards[1] > rewards[0]:
            winner_text = "Player 2 Wins!"
            color = (255, 100, 100)
        else:
            winner_text = "Draw!"
            color = (200, 200, 200)

        # Render winner text
        winner_surface = self.font_large.render(winner_text, True, color)
        winner_rect = winner_surface.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )

        # Draw semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Draw winner text
        self.screen.blit(winner_surface, winner_rect)

        pygame.display.flip()


def load_builtin_agent(agent_name: str) -> Agent:
    """
    Load a built-in pre-trained agent.

    Args:
        agent_name: Name of agent to load
            - "random": Random agent
            - "rule_based": Simple rule-based agent
            - "dqn_weak": Weakly trained DQN
            - "dqn_strong": Strongly trained DQN

    Returns:
        Agent instance
    """
    if agent_name == "random":
        from rl_arena.agents.random_agent import RandomAgent

        return RandomAgent()

    elif agent_name == "rule_based":
        from rl_arena.agents.rule_based_agent import RuleBasedAgent

        return RuleBasedAgent()

    elif agent_name == "dqn_weak":
        # TODO: Load pre-trained weak DQN model
        from rl_arena.agents.rule_based_agent import RuleBasedAgent

        return RuleBasedAgent()  # Placeholder

    elif agent_name == "dqn_strong":
        # TODO: Load pre-trained strong DQN model
        from rl_arena.agents.rule_based_agent import RuleBasedAgent

        return RuleBasedAgent()  # Placeholder

    else:
        raise ValueError(f"Unknown built-in agent: {agent_name}")


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RL-Arena Interactive Player")
    parser.add_argument("--env", default="pong", help="Environment name")
    parser.add_argument(
        "--player1",
        default="human",
        help="Player 1 agent (human, random, rule_based, dqn_weak, dqn_strong)",
    )
    parser.add_argument(
        "--player2",
        default="random",
        help="Player 2 agent (human, random, rule_based, dqn_weak, dqn_strong)",
    )
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--episodes", type=int, default=None, help="Maximum episodes to play")

    args = parser.parse_args()

    # Load agents
    player1 = None if args.player1 == "human" else load_builtin_agent(args.player1)
    player2 = None if args.player2 == "human" else load_builtin_agent(args.player2)

    # Start interactive player
    player = InteractivePlayer(
        env_name=args.env,
        fps=args.fps,
    )

    print("=" * 60)
    print("RL-ARENA INTERACTIVE PLAYER")
    print("=" * 60)
    print(f"Environment: {args.env}")
    print(f"Player 1: {args.player1}")
    print(f"Player 2: {args.player2}")
    print()
    print("Controls:")
    if args.player1 == "human":
        print("  Player 1: W (Up), S (Down)")
    if args.player2 == "human":
        print("  Player 2: Arrow Up/Down")
    print("  SPACE: Pause/Resume")
    print("  R: Reset episode")
    print("  Q/ESC: Quit")
    print("=" * 60)
    print()

    player.play(
        player1_agent=player1,
        player2_agent=player2,
        max_episodes=args.episodes,
    )
