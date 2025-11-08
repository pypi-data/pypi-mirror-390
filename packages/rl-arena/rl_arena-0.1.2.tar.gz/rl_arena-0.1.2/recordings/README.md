# Recordings Directory

This directory contains recorded game matches in JSON format and their HTML visualizations.

## File Types

- `*.json` - Match replay data (game states, actions, rewards)
- `*.html` - HTML5 animations generated from replay data

## Usage

### Record a Match

```python
from rl_arena import make
from rl_arena.core.recorder import MatchRecorder

env = make("pong")
recorder = MatchRecorder(metadata={"description": "My match"})

recorder.start_recording()
# ... play game ...
recorder.stop_recording()
recorder.save("recordings/my_match.json")
```

### Generate HTML Visualization

See `examples/replay_to_html.py` for converting JSON replays to HTML animations.

## Note

Files in this directory are ignored by git (except this README).
