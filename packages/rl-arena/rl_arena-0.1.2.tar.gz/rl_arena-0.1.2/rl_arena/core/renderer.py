"""Abstract renderer base class for RL Arena environments."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes


class Renderer(ABC):
    """
    Abstract base class for environment renderers.

    Renderers handle visualization of environment states in various formats:
    - Real-time display (matplotlib, pygame, etc.)
    - Frame capture (RGB arrays)
    - HTML5 animation generation
    - Jupyter notebook inline display
    """

    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize the renderer.

        Args:
            width: Rendering width in pixels
            height: Rendering height in pixels
        """
        self.width = width
        self.height = height
        self._fig: Optional["Figure"] = None
        self._ax: Optional["Axes"] = None
        self._is_setup = False

    @abstractmethod
    def render_frame(self, state: Dict[str, Any]) -> np.ndarray:
        """
        Render a single frame from the given state.

        Args:
            state: Dictionary containing the environment state

        Returns:
            RGB array of shape (height, width, 3) with values in [0, 255]

        Example:
            >>> state = {'ball': {'x': 400, 'y': 300}, 'paddle1': {'y': 250}}
            >>> frame = renderer.render_frame(state)
            >>> frame.shape
            (600, 800, 3)
        """
        pass

    @abstractmethod
    def render_html(self, history: List[Dict[str, Any]]) -> str:
        """
        Generate an HTML5 animation from the game history.

        Args:
            history: List of state dictionaries representing the full game

        Returns:
            Self-contained HTML string with embedded JavaScript animation

        Example:
            >>> history = [state1, state2, state3, ...]
            >>> html = renderer.render_html(history)
            >>> with open('replay.html', 'w') as f:
            ...     f.write(html)
        """
        pass

    def setup_matplotlib(self) -> None:
        """
        Initialize matplotlib figure and axes for real-time rendering.

        This method should be called before using matplotlib-based rendering.
        Override this method to customize the matplotlib setup.

        Example:
            >>> renderer.setup_matplotlib()
            >>> # Now can use matplotlib rendering
        """
        try:
            import matplotlib.pyplot as plt

            if self._fig is None:
                self._fig, self._ax = plt.subplots(figsize=(self.width / 100, self.height / 100))
                self._ax.set_xlim(0, self.width)
                self._ax.set_ylim(0, self.height)
                self._ax.set_aspect("equal")
                self._ax.axis("off")
                plt.tight_layout()
                self._is_setup = True
        except ImportError:
            raise ImportError(
                "Matplotlib is required for rendering. " "Install it with: pip install matplotlib"
            )

    def render_human(self, state: Dict[str, Any]) -> None:
        """
        Render for human viewing (real-time display).

        Args:
            state: Dictionary containing the environment state

        Example:
            >>> renderer.render_human(state)
            >>> # Displays frame in matplotlib window
        """
        try:
            import matplotlib.pyplot as plt

            # Setup matplotlib if needed
            if not self._is_setup:
                self.setup_matplotlib()

            # Render frame
            frame = self.render_frame(state)

            # Display frame
            if self._ax is not None:
                self._ax.clear()
                self._ax.imshow(frame)
                self._ax.axis("off")
                plt.pause(0.001)

        except ImportError:
            raise ImportError(
                "Matplotlib is required for human rendering. "
                "Install it with: pip install matplotlib"
            )

    def close(self) -> None:
        """
        Clean up renderer resources.

        Override this method to add custom cleanup logic.
        Call this method when done with the renderer.

        Example:
            >>> renderer.close()
        """
        if self._fig is not None:
            try:
                import matplotlib.pyplot as plt

                plt.close(self._fig)
            except ImportError:
                pass
            self._fig = None
            self._ax = None
            self._is_setup = False

    def render_ipython(self, state: Dict[str, Any]) -> Any:
        """
        Render for Jupyter notebook inline display.

        Args:
            state: Dictionary containing the environment state

        Returns:
            IPython display object

        Example:
            >>> display_obj = renderer.render_ipython(state)
            >>> # Automatically displays in Jupyter
        """
        try:
            from IPython.display import Image, display
            import io
            import matplotlib.pyplot as plt

            # Render frame
            frame = self.render_frame(state)

            # Convert to image
            fig, ax = plt.subplots(figsize=(self.width / 100, self.height / 100))
            ax.imshow(frame)
            ax.axis("off")
            plt.tight_layout()

            # Save to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
            buf.seek(0)
            plt.close(fig)

            # Display
            return display(Image(buf.read()))

        except ImportError:
            raise ImportError(
                "IPython is required for notebook rendering. "
                "Install it with: pip install ipython"
            )

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
