"""Create a new RL-Arena environment from template.

This script helps you quickly scaffold a new environment with all necessary files.
"""

import os
import sys
import argparse
from pathlib import Path


def to_snake_case(name: str) -> str:
    """Convert name to snake_case."""
    import re

    # Replace spaces and hyphens with underscores
    name = name.replace(" ", "_").replace("-", "_")
    # Insert underscores before uppercase letters
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    # Convert to lowercase and remove duplicate underscores
    name = name.lower()
    name = re.sub("_+", "_", name)
    return name


def to_pascal_case(name: str) -> str:
    """Convert name to PascalCase."""
    parts = name.replace("_", " ").replace("-", " ").split()
    return "".join(word.capitalize() for word in parts)


def create_environment(game_name: str, output_dir: Path, force: bool = False) -> None:
    """
    Create a new environment from template.

    Args:
        game_name: Human-readable game name (e.g., "Tic Tac Toe")
        output_dir: Directory where environment will be created
        force: Overwrite existing directory
    """
    # Convert names
    game_name_lower = to_snake_case(game_name)
    class_name = to_pascal_case(game_name)

    print(f"Creating environment: {game_name}")
    print(f"  Class name: {class_name}Environment")
    print(f"  Package name: {game_name_lower}")
    print()

    # Create output directory
    env_dir = output_dir / game_name_lower
    if env_dir.exists() and not force:
        print(f"Error: Directory {env_dir} already exists.")
        print("Use --force to overwrite.")
        sys.exit(1)

    env_dir.mkdir(parents=True, exist_ok=True)

    # Find template directory
    template_dir = Path(__file__).parent.parent / "templates" / "environment"
    if not template_dir.exists():
        print(f"Error: Template directory not found at {template_dir}")
        sys.exit(1)

    # Process templates
    replacements = {
        "{{game_name}}": game_name,
        "{{game_name_lower}}": game_name_lower,
        "{{class_name}}": class_name,
    }

    # File mappings (template -> output)
    file_mappings = {
        "__init__.py.template": "__init__.py",
        "environment.py.template": "environment.py",
        "renderer.py.template": "renderer.py",
        "test_environment.py.template": f"test_{game_name_lower}.py",
        "README.md.template": "README.md",
    }

    # Create files from templates
    for template_file, output_file in file_mappings.items():
        template_path = template_dir / template_file
        output_path = env_dir / output_file

        if not template_path.exists():
            print(f"Warning: Template {template_file} not found, skipping.")
            continue

        # Read template
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace placeholders
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        # Write output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ Created {output_file}")

    print()
    print("=" * 60)
    print("✅ Environment scaffolding complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print(f"1. Edit {env_dir / 'environment.py'}")
    print("   - Define action_space and observation_space")
    print("   - Implement game logic in step()")
    print("   - Implement _get_observations()")
    print()
    print(f"2. Edit {env_dir / 'renderer.py'}")
    print("   - Implement render_frame() for visualization")
    print("   - Implement render_ansi() for text display")
    print()
    print(f"3. Edit {env_dir / ('test_' + game_name_lower + '.py')}")
    print("   - Add game-specific tests")
    print()
    print(f"4. Update {env_dir / 'README.md'}")
    print("   - Document game rules and mechanics")
    print()
    print("5. Register environment in rl_arena/envs/__init__.py")
    print(f"   - Add: from rl_arena.envs.{game_name_lower} import {class_name}Environment")
    print()
    print("6. Test your environment:")
    print(f'   python -c "from rl_arena.tools import validate_environment;')
    print(f"   from rl_arena.envs.{game_name_lower} import {class_name}Environment;")
    print(f'   validate_environment({class_name}Environment)"')
    print()
    print("7. Run tests:")
    print(f"   pytest tests/envs/test_{game_name_lower}.py")
    print()
    print("Happy coding! 🎮")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a new RL-Arena environment from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create Tic-Tac-Toe environment
  python scripts/create_environment.py "Tic Tac Toe"
  
  # Create Connect Four environment in custom directory
  python scripts/create_environment.py "Connect Four" --output ./my_envs
  
  # Overwrite existing environment
  python scripts/create_environment.py "Snake" --force
        """,
    )

    parser.add_argument("game_name", help="Human-readable name of the game")

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("rl_arena/envs"),
        help="Output directory (default: rl_arena/envs)",
    )

    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing directory")

    args = parser.parse_args()

    # Create environment
    create_environment(args.game_name, args.output, args.force)


if __name__ == "__main__":
    main()
