"""
RL Arena - A Python library for competitive reinforcement learning environments.

Quick Start:
    >>> import rl_arena
    >>>
    >>> # Create environment
    >>> env = rl_arena.make("pong")
    >>>
    >>> # Train agent (requires stable-baselines3)
    >>> model = rl_arena.train_dqn("pong", total_timesteps=10000)
    >>>
    >>> # Evaluate agent
    >>> agent = rl_arena.create_agent(model)
    >>> results = rl_arena.evaluate(agent, "pong", n_episodes=10)
    >>>
    >>> # Create submission
    >>> rl_arena.create_submission(agent, "my_agent.py", agent_name="MyAgent")
"""

from rl_arena.version import __version__
from rl_arena.make import make, list_environments

# Core classes
from rl_arena.core.agent import Agent
from rl_arena.core.environment import Environment

# Training utilities
from rl_arena.training import (
    train_dqn,
    create_training_agent as create_agent,
    evaluate_agent as evaluate,
)

# Submission utilities
from rl_arena.submission import (
    create_submission_template as create_submission,
    validate_submission as validate,
    package_agent as package,
)

# Replay utilities
from rl_arena.utils.replay import (
    save_replay,
    load_replay,
    replay_to_html,
)


# Lazy import for interactive play (pygame is optional)
def play(*args, **kwargs):
    """Create an InteractivePlayer instance. Requires pygame."""
    from rl_arena.interactive import InteractivePlayer

    return InteractivePlayer(*args, **kwargs)


# Built-in agents
from rl_arena.agents import RandomAgent, RuleBasedAgent

__all__ = [
    # Version
    "__version__",
    # Core
    "make",
    "list_environments",
    "Agent",
    "Environment",
    # Training
    "train_dqn",
    "create_agent",
    "evaluate",
    # Submission
    "create_submission",
    "validate",
    "package",
    # Replay
    "save_replay",
    "load_replay",
    "replay_to_html",
    # Interactive
    "play",
    # Built-in agents
    "RandomAgent",
    "RuleBasedAgent",
]
