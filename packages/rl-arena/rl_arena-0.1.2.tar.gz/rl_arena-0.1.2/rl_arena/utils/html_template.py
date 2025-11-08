"""HTML5 template generation for match replays."""

from typing import Dict, Any, List, Optional


def _parse_pong_observation(obs_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse Pong observation dictionary into structured state.
    
    Args:
        obs_dict: Dictionary mapping agent IDs to observation arrays
                  Format: {agent_id: [ball_x, ball_y, ball_vx, ball_vy, paddle1_y, paddle2_y, score1, score2]}
    
    Returns:
        Structured state dictionary with ball, paddles, and scores
    """
    # Get the first observation (both agents see the same state in Pong)
    obs = list(obs_dict.values())[0]
    
    # Parse observation array: [ball_x, ball_y, ball_vx, ball_vy, paddle1_y, paddle2_y, score1, score2]
    return {
        "ball": {
            "x": float(obs[0]),
            "y": float(obs[1]),
        },
        "paddle1": {
            "y": float(obs[4]),
        },
        "paddle2": {
            "y": float(obs[5]),
        },
        "paddle_height": 0.2,  # Default paddle height
        "score": [int(obs[6]), int(obs[7])],
    }


def generate_pong_html(history: List[Dict[str, Any]], width: int = 800, height: int = 600) -> str:
    """
    Generate HTML5 animation for Pong environment replay.

    Args:
        history: List of state dictionaries from match recording
        width: Canvas width in pixels
        height: Canvas height in pixels

    Returns:
        Complete HTML string with embedded JavaScript animation
    """
    import json

    # Convert observation dictionaries to structured states
    structured_history = [_parse_pong_observation(state) for state in history]
    
    # Serialize state history
    history_json = json.dumps(structured_history)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pong Replay</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #ffffff;
        }}
        h1 {{
            color: #00ff88;
            margin-bottom: 10px;
        }}
        .container {{
            background: #1a1a2e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
        }}
        canvas {{
            border: 2px solid #444466;
            display: block;
            background: #1a1a2e;
        }}
        .controls {{
            margin-top: 20px;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        button {{
            background: #00ff88;
            border: none;
            color: #0a0a0a;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
            font-weight: bold;
            transition: background 0.3s;
        }}
        button:hover {{
            background: #00cc6a;
        }}
        button:disabled {{
            background: #444466;
            cursor: not-allowed;
        }}
        .slider {{
            flex: 1;
            min-width: 200px;
        }}
        .info {{
            margin-top: 10px;
            color: #aaaaaa;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>Pong Match Replay</h1>
    <div class="container">
        <canvas id="gameCanvas" width="{width}" height="{height}"></canvas>
        <div class="controls">
            <button id="playBtn">Play</button>
            <button id="pauseBtn">Pause</button>
            <button id="restartBtn">Restart</button>
            <input type="range" id="frameSlider" class="slider" min="0" max="100" value="0">
            <span id="frameInfo">Frame: 0 / 0</span>
        </div>
        <div class="info">
            <span id="speedInfo">Speed: 1x</span>
            <button onclick="changeSpeed(0.5)">0.5x</button>
            <button onclick="changeSpeed(1)">1x</button>
            <button onclick="changeSpeed(2)">2x</button>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const history = {history_json};
        
        let currentFrame = 0;
        let isPlaying = false;
        let animationSpeed = 1;
        let animationInterval = null;
        
        const playBtn = document.getElementById('playBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const restartBtn = document.getElementById('restartBtn');
        const frameSlider = document.getElementById('frameSlider');
        const frameInfo = document.getElementById('frameInfo');
        const speedInfo = document.getElementById('speedInfo');
        
        // Initialize
        frameSlider.max = history.length - 1;
        updateFrameInfo();
        
        function drawFrame(state) {{
            // Clear canvas
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw center line
            ctx.strokeStyle = '#444466';
            ctx.lineWidth = 2;
            ctx.setLineDash([10, 10]);
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2, 0);
            ctx.lineTo(canvas.width / 2, canvas.height);
            ctx.stroke();
            ctx.setLineDash([]);
            
            // Extract state
            const ball = state.ball || {{x: 0.5, y: 0.5}};
            const paddle1 = state.paddle1 || {{y: 0.5}};
            const paddle2 = state.paddle2 || {{y: 0.5}};
            const paddleHeight = state.paddle_height || 0.2;
            const scores = state.score || [0, 0];
            
            // Draw paddles
            const paddleWidth = 10;
            const paddlePixelHeight = paddleHeight * canvas.height;
            
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(
                0.05 * canvas.width - paddleWidth / 2,
                paddle1.y * canvas.height - paddlePixelHeight / 2,
                paddleWidth,
                paddlePixelHeight
            );
            
            ctx.fillStyle = '#ff0066';
            ctx.fillRect(
                0.95 * canvas.width - paddleWidth / 2,
                paddle2.y * canvas.height - paddlePixelHeight / 2,
                paddleWidth,
                paddlePixelHeight
            );
            
            // Draw ball
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(
                ball.x * canvas.width,
                ball.y * canvas.height,
                8,
                0,
                Math.PI * 2
            );
            ctx.fill();
            
            // Draw scores
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 48px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(scores[0], canvas.width * 0.35, 60);
            ctx.fillText(scores[1], canvas.width * 0.65, 60);
        }}
        
        function updateFrameInfo() {{
            frameInfo.textContent = 'Frame: ' + currentFrame + ' / ' + (history.length - 1);
            frameSlider.value = currentFrame;
        }}
        
        function renderCurrentFrame() {{
            if (currentFrame < history.length) {{
                drawFrame(history[currentFrame]);
                updateFrameInfo();
            }}
        }}
        
        function play() {{
            if (isPlaying) return;
            isPlaying = true;
            playBtn.disabled = true;
            pauseBtn.disabled = false;
            
            const frameDelay = 1000 / (60 * animationSpeed);
            animationInterval = setInterval(() => {{
                currentFrame++;
                if (currentFrame >= history.length) {{
                    pause();
                    currentFrame = history.length - 1;
                }}
                renderCurrentFrame();
            }}, frameDelay);
        }}
        
        function pause() {{
            isPlaying = false;
            playBtn.disabled = false;
            pauseBtn.disabled = true;
            if (animationInterval) {{
                clearInterval(animationInterval);
                animationInterval = null;
            }}
        }}
        
        function restart() {{
            pause();
            currentFrame = 0;
            renderCurrentFrame();
        }}
        
        function changeSpeed(speed) {{
            animationSpeed = speed;
            speedInfo.textContent = 'Speed: ' + speed + 'x';
            if (isPlaying) {{
                pause();
                play();
            }}
        }}
        
        // Event listeners
        playBtn.addEventListener('click', play);
        pauseBtn.addEventListener('click', pause);
        restartBtn.addEventListener('click', restart);
        
        frameSlider.addEventListener('input', (e) => {{
            currentFrame = parseInt(e.target.value);
            renderCurrentFrame();
        }});
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{
                e.preventDefault();
                if (isPlaying) pause();
                else play();
            }} else if (e.code === 'ArrowLeft') {{
                currentFrame = Math.max(0, currentFrame - 1);
                renderCurrentFrame();
            }} else if (e.code === 'ArrowRight') {{
                currentFrame = Math.min(history.length - 1, currentFrame + 1);
                renderCurrentFrame();
            }}
        }});
        
        // Initial render
        renderCurrentFrame();
    </script>
</body>
</html>"""

    return html


def generate_html(
    state_history: List[Dict[str, Any]],
    env_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    duration: Optional[float] = None,
    width: int = 800,
    height: int = 600,
) -> str:
    """
    Generate HTML5 animation for any environment replay.

    This is a dispatcher function that calls the appropriate environment-specific
    HTML generator based on the environment name.

    Args:
        state_history: List of state dictionaries
        env_name: Name of the environment
        metadata: Optional metadata dictionary
        duration: Optional match duration in seconds
        width: Canvas width
        height: Canvas height

    Returns:
        Complete HTML string

    Raises:
        ValueError: If environment is not supported
    """
    env_name_lower = env_name.lower()

    if "pong" in env_name_lower:
        return generate_pong_html(state_history, width, height)
    else:
        raise ValueError(f"HTML generation not implemented for environment: {env_name}")


def get_supported_environments() -> List[str]:
    """
    Get list of environments that support HTML replay generation.

    Returns:
        List of supported environment names
    """
    return ["Pong"]
