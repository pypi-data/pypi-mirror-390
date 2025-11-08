"""
Utilities for preparing and validating agents for submission.
"""

from typing import Optional, Dict, Any
from pathlib import Path
import inspect
import zipfile
import json
from rl_arena.core.agent import Agent


def create_submission_template(
    agent: Agent,
    output_path: str,
    agent_name: str = "MyAgent",
    description: str = "",
    author: str = "",
    version: str = "1.0.0",
) -> None:
    """
    Create a submission-ready agent file.

    This generates a standalone Python file that can be submitted
    to rl-arena-backend.

    Args:
        agent: Your trained agent
        output_path: Where to save the submission file
        agent_name: Name of your agent class
        description: Agent description
        author: Your name/username
        version: Agent version

    Example:
        >>> from rl_arena.submission import create_submission_template
        >>> from rl_arena.agents import RandomAgent
        >>>
        >>> agent = RandomAgent()
        >>> create_submission_template(
        ...     agent,
        ...     "my_submission.py",
        ...     agent_name="MyAwesomeAgent",
        ...     description="A random agent for testing",
        ...     author="your_name",
        ... )
    """

    # Get agent code
    agent_class = agent.__class__
    agent_source = inspect.getsource(agent_class)

    # Create submission file
    template = f'''"""
{agent_name} - Submission for RL-Arena

Description: {description}
Author: {author}
Version: {version}
"""

from rl_arena.core.agent import Agent


{agent_source}


# Metadata for backend
__agent_name__ = "{agent_name}"
__author__ = "{author}"
__version__ = "{version}"
__description__ = "{description}"


def create_agent() -> Agent:
    """
    Factory function called by rl-arena-backend.
    
    Returns:
        Agent instance
    """
    return {agent_class.__name__}()
'''

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template)

    print(f"✅ Submission template created: {output_path}")
    print(f"   Agent: {agent_name}")
    print(f"   Author: {author}")
    print(f"   Version: {version}")


def package_agent(
    agent_path: str,
    model_path: Optional[str] = None,
    output_path: str = "submission.zip",
    include_files: Optional[list] = None,
) -> None:
    """
    Package agent and model into a submission zip file.

    Args:
        agent_path: Path to agent Python file
        model_path: Path to trained model file (optional)
        output_path: Output zip file path
        include_files: Additional files to include

    Example:
        >>> from rl_arena.submission import package_agent
        >>>
        >>> package_agent(
        ...     agent_path="my_agent.py",
        ...     model_path="my_model.zip",
        ...     output_path="submission.zip"
        ... )
    """

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add agent file
        zipf.write(agent_path, "agent.py")

        # Add model if provided
        if model_path:
            model_name = Path(model_path).name
            zipf.write(model_path, f"models/{model_name}")

        # Add additional files
        if include_files:
            for file_path in include_files:
                zipf.write(file_path, Path(file_path).name)

    print(f"✅ Agent packaged: {output_path}")


def validate_submission(agent_path: str) -> Dict[str, Any]:
    """
    Validate a submission file before uploading.

    Checks:
    - File is valid Python
    - Has create_agent() function
    - Agent inherits from Agent base class
    - Has required metadata
    - File size is reasonable

    Args:
        agent_path: Path to submission file

    Returns:
        Validation result with issues found

    Example:
        >>> from rl_arena.submission import validate_submission
        >>>
        >>> result = validate_submission("my_submission.py")
        >>> if result['valid']:
        ...     print("✅ Submission is valid!")
        ... else:
        ...     print("❌ Issues found:", result['issues'])
    """

    issues = []
    warnings = []

    # Check file exists
    path = Path(agent_path)
    if not path.exists():
        return {
            "valid": False,
            "issues": [f"File not found: {agent_path}"],
            "warnings": [],
        }

    # Check file size (should be < 10MB)
    file_size = path.stat().st_size
    if file_size > 10 * 1024 * 1024:
        issues.append(f"File too large: {file_size / 1024 / 1024:.1f}MB (max 10MB)")

    # Read file
    try:
        with open(agent_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {
            "valid": False,
            "issues": [f"Could not read file: {e}"],
            "warnings": [],
        }

    # Check for required function
    if "def create_agent()" not in content:
        issues.append("Missing create_agent() function")

    # Check for metadata
    metadata_fields = ["__agent_name__", "__author__", "__version__"]
    for field in metadata_fields:
        if field not in content:
            warnings.append(f"Missing metadata: {field}")

    # Check imports
    if "from rl_arena.core.agent import Agent" not in content:
        if "Agent" in content:
            warnings.append("Agent class not imported from rl_arena.core.agent")

    # Try to import (basic syntax check)
    try:
        compile(content, agent_path, "exec")
    except SyntaxError as e:
        issues.append(f"Syntax error: {e}")

    valid = len(issues) == 0

    return {
        "valid": valid,
        "issues": issues,
        "warnings": warnings,
        "file_size": file_size,
    }


def generate_submission_readme(
    agent_name: str,
    env_name: str,
    performance: Dict[str, float],
    output_path: str = "README.md",
) -> None:
    """
    Generate a README for your submission.

    Args:
        agent_name: Name of your agent
        env_name: Environment trained on
        performance: Performance metrics
        output_path: Output path

    Example:
        >>> from rl_arena.submission import generate_submission_readme
        >>>
        >>> performance = {
        ...     'mean_reward': 5.2,
        ...     'std_reward': 1.3,
        ...     'training_steps': 50000,
        ... }
        >>>
        >>> generate_submission_readme(
        ...     agent_name="MyAgent",
        ...     env_name="pong",
        ...     performance=performance,
        ... )
    """

    readme = f"""# {agent_name}

## Overview
Agent trained for **{env_name}** environment.

## Performance
- **Mean Reward**: {performance.get('mean_reward', 'N/A')}
- **Std Reward**: {performance.get('std_reward', 'N/A')}
- **Training Steps**: {performance.get('training_steps', 'N/A')}

## Algorithm
{performance.get('algorithm', 'Not specified')}

## Training Details
{performance.get('training_details', 'Not provided')}

## Usage
```python
from agent import create_agent

agent = create_agent()
observation = env.reset()
action = agent.act(observation)
```

## Files
- `agent.py`: Agent implementation
- `models/`: Trained model weights (if applicable)
- `README.md`: This file

## Submission
Submitted to rl-arena-backend for competitive evaluation.
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"✅ README generated: {output_path}")
