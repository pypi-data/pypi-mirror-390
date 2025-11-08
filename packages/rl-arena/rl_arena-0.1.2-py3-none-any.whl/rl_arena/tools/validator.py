"""Environment validation tools for RL-Arena.

This module provides utilities to validate that custom environments
properly implement the RL-Arena API.
"""

import inspect
import warnings
from typing import Any, Dict, List, Optional, Type, Tuple
import numpy as np
import gymnasium as gym

from rl_arena.core.environment import Environment
from rl_arena.core.types import ActionType, ObservationType


class ValidationError(Exception):
    """Raised when environment validation fails."""

    pass


class ValidationWarning(UserWarning):
    """Warning for non-critical validation issues."""

    pass


class EnvironmentValidator:
    """Validates that an environment follows RL-Arena API specifications."""

    def __init__(self, env_class: Type[Environment], verbose: bool = True):
        """
        Initialize the validator.

        Args:
            env_class: The environment class to validate (not an instance)
            verbose: Whether to print detailed validation progress
        """
        self.env_class = env_class
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Run all validation checks on the environment.

        Args:
            config: Optional configuration to pass to environment constructor

        Returns:
            True if validation passes, False otherwise

        Raises:
            ValidationError: If critical validation fails
        """
        if self.verbose:
            print(f"🔍 Validating {self.env_class.__name__}...")
            print("=" * 60)

        try:
            # Create environment instance
            env = self._create_environment(config)

            # Run validation checks
            self._check_inheritance(env)
            self._check_properties(env)
            self._check_spaces(env)
            self._check_reset(env)
            self._check_step(env)
            self._check_render(env)
            self._check_seeding(env)
            self._check_invalid_actions(env)
            self._check_episode_termination(env)

            # Report results
            self._report_results()

            # Return success status
            if self.errors:
                raise ValidationError(f"Validation failed with {len(self.errors)} error(s)")

            return True

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self.errors.append(f"Unexpected error during validation: {str(e)}")
            raise ValidationError(f"Validation failed: {str(e)}")

    def _create_environment(self, config: Optional[Dict[str, Any]] = None) -> Environment:
        """Create environment instance for testing."""
        try:
            env = self.env_class(configuration=config)
            if self.verbose:
                print(f"✓ Environment created successfully\n")
            return env
        except Exception as e:
            self.errors.append(f"Failed to create environment: {str(e)}")
            raise ValidationError(f"Cannot create environment: {str(e)}")

    def _check_inheritance(self, env: Environment) -> None:
        """Check that environment inherits from Environment base class."""
        if self.verbose:
            print("📋 Checking inheritance...")

        if not isinstance(env, Environment):
            self.errors.append(f"{self.env_class.__name__} must inherit from Environment")
        else:
            if self.verbose:
                print("  ✓ Inherits from Environment\n")

    def _check_properties(self, env: Environment) -> None:
        """Check required properties exist and have correct types."""
        if self.verbose:
            print("📋 Checking required properties...")

        # Check num_players
        try:
            num_players = env.num_players
            if not isinstance(num_players, int):
                self.errors.append(f"num_players must be int, got {type(num_players)}")
            elif num_players < 1:
                self.errors.append(f"num_players must be >= 1, got {num_players}")
            else:
                if self.verbose:
                    print(f"  ✓ num_players: {num_players}")
        except Exception as e:
            self.errors.append(f"num_players property error: {str(e)}")

        # Check action_space
        try:
            action_space = env.action_space
            if not isinstance(action_space, gym.Space):
                self.errors.append(f"action_space must be gym.Space, got {type(action_space)}")
            else:
                if self.verbose:
                    print(f"  ✓ action_space: {action_space}")
        except Exception as e:
            self.errors.append(f"action_space property error: {str(e)}")

        # Check observation_space
        try:
            observation_space = env.observation_space
            if not isinstance(observation_space, gym.Space):
                self.errors.append(
                    f"observation_space must be gym.Space, got {type(observation_space)}"
                )
            else:
                if self.verbose:
                    print(f"  ✓ observation_space: {observation_space}")
        except Exception as e:
            self.errors.append(f"observation_space property error: {str(e)}")

        # Check metadata
        if not hasattr(env, "metadata"):
            self.warnings.append("Environment should have 'metadata' attribute")
        elif "render_modes" not in env.metadata:
            self.warnings.append("metadata should contain 'render_modes'")
        else:
            if self.verbose:
                print(f"  ✓ metadata: {env.metadata['render_modes']}")

        if self.verbose:
            print()

    def _check_spaces(self, env: Environment) -> None:
        """Check that spaces are properly defined."""
        if self.verbose:
            print("📋 Checking space definitions...")

        # Test action space sampling
        try:
            action = env.action_space.sample()
            if self.verbose:
                print(f"  ✓ action_space.sample() works: {action}")
        except Exception as e:
            self.errors.append(f"action_space.sample() failed: {str(e)}")

        # Test observation space sampling
        try:
            obs = env.observation_space.sample()
            if self.verbose:
                print(f"  ✓ observation_space.sample() works")
        except Exception as e:
            self.errors.append(f"observation_space.sample() failed: {str(e)}")

        # Test action space contains
        try:
            action = env.action_space.sample()
            if not env.action_space.contains(action):
                self.errors.append("action_space.sample() returns invalid action")
            else:
                if self.verbose:
                    print(f"  ✓ action_space.contains() works")
        except Exception as e:
            self.errors.append(f"action_space.contains() failed: {str(e)}")

        if self.verbose:
            print()

    def _check_reset(self, env: Environment) -> None:
        """Check reset() method works correctly."""
        if self.verbose:
            print("📋 Checking reset() method...")

        # Test basic reset
        try:
            observations, info = env.reset()

            # Check observations type
            if not isinstance(observations, list):
                self.errors.append(
                    f"reset() must return list of observations, got {type(observations)}"
                )
            elif len(observations) != env.num_players:
                self.errors.append(
                    f"reset() must return {env.num_players} observations, got {len(observations)}"
                )
            else:
                # Check each observation
                for i, obs in enumerate(observations):
                    if not env.observation_space.contains(obs):
                        self.errors.append(f"Observation {i} from reset() not in observation_space")

            # Check info type
            if not isinstance(info, dict):
                self.errors.append(f"reset() must return dict info, got {type(info)}")

            if not self.errors:
                if self.verbose:
                    print(f"  ✓ reset() returns correct types")
                    print(f"  ✓ Observations: {len(observations)} players")

        except Exception as e:
            self.errors.append(f"reset() failed: {str(e)}")

        # Test reset with seed
        try:
            obs1, _ = env.reset(seed=42)
            obs2, _ = env.reset(seed=42)
            obs3, _ = env.reset(seed=123)

            # Check determinism
            if not self._observations_equal(obs1, obs2):
                self.warnings.append(
                    "reset(seed=42) produces different observations (should be deterministic)"
                )
            else:
                if self.verbose:
                    print(f"  ✓ reset(seed=X) is deterministic")

            # Check different seeds produce different results (usually)
            if self._observations_equal(obs1, obs3):
                self.warnings.append(
                    "reset() with different seeds produces same observations (might be ok)"
                )

        except Exception as e:
            self.warnings.append(f"reset(seed=X) failed: {str(e)}")

        if self.verbose:
            print()

    def _check_step(self, env: Environment) -> None:
        """Check step() method works correctly."""
        if self.verbose:
            print("📋 Checking step() method...")

        try:
            # Reset environment
            observations, info = env.reset(seed=42)

            # Sample actions
            actions = [env.action_space.sample() for _ in range(env.num_players)]

            # Take step
            new_obs, rewards, terminated, truncated, info = env.step(actions)

            # Check observations
            if not isinstance(new_obs, list):
                self.errors.append(f"step() must return list of observations, got {type(new_obs)}")
            elif len(new_obs) != env.num_players:
                self.errors.append(
                    f"step() must return {env.num_players} observations, got {len(new_obs)}"
                )
            else:
                for i, obs in enumerate(new_obs):
                    if not env.observation_space.contains(obs):
                        self.errors.append(f"Observation {i} from step() not in observation_space")

            # Check rewards
            if not isinstance(rewards, list):
                self.errors.append(f"step() must return list of rewards, got {type(rewards)}")
            elif len(rewards) != env.num_players:
                self.errors.append(
                    f"step() must return {env.num_players} rewards, got {len(rewards)}"
                )
            else:
                for i, reward in enumerate(rewards):
                    if not isinstance(reward, (int, float, np.number)):
                        self.errors.append(f"Reward {i} must be numeric, got {type(reward)}")

            # Check terminated
            if not isinstance(terminated, bool):
                self.errors.append(f"step() terminated must be bool, got {type(terminated)}")

            # Check truncated
            if not isinstance(truncated, bool):
                self.errors.append(f"step() truncated must be bool, got {type(truncated)}")

            # Check info
            if not isinstance(info, dict):
                self.errors.append(f"step() info must be dict, got {type(info)}")

            if not self.errors:
                if self.verbose:
                    print(f"  ✓ step() returns correct types")
                    print(f"  ✓ Observations: {len(new_obs)}")
                    print(f"  ✓ Rewards: {rewards}")
                    print(f"  ✓ Terminated: {terminated}, Truncated: {truncated}")

        except Exception as e:
            self.errors.append(f"step() failed: {str(e)}")

        if self.verbose:
            print()

    def _check_render(self, env: Environment) -> None:
        """Check render() method works for all modes."""
        if self.verbose:
            print("📋 Checking render() methods...")

        # Reset environment first
        try:
            env.reset(seed=42)
        except Exception:
            pass  # Already tested in _check_reset

        # Test each render mode
        render_modes = env.metadata.get("render_modes", [])

        for mode in render_modes:
            try:
                if mode == "html":
                    # HTML requires state recording
                    env.enable_state_recording(True)
                    env.reset(seed=42)
                    env.step([env.action_space.sample() for _ in range(env.num_players)])

                result = env.render(mode=mode)

                # Check return types
                if mode == "human" or mode == "ipython":
                    if result is not None:
                        self.warnings.append(
                            f"render('{mode}') should return None, got {type(result)}"
                        )
                elif mode == "rgb_array":
                    if not isinstance(result, np.ndarray):
                        self.errors.append(
                            f"render('rgb_array') must return numpy array, got {type(result)}"
                        )
                    elif result.ndim != 3:
                        self.errors.append(
                            f"render('rgb_array') must return 3D array (H,W,C), got shape {result.shape}"
                        )
                elif mode == "ansi":
                    if not isinstance(result, str):
                        self.errors.append(f"render('ansi') must return string, got {type(result)}")
                elif mode == "html":
                    if not isinstance(result, str):
                        self.errors.append(f"render('html') must return string, got {type(result)}")

                if self.verbose:
                    print(f"  ✓ render('{mode}') works")

            except Exception as e:
                # IPython rendering is optional
                if mode == "ipython" and "IPython" in str(e):
                    self.warnings.append(f"render('ipython') requires IPython: {str(e)}")
                    if self.verbose:
                        print(f"  ⚠ render('ipython') skipped (IPython not installed)")
                else:
                    self.errors.append(f"render('{mode}') failed: {str(e)}")

        if self.verbose:
            print()

    def _check_seeding(self, env: Environment) -> None:
        """Check that seeding works correctly."""
        if self.verbose:
            print("📋 Checking reproducibility (seeding)...")

        try:
            # Run two episodes with same seed
            seed = 12345

            # Episode 1
            obs1, _ = env.reset(seed=seed)
            trajectory1 = [obs1]
            for _ in range(10):
                actions = [env.action_space.sample() for _ in range(env.num_players)]
                obs, rewards, terminated, truncated, _ = env.step(actions)
                trajectory1.append((obs, rewards, terminated, truncated))
                if terminated or truncated:
                    break

            # Episode 2
            obs2, _ = env.reset(seed=seed)
            trajectory2 = [obs2]
            for _ in range(10):
                actions = [env.action_space.sample() for _ in range(env.num_players)]
                obs, rewards, terminated, truncated, _ = env.step(actions)
                trajectory2.append((obs, rewards, terminated, truncated))
                if terminated or truncated:
                    break

            # Check if trajectories match
            if len(trajectory1) != len(trajectory2):
                self.warnings.append(
                    f"Same seed produces different trajectory lengths: {len(trajectory1)} vs {len(trajectory2)}"
                )
            else:
                # Check initial observations
                if not self._observations_equal(trajectory1[0], trajectory2[0]):
                    self.warnings.append("Same seed produces different initial observations")
                else:
                    if self.verbose:
                        print(f"  ✓ Seeding is reproducible")
                        print(f"  ✓ Trajectory length: {len(trajectory1)}")

        except Exception as e:
            self.warnings.append(f"Seeding check failed: {str(e)}")

        if self.verbose:
            print()

    def _check_invalid_actions(self, env: Environment) -> None:
        """Check that invalid actions are handled gracefully."""
        if self.verbose:
            print("📋 Checking invalid action handling...")

        env.reset(seed=42)

        # Test with wrong number of actions
        try:
            env.step([env.action_space.sample()])  # Only 1 action instead of num_players
            self.warnings.append("step() accepts wrong number of actions (should validate)")
        except (ValueError, AssertionError, IndexError):
            if self.verbose:
                print(f"  ✓ Rejects wrong number of actions")
        except Exception as e:
            self.warnings.append(f"Unexpected error with wrong action count: {str(e)}")

        # Test with invalid action values
        try:
            if isinstance(env.action_space, gym.spaces.Discrete):
                invalid_action = env.action_space.n + 10  # Out of range
                actions = [invalid_action] * env.num_players
                env.step(actions)
                self.warnings.append("step() accepts invalid actions (should validate or clip)")
            elif self.verbose:
                print(f"  ⚠ Cannot test invalid actions for {type(env.action_space)}")
        except (ValueError, AssertionError, IndexError):
            if self.verbose:
                print(f"  ✓ Rejects invalid action values")
        except Exception as e:
            self.warnings.append(f"Unexpected error with invalid actions: {str(e)}")

        if self.verbose:
            print()

    def _check_episode_termination(self, env: Environment) -> None:
        """Check that episodes terminate properly."""
        if self.verbose:
            print("📋 Checking episode termination...")

        try:
            env.reset(seed=42)
            max_steps = 1000
            terminated = False
            truncated = False

            for step in range(max_steps):
                actions = [env.action_space.sample() for _ in range(env.num_players)]
                obs, rewards, terminated, truncated, info = env.step(actions)

                if terminated or truncated:
                    if self.verbose:
                        print(f"  ✓ Episode terminates after {step + 1} steps")
                        if terminated:
                            print(f"  ✓ Terminal state reached")
                        if truncated:
                            print(f"  ✓ Episode truncated")
                    break

            if not (terminated or truncated):
                self.warnings.append(
                    f"Episode did not terminate within {max_steps} steps (might be ok for some environments)"
                )

        except Exception as e:
            self.errors.append(f"Episode termination check failed: {str(e)}")

        if self.verbose:
            print()

    def _observations_equal(self, obs1: List[ObservationType], obs2: List[ObservationType]) -> bool:
        """Check if two observation lists are equal."""
        if len(obs1) != len(obs2):
            return False

        for o1, o2 in zip(obs1, obs2):
            if isinstance(o1, np.ndarray) and isinstance(o2, np.ndarray):
                if not np.array_equal(o1, o2):
                    return False
            elif o1 != o2:
                return False

        return True

    def _report_results(self) -> None:
        """Print validation results."""
        print("=" * 60)
        print("📊 VALIDATION RESULTS")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All checks passed! Environment is valid.")
        elif not self.errors:
            print(f"\n✅ Environment is valid (with {len(self.warnings)} warnings to review)")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s)")

        print("=" * 60)


def validate_environment(
    env_class: Type[Environment],
    config: Optional[Dict[str, Any]] = None,
    verbose: bool = True,
) -> bool:
    """
    Validate an environment class.

    Args:
        env_class: The environment class to validate (not an instance)
        config: Optional configuration to pass to environment
        verbose: Whether to print detailed results

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails

    Example:
        >>> from rl_arena.envs.pong import PongEnv
        >>> from rl_arena.tools.validator import validate_environment
        >>> validate_environment(PongEnv)
        True
    """
    validator = EnvironmentValidator(env_class, verbose=verbose)
    return validator.validate(config)
