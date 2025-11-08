# Pong Environment

A classic 2-player Pong game environment for competitive reinforcement learning.

## Overview

Pong is a simple yet challenging environment where two players control paddles to bounce a ball back and forth. The first player to reach the winning score wins the game.

## State Space

The observation is an 8-dimensional vector containing:
- `ball_x`: Ball X position (normalized to [0, 1])
- `ball_y`: Ball Y position (normalized to [0, 1])
- `ball_vx`: Ball X velocity
- `ball_vy`: Ball Y velocity
- `paddle1_y`: Player 1 paddle Y position (normalized to [0, 1])
- `paddle2_y`: Player 2 paddle Y position (normalized to [0, 1])
- `score1`: Player 1 score
- `score2`: Player 2 score

## Action Space

Each player has 3 discrete actions:
- `0`: Move UP
- `1`: STAY (no movement)
- `2`: Move DOWN

## Rewards

- `+1`: For scoring a point (ball passes opponent's paddle)
- `-1`: For conceding a point (ball passes your paddle)
- `0`: Otherwise

## Episode Termination

An episode ends when:
1. A player reaches the winning score (default: 11 points), OR
2. Maximum steps are reached (default: 1000 steps)

## Configuration

You can customize the environment by passing a configuration dictionary:

```python
import rl_arena

env = rl_arena.make("pong", configuration={
    "winning_score": 5,      # First to 5 wins
    "max_steps": 2000,       # Longer episodes
    "ball_speed": 0.03,      # Faster ball
    "paddle_height": 0.15,   # Smaller paddles
})
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `width` | float | 1.0 | Field width (normalized) |
| `height` | float | 1.0 | Field height (normalized) |
| `paddle_height` | float | 0.2 | Paddle height |
| `paddle_speed` | float | 0.05 | Paddle movement speed per step |
| `ball_speed` | float | 0.02 | Initial ball speed |
| `ball_radius` | float | 0.02 | Ball radius |
| `winning_score` | int | 11 | Score needed to win |
| `max_steps` | int | 1000 | Maximum steps per episode |

## Example Usage

```python
import rl_arena

# Create environment
env = rl_arena.make("pong")

# Reset environment
observations, info = env.reset(seed=42)

# Run one episode
done = False
while not done:
    # Both players take random actions
    actions = [env.action_space.sample(), env.action_space.sample()]
    
    observations, rewards, terminated, truncated, info = env.step(actions)
    done = terminated or truncated
    
    # Render the game
    env.render()
    
    if done:
        print(f"Game Over! Final scores: {info['scores']}")

env.close()
```

## Visualization & Recording

### Real-time Visualization

```python
import rl_arena

env = rl_arena.make("pong")
observations, info = env.reset()

for _ in range(100):
    actions = [env.action_space.sample(), env.action_space.sample()]
    observations, rewards, terminated, truncated, info = env.step(actions)
    
    # Display in Matplotlib window
    env.render(mode='human')
    
    if terminated or truncated:
        break

env.close()
```

### Render Modes

Pong supports multiple rendering modes:

- **`human`**: Real-time Matplotlib window with dark theme
- **`rgb_array`**: Returns (600, 800, 3) NumPy array
- **`ansi`**: ASCII art for terminal (40x20 grid)
- **`ipython`**: Inline display in Jupyter notebooks
- **`html`**: Interactive HTML5 replay (requires state recording)

### Recording Matches

```python
from rl_arena.core.recorder import MatchRecorder

env = rl_arena.make("pong")
recorder = MatchRecorder(metadata={'player1': 'AgentA', 'player2': 'AgentB'})
recorder.start_recording()

observations, info = env.reset()
for _ in range(1000):
    actions = [agent1.act(observations[0]), agent2.act(observations[1])]
    observations, rewards, terminated, truncated, info = env.step(actions)
    
    # Record frame
    state = env._get_render_state()
    recorder.record_frame(state, actions, rewards, info)
    
    if terminated or truncated:
        break

recorder.stop_recording()
recorder.save('match.json')
print(f'Recorded {len(recorder)} frames')
```

### Generate HTML Replay

```python
from rl_arena.utils.replay import load_replay, replay_to_html

replay = load_replay('match.json')
replay_to_html(replay, 'Pong', 'replay.html')
# Open replay.html in your browser!
```

See [VISUALIZATION.md](../../../docs/VISUALIZATION.md) for complete documentation.

## Strategy Tips

For AI agents competing in Pong:

1. **Track the ball**: The ball position and velocity are key to predicting where it will go
2. **Position proactively**: Move your paddle to where the ball will be, not where it is
3. **Stay centered**: When the ball is far away, return to center position
4. **Bounce angles**: The ball's bounce angle changes slightly on each paddle hit, adding unpredictability

## Performance Benchmarks

| Agent Type | Win Rate | Avg. Score Diff |
|------------|----------|-----------------|
| Random vs Random | 50% | 0.0 |
| Rule-based vs Random | 95% | +8.5 |
| DQN vs Random | 98% | +9.2 |

## Contributing

To improve this environment, please consider:
- Adding more realistic physics
- Implementing spin mechanics
- Adding power-ups or variations
- Improving rendering performance
- Adding sound effects

See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for guidelines.
