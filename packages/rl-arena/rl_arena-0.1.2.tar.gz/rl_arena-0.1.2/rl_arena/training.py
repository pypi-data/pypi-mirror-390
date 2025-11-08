"""
Helper utilities for training agents with popular RL libraries.
"""

from typing import Optional, Callable, Dict, Any
import numpy as np
from rl_arena.core.agent import Agent


class TrainingCallback:
    """
    Callback for monitoring training progress.

    Example:
        >>> from rl_arena.training import TrainingCallback
        >>> callback = TrainingCallback(log_interval=1000)
        >>> model.learn(total_timesteps=10000, callback=callback)
    """

    def __init__(
        self,
        log_interval: int = 1000,
        eval_env=None,
        eval_freq: int = 5000,
        n_eval_episodes: int = 5,
    ):
        self.log_interval = log_interval
        self.eval_env = eval_env
        self.eval_freq = eval_freq
        self.n_eval_episodes = n_eval_episodes
        self.episode_rewards: list[float] = []
        self.episode_lengths: list[int] = []

    def __call__(self, locals_dict, globals_dict):
        """Called by Stable-Baselines3 during training."""
        return True


def create_training_agent(model, deterministic: bool = True) -> Agent:
    """
    Wrap a trained model into an Agent for submission.

    Args:
        model: Trained model (e.g., from Stable-Baselines3)
        deterministic: Use deterministic actions

    Returns:
        Agent instance ready for submission

    Example:
        >>> from stable_baselines3 import DQN
        >>> from rl_arena.training import create_training_agent
        >>>
        >>> model = DQN.load("my_agent.zip")
        >>> agent = create_training_agent(model)
        >>>
        >>> # Test agent
        >>> env = make("pong")
        >>> obs, _ = env.reset()
        >>> action = agent.act(obs[0])
    """

    class TrainedAgent(Agent):
        def __init__(self):
            super().__init__()
            self.model = model
            self.deterministic = deterministic

        def act(self, observation, info=None):
            action, _ = self.model.predict(observation, deterministic=self.deterministic)
            return int(action)

    return TrainedAgent()


def evaluate_agent(
    agent: Agent,
    env_name: str,
    n_episodes: int = 10,
    render: bool = False,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Evaluate an agent's performance.

    Args:
        agent: Agent to evaluate
        env_name: Environment name
        n_episodes: Number of episodes to run
        render: Whether to render during evaluation
        seed: Random seed

    Returns:
        Dictionary with evaluation results:
        - mean_reward: Average episode reward
        - std_reward: Standard deviation of rewards
        - mean_length: Average episode length
        - episodes: List of individual episode results

    Example:
        >>> from rl_arena.training import evaluate_agent
        >>> from rl_arena.agents import RandomAgent
        >>>
        >>> agent = RandomAgent()
        >>> results = evaluate_agent(agent, "pong", n_episodes=10)
        >>> print(f"Mean reward: {results['mean_reward']:.2f}")
    """
    from rl_arena import make

    config = {"render_mode": "human" if render else None}
    env = make(env_name, config)

    episode_rewards = []
    episode_lengths = []

    for ep in range(n_episodes):
        if seed is not None:
            env.reset(seed=seed + ep)
        else:
            env.reset()

        observations, _ = env.reset()
        done = False
        episode_reward = 0
        episode_length = 0

        while not done:
            # Get actions (assuming 2-player)
            action1 = agent.act(observations[0])
            action2 = env.action_space.sample()  # Random opponent

            observations, rewards, terminated, truncated, info = env.step([action1, action2])

            episode_reward += rewards[0]  # Agent's reward
            episode_length += 1
            done = terminated or truncated

            if render:
                env.render()

        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)

    return {
        "mean_reward": float(np.mean(episode_rewards)),
        "std_reward": float(np.std(episode_rewards)),
        "mean_length": float(np.mean(episode_lengths)),
        "std_length": float(np.std(episode_lengths)),
        "episodes": [{"reward": r, "length": l} for r, l in zip(episode_rewards, episode_lengths)],
    }


def train_dqn(
    env_name: str,
    total_timesteps: int = 10000,
    learning_rate: float = 1e-3,
    buffer_size: int = 10000,
    learning_starts: int = 1000,
    batch_size: int = 32,
    gamma: float = 0.99,
    train_freq: int = 4,
    gradient_steps: int = 1,
    target_update_interval: int = 1000,
    exploration_fraction: float = 0.1,
    exploration_initial_eps: float = 1.0,
    exploration_final_eps: float = 0.05,
    seed: Optional[int] = None,
    verbose: int = 1,
):
    """
    Quick DQN training helper.

    Args:
        env_name: Environment to train on
        total_timesteps: Total training steps
        learning_rate: Learning rate
        buffer_size: Replay buffer size
        ... (other DQN hyperparameters)

    Returns:
        Trained DQN model

    Example:
        >>> from rl_arena.training import train_dqn
        >>>
        >>> # Train agent
        >>> model = train_dqn("pong", total_timesteps=50000)
        >>>
        >>> # Save model
        >>> model.save("my_agent.zip")
    """
    try:
        from stable_baselines3 import DQN
        from rl_arena.wrappers.gymnasium_wrapper import GymnasiumWrapper
    except ImportError:
        raise ImportError(
            "Stable-Baselines3 required for training. "
            "Install with: pip install stable-baselines3"
        )

    # Create environment
    env = GymnasiumWrapper(env_name, player_id=0)

    # Create model
    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=learning_rate,
        buffer_size=buffer_size,
        learning_starts=learning_starts,
        batch_size=batch_size,
        gamma=gamma,
        train_freq=train_freq,
        gradient_steps=gradient_steps,
        target_update_interval=target_update_interval,
        exploration_fraction=exploration_fraction,
        exploration_initial_eps=exploration_initial_eps,
        exploration_final_eps=exploration_final_eps,
        verbose=verbose,
        seed=seed,
    )

    # Train
    model.learn(total_timesteps=total_timesteps)

    return model
