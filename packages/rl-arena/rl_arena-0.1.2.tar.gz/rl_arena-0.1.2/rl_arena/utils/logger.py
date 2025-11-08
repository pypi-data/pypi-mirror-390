"""Logging utilities for RL Arena."""

import logging
import sys
from typing import Optional
from pathlib import Path


# Default logging format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: str = DEFAULT_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
) -> None:
    """
    Set up logging configuration for RL Arena.

    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Optional file path to write logs to
        format_string: Format string for log messages
        date_format: Format string for timestamps

    Example:
        >>> from rl_arena.utils import setup_logging
        >>> import logging
        >>>
        >>> # Setup basic logging
        >>> setup_logging(level=logging.INFO)
        >>>
        >>> # Setup with file output
        >>> setup_logging(level=logging.DEBUG, log_file="logs/rl_arena.log")
    """
    # Create formatter
    formatter = logging.Formatter(format_string, datefmt=date_format)

    # Setup root logger
    root_logger = logging.getLogger("rl_arena")
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> from rl_arena.utils import get_logger
        >>>
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting training")
        >>> logger.debug("Current step: 100")
        >>> logger.warning("High loss detected")
        >>> logger.error("Training failed")
    """
    return logging.getLogger(f"rl_arena.{name}")


class CompetitionLogger:
    """
    Specialized logger for tracking competition metrics.

    This logger provides structured logging for competition events
    like matches, rounds, and player actions.
    """

    def __init__(self, name: str = "competition"):
        """
        Initialize the competition logger.

        Args:
            name: Name of the logger
        """
        self.logger = get_logger(name)
        self.match_id: Optional[str] = None

    def start_match(self, match_id: str, players: list[str]) -> None:
        """Log the start of a match."""
        self.match_id = match_id
        self.logger.info(f"Match {match_id} started with players: {', '.join(players)}")

    def log_step(
        self,
        step: int,
        actions: list,
        rewards: list[float],
    ) -> None:
        """Log a single step in the match."""
        self.logger.debug(
            f"[Match {self.match_id}] Step {step}: " f"actions={actions}, rewards={rewards}"
        )

    def end_match(
        self,
        winner: Optional[str],
        final_scores: list[float],
        num_steps: int,
    ) -> None:
        """Log the end of a match."""
        winner_str = winner if winner else "Draw"
        self.logger.info(
            f"Match {self.match_id} ended after {num_steps} steps. "
            f"Winner: {winner_str}, Final scores: {final_scores}"
        )
        self.match_id = None

    def log_error(self, error: Exception, context: str = "") -> None:
        """Log an error that occurred during the match."""
        context_str = f" ({context})" if context else ""
        self.logger.error(f"[Match {self.match_id}] Error{context_str}: {error}", exc_info=True)
