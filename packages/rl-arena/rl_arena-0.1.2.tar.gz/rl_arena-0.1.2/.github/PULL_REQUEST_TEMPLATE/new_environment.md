---
name: New Environment
about: Submit a new environment to RL Arena
title: '[ENV] Add [Environment Name] environment'
labels: 'new-environment'
assignees: ''
---

## Environment Information

**Environment Name:** <!-- e.g., "connect4", "chess", "poker" -->

**Game Type:** <!-- e.g., "Board game", "Card game", "Physics-based" -->

**Number of Players:** <!-- e.g., 2, 3, 4 -->

**Brief Description:**
<!-- Provide a 2-3 sentence description of the game -->

## Implementation Checklist

Please ensure you have completed the following:

### Code
- [ ] Environment class inherits from `Environment` base class
- [ ] All abstract methods are implemented (`reset`, `step`, `render`, `get_observation`)
- [ ] Environment is registered with `@register_environment` decorator
- [ ] Proper type hints on all methods
- [ ] Comprehensive docstrings (Google style)
- [ ] Configuration file (`config.yaml`) if needed
- [ ] Renderer implementation (at least ANSI mode)

### Testing
- [ ] Tests added in `tests/envs/test_[your_env].py`
- [ ] Test coverage > 80%
- [ ] All tests pass locally (`pytest tests/envs/test_[your_env].py`)
- [ ] Environment is deterministic with same seed

### Documentation
- [ ] Environment-specific README.md
- [ ] State space documented
- [ ] Action space documented
- [ ] Reward structure explained
- [ ] Configuration options documented
- [ ] Usage examples provided

### Examples
- [ ] Example script added in `examples/`
- [ ] Example demonstrates basic usage

### Code Quality
- [ ] Code formatted with `black`
- [ ] No linting errors (`flake8`)
- [ ] Type checking passes (`mypy`)
- [ ] Main README.md updated with new environment

## Additional Information

**Related Issues:** <!-- Link to any related issues -->

**Inspiration/Reference:** <!-- Any papers, implementations, or games this is based on -->

**Special Dependencies:** <!-- Any additional dependencies required? -->

## Testing Instructions

Describe how reviewers can test your environment:

```python
import rl_arena

env = rl_arena.make("your-env-name")
# ... testing code ...
```

## Screenshots/Demo

<!-- If applicable, add screenshots or demo output -->

## Questions for Reviewers

<!-- Any specific questions or areas you'd like feedback on? -->
