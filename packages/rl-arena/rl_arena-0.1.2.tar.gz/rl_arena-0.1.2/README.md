# RL Arena 🎮

A Python library for competitive reinforcement learning environments, similar to kaggle-environments but focused on multi-agent RL research and competitions.

[![Tests](https://github.com/rl-arena/rl-arena-env/workflows/Tests/badge.svg)](https://github.com/rl-arena/rl-arena-env/actions)
[![PyPI version](https://badge.fury.io/py/rl-arena.svg)](https://badge.fury.io/py/rl-arena)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🌟 Features

- **Easy-to-use API**: Familiar Gymnasium-style interface
- **Competitive Multi-Agent**: Built for head-to-head competition
- **Extensible**: Simple framework for adding new environments
- **Well-tested**: Comprehensive test suite with >80% coverage
- **Type-safe**: Full type hints for better development experience
- **Reproducible**: Deterministic environments with seed support
- **Visualization System**: Real-time rendering with Matplotlib
- **Replay Recording**: Save and replay matches in JSON format
- **HTML5 Replays**: Interactive browser-based match playback

## 📦 Installation

### From PyPI (recommended)

```bash
pip install rl-arena
```

### From Source

```bash
git clone https://github.com/rl-arena/rl-arena-env.git
cd rl-arena-env
pip install -e .
```

### For Development

```bash
git clone https://github.com/rl-arena/rl-arena-env.git
cd rl-arena-env
pip install -e ".[dev]"
```

## 🚀 Quick Start (30 seconds!)

RL-Arena makes it easy to: **Create environments → Train agents → Test → Submit**

```python
import rl_arena

# 1️⃣ Create environment
env = rl_arena.make("pong")

# 2️⃣ Train agent (DQN)
model = rl_arena.train_dqn("pong", total_timesteps=10000)

# 3️⃣ Test agent
agent = rl_arena.create_agent(model)
results = rl_arena.evaluate(agent, "pong", n_episodes=10)
print(f"Average reward: {results['mean_reward']:.2f}")

# 4️⃣ Create submission file
rl_arena.create_submission(
    agent,
    "my_submission.py",
    agent_name="MyAgent",
    author="your_name"
)
```

**That's it!** Submit `my_submission.py` to rl-arena-backend.

---

## 📖 Basic Usage

### Environment Creation

```python
import rl_arena

# Create environment
env = rl_arena.make("pong")

# Use built-in agents
agent1 = rl_arena.RandomAgent()
agent2 = rl_arena.RuleBasedAgent()

# Run a game
observations, info = env.reset(seed=42)
done = False

while not done:
    # Get actions from agents
    actions = [
        agent1.act(observations[0]),
        agent2.act(observations[1])
    ]
    
    # Step environment
    observations, rewards, terminated, truncated, info = env.step(actions)
    done = terminated or truncated
    
    # Render
    env.render()

print(f"Final scores: {info['scores']}")
env.close()
```

## 🎯 Available Environments

| Environment | Players | Description | Complexity |
|-------------|---------|-------------|------------|
| **pong** | 2 | Classic Pong game | ⭐ Easy |

**More environments coming soon!** Contributions welcome! 

## 🎮 Environment Details

### Pong

Classic 2-player Pong game with customizable physics.

```python
env = rl_arena.make("pong", configuration={
    "winning_score": 11,    # First to 11 wins
    "max_steps": 1000,      # Episode length limit
    "ball_speed": 0.02,     # Ball movement speed
    "paddle_height": 0.2,   # Paddle size
})
```

**State Space:** Ball position & velocity, paddle positions, scores  
**Action Space:** Discrete(3) - UP, STAY, DOWN  
**Rewards:** +1 for scoring, -1 for conceding

See [Pong documentation](rl_arena/envs/pong/README.md) for more details.

## 📚 Documentation

- **[Complete Library API Guide](docs/LIBRARY_API.md)**: Full API reference with examples
- **[Environment Creation Tutorial](docs/ENVIRONMENT_CREATION_TUTORIAL.md)**: Create custom environments
- **[Interactive Mode Guide](docs/INTERACTIVE_MODE.md)**: Play against AI interactively

## 🔨 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rl_arena tests/

# Run specific test file
pytest tests/test_core.py -v
```

### Code Quality

```bash
# Format code
black rl_arena/ tests/ examples/

# Type checking
mypy rl_arena/

# Linting
flake8 rl_arena/ tests/ examples/
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Add New Environments**: See [Environment Creation Tutorial](docs/ENVIRONMENT_CREATION_TUTORIAL.md)
2. **Fix Bugs**: Check [open issues](https://github.com/rl-arena/rl-arena-env/issues)
3. **Improve Documentation**: Help make RL Arena more accessible
4. **Add Examples**: Share your agent implementations

### Quick Contribution Workflow

```bash
# Fork and clone
git clone https://github.com/YOUR-USERNAME/rl-arena-env.git
cd rl-arena-env

# Create branch
git checkout -b feature/my-new-environment

# Make changes, add tests, update docs

# Run tests and linting
pytest
black rl_arena/ tests/
flake8 rl_arena/

# Commit and push
git commit -m "feat: Add new environment"
git push origin feature/my-new-environment

# Open Pull Request on GitHub
```

## 📖 Examples

### Train and Evaluate Agent

```python
import rl_arena

# Train DQN agent
model = rl_arena.train_dqn("pong", total_timesteps=50000)

# Evaluate performance
agent = rl_arena.create_agent(model)
results = rl_arena.evaluate(agent, "pong", n_episodes=20)
print(f"Win rate: {results['mean_reward']:.2%}")
```

### Interactive Play (Human vs AI)

```python
# Requires pygame: pip install pygame
player = rl_arena.play("pong", fps=60)
player.play(
    player1_agent=None,  # Human player
    player2_agent=agent,  # Your trained AI
)
```

### Record and Replay Matches

```python
from rl_arena.utils.replay import save_replay, replay_to_html

# Record match
recorder = rl_arena.MatchRecorder()
env = rl_arena.make("pong")
env.set_recorder(recorder)

# ... play game ...

# Save replay
recording = recorder.get_recording()
save_replay(recording, "match.json")

# Generate HTML replay
html = replay_to_html(recording, "pong", "replay.html")
```

### Create Submission File

```python
# Create submission for competition
rl_arena.create_submission(
    agent=agent,
    output_path="submission.py",
    agent_name="MyPongMaster",
    author="your_name",
    description="DQN agent trained for 50K steps"
)

# Validate submission
result = rl_arena.validate("submission.py")
if result['valid']:
    print("✅ Ready to submit!")
```

## 🎓 Use Cases

- **Research**: Study multi-agent RL algorithms
- **Education**: Learn RL in competitive settings
- **Competitions**: Host RL tournaments and competitions
- **Benchmarking**: Compare agent performance across environments
- **Fun**: Build and battle AI agents!

## 🏗️ Project Structure

```
rl-arena-env/
├── rl_arena/              # Main package
│   ├── core/              # Base classes and interfaces
│   ├── envs/              # Environment implementations
│   │   ├── pong/          # Pong environment
│   │   └── __template__/  # Template for new environments
│   └── utils/             # Utilities (replay, logging, etc.)
├── tests/                 # Test suite
├── examples/              # Example scripts
├── docs/                  # Documentation
└── .github/               # CI/CD workflows
```



## 🙏 Acknowledgments

- Inspired by [kaggle-environments](https://github.com/Kaggle/kaggle-environments)
- Built on [Gymnasium](https://gymnasium.farama.org/)
- Thanks to all [contributors](https://github.com/rl-arena/rl-arena-env/graphs/contributors)

## 📬 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/rl-arena/rl-arena-env/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rl-arena/rl-arena-env/discussions)
- **Email**: kwaklloyd@gmail.com

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## ⭐ Star History

If you find RL Arena useful, please consider starring the repository!

---

**Made with ❤️ by the RL Arena community**