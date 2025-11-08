"""Match recording functionality for RL Arena."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class MatchRecorder:
    """
    Records match gameplay for replay and analysis.

    This class captures frame-by-frame state information during a match,
    along with metadata, and can save/load recordings in JSON format.

    Example:
        >>> recorder = MatchRecorder(metadata={'env': 'Pong-v1'})
        >>> recorder.start_recording()
        >>> for step in range(100):
        ...     state = env.step(actions)
        ...     recorder.record_frame(state, actions, rewards)
        >>> recorder.stop_recording()
        >>> recorder.save('match.json')
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize the match recorder.

        Args:
            metadata: Optional metadata about the match (env name, players, etc.)
        """
        self.metadata = metadata or {}
        self.frames: List[Dict[str, Any]] = []
        self.is_recording = False
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def start_recording(self) -> None:
        """Start recording a match."""
        self.is_recording = True
        self.frames = []
        self.start_time = datetime.now()
        self.end_time = None

    def stop_recording(self) -> None:
        """Stop recording the current match."""
        self.is_recording = False
        self.end_time = datetime.now()

    def record_frame(
        self,
        state: Dict[str, Any],
        actions: Optional[List[Any]] = None,
        rewards: Optional[List[float]] = None,
        info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a single frame of the match.

        Args:
            state: Current state dictionary
            actions: Actions taken by players (optional)
            rewards: Rewards received by players (optional)
            info: Additional information (optional)
        """
        if not self.is_recording:
            return

        frame = {
            "step": len(self.frames),
            "state": state,
        }

        if actions is not None:
            frame["actions"] = actions
        if rewards is not None:
            frame["rewards"] = rewards
        if info is not None:
            frame["info"] = info

        self.frames.append(frame)

    def get_recording(self) -> Dict[str, Any]:
        """
        Get the complete recording data.

        Returns:
            Dictionary containing metadata and all recorded frames
        """
        duration = None
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()

        return {
            "metadata": self.metadata,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": duration,
            "num_frames": len(self.frames),
            "frames": self.frames,
        }

    def save(self, filepath: str) -> None:
        """
        Save the recording to a JSON file.

        Args:
            filepath: Path where the recording will be saved

        Raises:
            ValueError: If no frames have been recorded
        """
        if not self.frames:
            raise ValueError("No frames recorded. Cannot save empty recording.")

        recording = self.get_recording()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(recording, f, indent=2, default=str)

    @classmethod
    def load(cls, filepath: str) -> "MatchRecorder":
        """
        Load a recording from a JSON file.

        Args:
            filepath: Path to the recording file

        Returns:
            MatchRecorder instance with loaded data

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        recorder = cls(metadata=data.get("metadata", {}))
        recorder.frames = data.get("frames", [])

        # Restore timestamps
        if data.get("start_time"):
            recorder.start_time = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            recorder.end_time = datetime.fromisoformat(data["end_time"])

        return recorder

    def clear(self) -> None:
        """Clear all recorded frames."""
        self.frames = []
        self.start_time = None
        self.end_time = None
        self.is_recording = False

    def get_frame(self, index: int) -> Dict[str, Any]:
        """
        Get a specific frame by index.

        Args:
            index: Frame index

        Returns:
            Frame data dictionary

        Raises:
            IndexError: If index is out of range
        """
        return self.frames[index]

    def get_state_history(self) -> List[Dict[str, Any]]:
        """
        Extract just the state information from all frames.

        Returns:
            List of state dictionaries
        """
        return [frame["state"] for frame in self.frames]

    def __len__(self) -> int:
        """Return the number of recorded frames."""
        return len(self.frames)

    def __repr__(self) -> str:
        """String representation of the recorder."""
        status = "recording" if self.is_recording else "stopped"
        return f"MatchRecorder(frames={len(self.frames)}, status={status})"
