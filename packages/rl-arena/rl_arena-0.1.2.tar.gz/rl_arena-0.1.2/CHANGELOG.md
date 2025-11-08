# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Visualization System**: Complete rendering framework with multiple modes
  - human mode: Real-time Matplotlib visualization
  - gb_array mode: NumPy array output for video recording
  - nsi mode: ASCII art terminal display
  - ipython mode: Jupyter notebook inline display
  - html mode: Interactive HTML5 replay generation
  
- **Renderer Architecture**: Abstract Renderer base class
  - PongRenderer: Matplotlib-based renderer with dark theme
  - Colored paddles (left: #00ff88, right: #ff0066)
  - Score display and center line visualization
  
- **Match Recording System**: MatchRecorder class for gameplay capture
  - Frame-by-frame state recording
  - JSON export/import with metadata support
  - Timestamp tracking for replay analysis
  
- **Replay Utilities** (l_arena.utils.replay):
  - save_replay() / load_replay(): JSON persistence
  - eplay_to_html(): Convert recordings to interactive HTML
  - get_replay_stats(): Extract match statistics
  - merge_replays(): Combine multiple recordings
  - extract_frames(): Filter and downsample recordings
  
- **HTML5 Replay Player**: Interactive browser-based playback
  - Play/Pause controls
  - Speed adjustment (0.5x, 1x, 2x)
  - Frame scrubbing slider
  - Keyboard shortcuts (Space, Arrow keys)
  
- **State Recording in Environments**:
  - enable_state_recording(): Toggle automatic state capture
  - get_state_history(): Retrieve recorded states
  - clear_state_history(): Reset recording buffer
  
- **Environment Updates**:
  - Abstract methods: _create_renderer(), _get_render_state()
  - Pong environment now fully supports all render modes
  
- **Example Scripts**:
  - examples/visualize_game.py: Real-time game visualization
  - examples/record_match.py: Match recording demonstration
  - examples/replay_to_html.py: HTML replay generation
  
- **Test Coverage**:
  - 	ests/test_renderer.py: PongRenderer test suite
  - 	ests/test_recorder.py: MatchRecorder test suite
  - 	ests/test_replay.py: Replay utilities test suite
  - All tests passing (13/13)
  
- **Documentation**:
  - docs/VISUALIZATION.md: Comprehensive visualization guide
  - Updated README with visualization examples
  - API documentation for new classes

### Changed
- **Environment Base Class**: ender() method now concrete with mode dispatch
- **Pong Environment**: Integrated with new rendering system
- **Dependencies**: Added matplotlib>=3.5.0 to requirements.txt

### Fixed
- Import issues in l_arena.utils.__init__.py
- Renderer cleanup in environment close() method

## [0.1.0] - 2024-11-05

### Added
- Initial release
- Pong environment implementation
- Base Environment and Agent classes
- Random agent example
- Test suite with pytest
- CI/CD with GitHub Actions
- Type hints and documentation
- Seeding mechanism for reproducibility

[Unreleased]: https://github.com/rl-arena/rl-arena-env/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/rl-arena/rl-arena-env/releases/tag/v0.1.0
