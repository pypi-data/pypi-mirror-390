"""Replay utilities for loading and converting match recordings."""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path


def save_replay(recording: Dict[str, Any], filepath: str, pretty: bool = True) -> None:
    """
    Save a replay recording to a JSON file.

    Args:
        recording: Recording dictionary (from MatchRecorder.get_recording())
        filepath: Path where the replay will be saved
        pretty: If True, use indentation for readability

    Example:
        >>> recorder = MatchRecorder()
        >>> # ... record match ...
        >>> save_replay(recorder.get_recording(), 'match.json')
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    indent = 2 if pretty else None
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(recording, f, indent=indent, default=str)


def load_replay(filepath: str) -> Dict[str, Any]:
    """
    Load a replay recording from a JSON file.

    Args:
        filepath: Path to the replay file

    Returns:
        Recording dictionary

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON

    Example:
        >>> replay = load_replay('match.json')
        >>> print(f"Match duration: {replay['duration']} seconds")
        >>> print(f"Number of frames: {replay['num_frames']}")
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
        return data


def replay_to_html(
    recording: Dict[str, Any], env_name: str, output_path: Optional[str] = None
) -> str:
    """
    Convert a replay recording to an HTML5 animation.

    Args:
        recording: Recording dictionary
        env_name: Name of the environment (e.g., 'Pong')
        output_path: Optional path to save the HTML file

    Returns:
        HTML string

    Example:
        >>> replay = load_replay('match.json')
        >>> html = replay_to_html(replay, 'Pong', 'match.html')
    """
    from rl_arena.utils.html_template import generate_html

    # Extract state history from frames
    state_history = [frame["state"] for frame in recording.get("frames", [])]

    # Generate HTML
    html = generate_html(
        state_history=state_history,
        env_name=env_name,
        metadata=recording.get("metadata", {}),
        duration=recording.get("duration"),
    )

    # Save if output path is provided
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    return html


def get_replay_stats(recording: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract statistics from a replay recording.

    Args:
        recording: Recording dictionary

    Returns:
        Dictionary containing replay statistics

    Example:
        >>> replay = load_replay('match.json')
        >>> stats = get_replay_stats(replay)
        >>> print(f"Average reward: {stats['avg_reward']}")
    """
    frames = recording.get("frames", [])

    if not frames:
        return {
            "num_frames": 0,
            "duration": recording.get("duration"),
            "metadata": recording.get("metadata", {}),
        }

    # Calculate statistics
    total_rewards = [0.0] * len(frames[0].get("rewards", [0]))
    for frame in frames:
        rewards = frame.get("rewards", [])
        for i, r in enumerate(rewards):
            if i < len(total_rewards):
                total_rewards[i] += r

    avg_rewards = [r / len(frames) for r in total_rewards]

    return {
        "num_frames": len(frames),
        "duration": recording.get("duration"),
        "total_rewards": total_rewards,
        "avg_rewards": avg_rewards,
        "metadata": recording.get("metadata", {}),
        "start_time": recording.get("start_time"),
        "end_time": recording.get("end_time"),
    }


def merge_replays(replays: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple replay recordings into a single recording.

    Args:
        replays: List of recording dictionaries

    Returns:
        Merged recording dictionary

    Example:
        >>> replay1 = load_replay('match1.json')
        >>> replay2 = load_replay('match2.json')
        >>> merged = merge_replays([replay1, replay2])
        >>> save_replay(merged, 'combined.json')
    """
    if not replays:
        return {"metadata": {}, "frames": []}

    merged_frames = []
    step_offset = 0

    for replay in replays:
        frames = replay.get("frames", [])
        for frame in frames:
            new_frame = frame.copy()
            new_frame["step"] = step_offset + frame.get("step", 0)
            merged_frames.append(new_frame)
        step_offset += len(frames)

    # Merge metadata
    merged_metadata = replays[0].get("metadata", {}).copy()
    merged_metadata["num_matches"] = len(replays)

    return {
        "metadata": merged_metadata,
        "start_time": replays[0].get("start_time"),
        "end_time": replays[-1].get("end_time"),
        "duration": sum(r.get("duration", 0) for r in replays if r.get("duration")),
        "num_frames": len(merged_frames),
        "frames": merged_frames,
    }


def extract_frames(
    recording: Dict[str, Any], start: int = 0, end: Optional[int] = None, step: int = 1
) -> Dict[str, Any]:
    """
    Extract a subset of frames from a recording.

    Args:
        recording: Recording dictionary
        start: Starting frame index
        end: Ending frame index (exclusive), None for all remaining frames
        step: Step size for frame extraction

    Returns:
        New recording with extracted frames

    Example:
        >>> replay = load_replay('match.json')
        >>> # Extract every 10th frame
        >>> sparse = extract_frames(replay, step=10)
        >>> # Extract first 100 frames
        >>> beginning = extract_frames(replay, end=100)
    """
    frames = recording.get("frames", [])
    extracted_frames = frames[start:end:step]

    # Renumber steps
    for i, frame in enumerate(extracted_frames):
        frame["step"] = i

    return {
        "metadata": recording.get("metadata", {}).copy(),
        "start_time": recording.get("start_time"),
        "end_time": recording.get("end_time"),
        "duration": recording.get("duration"),
        "num_frames": len(extracted_frames),
        "frames": extracted_frames,
    }
