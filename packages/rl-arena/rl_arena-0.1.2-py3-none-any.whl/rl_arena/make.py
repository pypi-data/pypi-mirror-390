"""Factory function for creating RL Arena environments."""

from typing import Dict, Any, Optional
from rl_arena.envs.registry import ENVIRONMENT_REGISTRY
from rl_arena.core.environment import Environment
from rl_arena.core.exceptions import EnvironmentNotFoundError


def make(env_name: str, configuration: Optional[Dict[str, Any]] = None) -> Environment:
    """
    Create an environment by name.

    This is the main factory function for creating RL Arena environments.
    It follows the same pattern as OpenAI Gym's make() function.

    Args:
        env_name: The name of the environment to create (e.g., "pong", "connect4")
        configuration: Optional dictionary of configuration parameters to override
                      the environment's defaults. Configuration options are
                      environment-specific.

    Returns:
        An instance of the requested environment

    Raises:
        EnvironmentNotFoundError: If the environment name is not registered

    Example:
        >>> import rl_arena
        >>> env = rl_arena.make("pong")
        >>> observations = env.reset()
        >>>
        >>> # With custom configuration
        >>> env = rl_arena.make("pong", configuration={
        ...     "max_steps": 2000,
        ...     "ball_speed": 2.0
        ... })
    """
    if env_name not in ENVIRONMENT_REGISTRY:
        available = ", ".join(sorted(ENVIRONMENT_REGISTRY.keys()))
        raise EnvironmentNotFoundError(
            f"Environment '{env_name}' not found. " f"Available environments: {available}"
        )

    env_class = ENVIRONMENT_REGISTRY[env_name]

    if configuration is None:
        configuration = {}

    return env_class(configuration=configuration)


def list_environments() -> list[str]:
    """
    List all registered environments.

    Returns:
        A sorted list of environment names that can be passed to make()

    Example:
        >>> import rl_arena
        >>> print(rl_arena.list_environments())
        ['connect4', 'pong', 'tictactoe']
    """
    return sorted(ENVIRONMENT_REGISTRY.keys())
