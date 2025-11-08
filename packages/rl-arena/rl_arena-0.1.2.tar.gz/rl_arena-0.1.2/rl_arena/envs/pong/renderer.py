"""Rendering functionality for the Pong environment."""

from typing import Dict, Any, List
import numpy as np
from rl_arena.core.renderer import Renderer


class PongRenderer(Renderer):
    """Matplotlib and HTML5-based renderer for Pong environment."""

    def __init__(self, width: int = 800, height: int = 600):
        super().__init__(width, height)
        self.bg_color = "#1a1a2e"
        self.paddle1_color = "#00ff88"
        self.paddle2_color = "#ff0066"
        self.ball_color = "#ffffff"
        self.line_color = "#444466"
        self.paddle_width = 10
        self.ball_radius = 8

    def render_frame(self, state: Dict[str, Any]) -> np.ndarray:
        """Render a single frame using matplotlib."""
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        fig = plt.figure(figsize=(self.width / 100, self.height / 100), dpi=100)
        ax = fig.add_subplot(111)
        fig.patch.set_facecolor(self.bg_color)
        ax.set_facecolor(self.bg_color)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")

        # Draw center line
        for y in np.arange(0.05, 1.0, 0.05):
            ax.plot([0.5, 0.5], [y, y + 0.02], color=self.line_color, linewidth=2)

        # Extract state
        ball = state.get("ball", {"x": 0.5, "y": 0.5})
        paddle1 = state.get("paddle1", {"y": 0.5})
        paddle2 = state.get("paddle2", {"y": 0.5})
        paddle_height = state.get("paddle_height", 0.2)
        scores = state.get("score", [0, 0])

        # Draw paddles
        paddle_w = self.paddle_width / self.width
        ball_r = self.ball_radius / self.width

        ax.add_patch(
            patches.Rectangle(
                (0.05 - paddle_w / 2, paddle1["y"] - paddle_height / 2),
                paddle_w,
                paddle_height,
                facecolor=self.paddle1_color,
            )
        )
        ax.add_patch(
            patches.Rectangle(
                (0.95 - paddle_w / 2, paddle2["y"] - paddle_height / 2),
                paddle_w,
                paddle_height,
                facecolor=self.paddle2_color,
            )
        )

        # Draw ball
        ax.add_patch(patches.Circle((ball["x"], ball["y"]), ball_r, facecolor=self.ball_color))

        # Draw scores
        ax.text(
            0.35,
            0.95,
            f"{scores[0]}",
            fontsize=32,
            color="white",
            ha="center",
            va="top",
            weight="bold",
        )
        ax.text(
            0.65,
            0.95,
            f"{scores[1]}",
            fontsize=32,
            color="white",
            ha="center",
            va="top",
            weight="bold",
        )

        plt.tight_layout(pad=0)
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        frame = np.asarray(canvas.buffer_rgba())[:, :, :3]
        plt.close(fig)
        return frame

    def render_html(self, history: List[Dict[str, Any]]) -> str:
        """Generate HTML5 animation from match history."""
        from rl_arena.utils.html_template import generate_pong_html

        return generate_pong_html(history, self.width, self.height)

    def render_ansi(self, state: Dict[str, Any]) -> str:
        """Render ASCII art representation for terminal display."""
        # Extract state information
        ball = state.get("ball", {"x": 0.5, "y": 0.5})
        paddle1 = state.get("paddle1", {"y": 0.5})
        paddle2 = state.get("paddle2", {"y": 0.5})
        paddle_height = state.get("paddle_height", 0.2)
        scores = state.get("score", [0, 0])

        ball_pos = (ball["x"], ball["y"])
        paddle1_y = paddle1["y"]
        paddle2_y = paddle2["y"]
        score1, score2 = scores[0], scores[1]

        width, height = 40, 20
        grid = [[" " for _ in range(width)] for _ in range(height)]

        # Center line
        for y in range(height):
            grid[y][width // 2] = "|"

        # Paddle 1
        p1_start = int((1 - paddle1_y - paddle_height / 2) * height)
        p1_end = int((1 - paddle1_y + paddle_height / 2) * height)
        for y in range(max(0, p1_start), min(height, p1_end)):
            grid[y][1] = "█"

        # Paddle 2
        p2_start = int((1 - paddle2_y - paddle_height / 2) * height)
        p2_end = int((1 - paddle2_y + paddle_height / 2) * height)
        for y in range(max(0, p2_start), min(height, p2_end)):
            grid[y][width - 2] = "█"

        # Ball
        ball_x = int(ball_pos[0] * width)
        ball_y = int((1 - ball_pos[1]) * height)
        if 0 <= ball_x < width and 0 <= ball_y < height:
            grid[ball_y][ball_x] = "●"

        # Build result
        result = f"  {score1}  |  {score2}  \n" + "=" * width + "\n"
        for row in grid:
            result += "".join(row) + "\n"
        result += "=" * width
        return result
        ball_x = int(ball_pos[0] * width)
        ball_y = int((1 - ball_pos[1]) * height)
        if 0 <= ball_x < width and 0 <= ball_y < height:
            grid[ball_y][ball_x] = ""

        # Build result
        result = f"  {score1}  |  {score2}  \n" + "=" * width + "\n"
        for row in grid:
            result += "".join(row) + "\n"
        result += "=" * width
        return result
