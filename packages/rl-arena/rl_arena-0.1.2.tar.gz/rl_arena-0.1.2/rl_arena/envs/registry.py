"""Environment registry for RL Arena.

This module provides the registry system for environments, allowing
new environments to be registered and discovered dynamically.
"""

from typing import Dict, Type, Callable
from rl_arena.core.environment import Environment


# Global registry of all available environments
ENVIRONMENT_REGISTRY: Dict[str, Type[Environment]] = {}


def register_environment(name: str) -> Callable[[Type[Environment]], Type[Environment]]:
    """
    Decorator to register an environment in the global registry.

    This decorator should be used on all Environment subclasses to make
    them available via the make() factory function.

    Args:
        name: The name to register the environment under

    Returns:
        The decorator function

    Example:
        >>> @register_environment("my-game")
        ... class MyGameEnvironment(Environment):
        ...     pass
        >>>
        >>> # Now "my-game" can be created with make()
        >>> env = make("my-game")
    """

    def decorator(cls: Type[Environment]) -> Type[Environment]:
        if name in ENVIRONMENT_REGISTRY:
            raise ValueError(
                f"Environment '{name}' is already registered. "
                f"Existing: {ENVIRONMENT_REGISTRY[name].__name__}, "
                f"New: {cls.__name__}"
            )

        if not issubclass(cls, Environment):
            raise TypeError(f"Cannot register {cls.__name__}: must be a subclass of Environment")

        ENVIRONMENT_REGISTRY[name] = cls
        return cls

    return decorator


def unregister_environment(name: str) -> None:
    """
    Remove an environment from the registry.

    This is mainly useful for testing purposes.

    Args:
        name: The name of the environment to unregister

    Raises:
        KeyError: If the environment is not registered
    """
    if name not in ENVIRONMENT_REGISTRY:
        raise KeyError(f"Environment '{name}' is not registered")

    del ENVIRONMENT_REGISTRY[name]


def get_environment_class(name: str) -> Type[Environment]:
    """
    Get the environment class by name.

    Args:
        name: The name of the environment

    Returns:
        The environment class

    Raises:
        KeyError: If the environment is not registered
    """
    if name not in ENVIRONMENT_REGISTRY:
        available = ", ".join(sorted(ENVIRONMENT_REGISTRY.keys()))
        raise KeyError(f"Environment '{name}' not found. " f"Available environments: {available}")

    return ENVIRONMENT_REGISTRY[name]


# Import environments to trigger registration
# This ensures all environments are registered when the module is imported
from rl_arena.envs import pong  # noqa: E402, F401
