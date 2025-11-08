"""Validation utilities for actions and configurations."""

from typing import Any, Dict, List, Optional
import gymnasium as gym

from rl_arena.core.exceptions import InvalidActionError, InvalidConfigurationError


def validate_action(
    action: Any,
    action_space: gym.Space,
    player_id: int,
) -> None:
    """
    Validate that an action is valid for the given action space.

    Args:
        action: The action to validate
        action_space: The action space to validate against
        player_id: The ID of the player taking the action

    Raises:
        InvalidActionError: If the action is not valid

    Example:
        >>> import gymnasium as gym
        >>> from rl_arena.utils import validate_action
        >>>
        >>> action_space = gym.spaces.Discrete(3)
        >>> validate_action(1, action_space, player_id=0)  # OK
        >>> validate_action(5, action_space, player_id=0)  # Raises InvalidActionError
    """
    if not action_space.contains(action):
        raise InvalidActionError(
            action=action,
            player_id=player_id,
            message=f"Action {action} is not in action space {action_space}",
        )


def validate_actions(
    actions: List[Any],
    action_space: gym.Space,
    num_players: int,
) -> None:
    """
    Validate a list of actions for all players.

    Args:
        actions: List of actions, one per player
        action_space: The action space to validate against
        num_players: Expected number of players

    Raises:
        ValueError: If the number of actions doesn't match num_players
        InvalidActionError: If any action is invalid
    """
    if len(actions) != num_players:
        raise ValueError(f"Expected {num_players} actions, got {len(actions)}")

    for player_id, action in enumerate(actions):
        validate_action(action, action_space, player_id)


def validate_configuration(
    configuration: Dict[str, Any],
    required_keys: List[str],
    optional_keys: Optional[List[str]] = None,
    key_types: Optional[Dict[str, type]] = None,
) -> None:
    """
    Validate an environment configuration dictionary.

    Args:
        configuration: The configuration to validate
        required_keys: List of required configuration keys
        optional_keys: List of optional configuration keys (default: [])
        key_types: Dictionary mapping keys to their expected types (default: {})

    Raises:
        InvalidConfigurationError: If the configuration is invalid

    Example:
        >>> config = {"max_steps": 1000, "ball_speed": 2.0}
        >>> validate_configuration(
        ...     config,
        ...     required_keys=["max_steps"],
        ...     optional_keys=["ball_speed", "paddle_height"],
        ...     key_types={"max_steps": int, "ball_speed": float}
        ... )
    """
    optional_keys = optional_keys or []
    key_types = key_types or {}

    # Check for required keys
    missing_keys = set(required_keys) - set(configuration.keys())
    if missing_keys:
        raise InvalidConfigurationError(f"Missing required configuration keys: {missing_keys}")

    # Check for unknown keys
    allowed_keys = set(required_keys) | set(optional_keys)
    unknown_keys = set(configuration.keys()) - allowed_keys
    if unknown_keys:
        raise InvalidConfigurationError(
            f"Unknown configuration keys: {unknown_keys}. " f"Allowed keys: {allowed_keys}"
        )

    # Check types
    for key, expected_type in key_types.items():
        if key in configuration:
            value = configuration[key]
            if not isinstance(value, expected_type):
                raise InvalidConfigurationError(
                    f"Configuration key '{key}' has type {type(value).__name__}, "
                    f"expected {expected_type.__name__}"
                )


def validate_observation_shape(
    observation: Any,
    observation_space: gym.Space,
) -> None:
    """
    Validate that an observation matches the observation space.

    Args:
        observation: The observation to validate
        observation_space: The observation space to validate against

    Raises:
        ValueError: If the observation doesn't match the space
    """
    if not observation_space.contains(observation):
        raise ValueError(
            f"Observation {observation} is not in observation space {observation_space}"
        )
