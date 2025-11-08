"""Custom exceptions for RL Arena."""

from typing import Any


class RLArenaException(Exception):
    """Base exception for all RL Arena errors."""

    pass


class EnvironmentError(RLArenaException):
    """Raised when there is an error with the environment itself."""

    pass


class EnvironmentNotFoundError(EnvironmentError):
    """Raised when attempting to create an environment that doesn't exist."""

    pass


class InvalidActionError(RLArenaException):
    """Raised when an agent takes an invalid action."""

    def __init__(self, action: Any, player_id: int, message: str = ""):
        """
        Initialize the exception.

        Args:
            action: The invalid action that was taken
            player_id: The ID of the player who took the invalid action
            message: Optional additional error message
        """
        self.action = action
        self.player_id = player_id

        if not message:
            message = f"Player {player_id} took invalid action: {action}"

        super().__init__(message)


class InvalidConfigurationError(EnvironmentError):
    """Raised when environment configuration is invalid."""

    pass


class GameEndedError(RLArenaException):
    """Raised when trying to step in an environment that has already ended."""

    pass


class InvalidPlayerError(RLArenaException):
    """Raised when an invalid player ID is used."""

    def __init__(self, player_id: int, num_players: int):
        """
        Initialize the exception.

        Args:
            player_id: The invalid player ID
            num_players: The number of players in the environment
        """
        message = f"Invalid player ID: {player_id}. " f"Must be between 0 and {num_players - 1}"
        super().__init__(message)
