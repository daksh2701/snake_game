import streamlit as st
import time
import random
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List
from streamlit.components.v1 import html

# Configure Streamlit
st.set_page_config(
    page_title="🐍 Snake Game",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants (adapted from your original game)
MOVE_DISTANCE = 20
GRID_SIZE = 20
BOARD_WIDTH = 800
BOARD_HEIGHT = 800
BOUNDARY = 380

@dataclass
class Position:
    x: float
    y: float

# Adapted Snake class from your snake.py
class StreamlitSnake:
    def __init__(self):
        self.segments = []
        self.create_snake()
        self.head = self.segments[0]
        self.direction = "RIGHT"
    
    def create_snake(self):
        starting_positions = [Position(0, 0), Position(-20, 0), Position(-40, 0)]
        self.segments = []
        for position in starting_positions:
            self.add_segment(position)
    
    def add_segment(self, position):
        self.segments.append(Position(position.x, position.y))
    
    def extend_snake(self):
        # Add segment at the tail position
        tail_position = self.segments[-1]
        self.add_segment(tail_position)
    
    def move(self):
        # Move body segments
        for i in range(len(self.segments) - 1, 0, -1):
            self.segments[i].x = self.segments[i-1].x
            self.segments[i].y = self.segments[i-1].y
        
        # Move head based on direction
        if self.direction == "UP":
            self.head.y += MOVE_DISTANCE
        elif self.direction == "DOWN":
            self.head.y -= MOVE_DISTANCE
        elif self.direction == "LEFT":
            self.head.x -= MOVE_DISTANCE
        elif self.direction == "RIGHT":
            self.head.x += MOVE_DISTANCE
    
    def up(self):
        if self.direction != "DOWN":
            self.direction = "UP"
    
    def down(self):
        if self.direction != "UP":
            self.direction = "DOWN"
    
    def left(self):
        if self.direction != "RIGHT":
            self.direction = "LEFT"
    
    def right(self):
        if self.direction != "LEFT":
            self.direction = "RIGHT"
    
    def distance(self, other_pos):
        return ((self.head.x - other_pos.x)**2 + (self.head.y - other_pos.y)**2)**0.5

# Adapted Food class from your food.py
class StreamlitFood:
    def __init__(self):
        self.position = Position(0, 0)
        self.refresh()
    
    def refresh(self):
        self.position.x = random.randint(-280, 280)
        self.position.y = random.randint(-280, 280)
        # Round to nearest 20 to align with grid
        self.position.x = round(self.position.x / 20) * 20
        self.position.y = round(self.position.y / 20) * 20

# Enhanced Scoreboard class with high score tracking
class StreamlitScoreboard:
    def __init__(self):
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over_flag = False
    
    def increase_score(self):
        self.score += 1
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
    
    def game_over(self):
        self.game_over_flag = True
        self.save_high_score()
    
    def reset(self):
        self.score = 0
        self.game_over_flag = False
    
    def load_high_score(self):
        try:
            if os.path.exists("high_score.json"):
                with open("high_score.json", "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            data = {
                "high_score": self.high_score,
                "last_updated": datetime.now().isoformat(),
                "total_games": self.get_total_games() + 1
            }
            with open("high_score.json", "w") as f:
                json.dump(data, f)
        except:
            pass
    
    def get_total_games(self):
        try:
            if os.path.exists("high_score.json"):
                with open("high_score.json", "r") as f:
                    data = json.load(f)
                    return data.get("total_games", 0)
        except:
            pass
        return 0

# Removed text-based grid display - keeping only HTML display

# HTML Canvas-based game visualization with keyboard controls
def create_html_game_display(snake, food, score, high_score, game_over):
    """Create an HTML canvas representation of the game with keyboard controls"""
    
    canvas_width = 400
    canvas_height = 400
    scale = canvas_width / 800  # Scale down from 800x800 to 400x400
    
    # JavaScript for keyboard controls
    keyboard_script = """
    <script>
        document.addEventListener('keydown', function(event) {
            const key = event.key;
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'w', 'a', 's', 'd', 'W', 'A', 'S', 'D'].includes(key)) {
                event.preventDefault();
                
                // Send key press to Streamlit
                if (key === 'ArrowUp' || key === 'w' || key === 'W') {
                    window.parent.postMessage({type: 'keypress', key: 'up'}, '*');
                } else if (key === 'ArrowDown' || key === 's' || key === 'S') {
                    window.parent.postMessage({type: 'keypress', key: 'down'}, '*');
                } else if (key === 'ArrowLeft' || key === 'a' || key === 'A') {
                    window.parent.postMessage({type: 'keypress', key: 'left'}, '*');
                } else if (key === 'ArrowRight' || key === 'd' || key === 'D') {
                    window.parent.postMessage({type: 'keypress', key: 'right'}, '*');
                }
            }
        });
        
        // Make sure the game area is focusable
        document.getElementById('game-area').focus();
    </script>
    """
    
    html_content = f"""
    <div id="game-area" tabindex="0" style="display: flex; flex-direction: column; align-items: center; background-color: #1e1e1e; padding: 20px; border-radius: 10px; outline: none;">
        <h2 style="color: {'red' if game_over else 'white'}; margin: 10px;">
            {'🎮 GAME OVER' if game_over else '🐍 SNAKE GAME'}
        </h2>
        <div style="color: white; margin: 10px;">
            Score: {score} | High Score: <span style="color: gold;">{high_score}</span>
        </div>
        <div style="color: #ccc; margin: 5px; font-size: 12px;">
            Use ↑↓←→ arrow keys or WASD to control the snake
        </div>
        <div style="position: relative; width: {canvas_width}px; height: {canvas_height}px; background-color: black; border: 3px solid lime; border-radius: 5px;">
            <!-- Snake segments -->
    """
    
    # Add snake segments
    for i, segment in enumerate(snake.segments):
        x = (segment.x + 400) * scale
        y = (400 - segment.y) * scale  # Flip Y coordinate
        
        color = "lime" if i == 0 else "lightgreen"
        size = 18 if i == 0 else 16
        
        html_content += f"""
            <div style="position: absolute; left: {x-size//2}px; top: {y-size//2}px; 
                        width: {size}px; height: {size}px; background-color: {color}; 
                        border-radius: 50%; border: 1px solid darkgreen;"></div>
        """
    
    # Add food
    fx = (food.position.x + 400) * scale
    fy = (400 - food.position.y) * scale
    
    html_content += f"""
            <!-- Food -->
            <div style="position: absolute; left: {fx-8}px; top: {fy-8}px; 
                        width: 16px; height: 16px; background-color: red; 
                        border-radius: 50%; border: 1px solid darkred;"></div>
        </div>
    </div>
    {keyboard_script}
    """
    
    return html_content

# Initialize session state
def init_game():
    st.session_state.snake = StreamlitSnake()
    st.session_state.food = StreamlitFood()
    st.session_state.scoreboard = StreamlitScoreboard()
    st.session_state.game_running = True
    st.session_state.last_update = time.time()
    st.session_state.speed = 0.3
    st.session_state.last_key_press = None

if 'snake' not in st.session_state:
    init_game()

def check_collisions():
    """Check all collisions based on your original main.py logic"""
    snake = st.session_state.snake
    food = st.session_state.food
    scoreboard = st.session_state.scoreboard
    
    # Check food collision (distance < 20 from original)
    if snake.distance(food.position) < 20:
        food.refresh()
        snake.extend_snake()
        scoreboard.increase_score()
        return "food"
    
    # Check wall collision (adapted from your boundary check)
    head = snake.head
    if (head.x > BOUNDARY or head.x < -BOUNDARY or 
        head.y > BOUNDARY or head.y < -BOUNDARY):
        scoreboard.game_over()
        st.session_state.game_running = False
        return "wall"
    
    # Check self collision
    for segment in snake.segments[1:]:  # Skip head
        if abs(snake.head.x - segment.x) < 15 and abs(snake.head.y - segment.y) < 15:
            scoreboard.game_over()
            st.session_state.game_running = False
            return "self"
    
    return None

def main():
    st.title("🐍 Snake Game")
    st.markdown("*Recreated from your Python files with high score tracking!*")
    
    # Sidebar with game stats and controls
    with st.sidebar:
        st.header("🎮 Game Stats")
        st.metric("Current Score", st.session_state.scoreboard.score)
        st.metric("High Score", st.session_state.scoreboard.high_score, 
                 delta=st.session_state.scoreboard.score - st.session_state.scoreboard.high_score if st.session_state.scoreboard.score > 0 else None)
        
        total_games = st.session_state.scoreboard.get_total_games()
        if total_games > 0:
            st.metric("Total Games Played", total_games)
        
        st.header("🎛️ Game Controls")
        
        game_speed = st.slider("Game Speed (seconds)", 0.1, 0.8, st.session_state.speed, 0.1)
        st.session_state.speed = game_speed
        
        if st.button("🔄 New Game", type="primary"):
            init_game()
            st.rerun()
        
        if st.button("🗑️ Reset High Score"):
            if os.path.exists("high_score.json"):
                os.remove("high_score.json")
            st.session_state.scoreboard.high_score = 0
            st.success("High score reset!")
            time.sleep(1)
            st.rerun()
        
        st.header("📖 Instructions")
        st.markdown("""
        **How to Play:**
        - Use the arrow buttons to control the snake
        - Eat red food to grow and score points
        - Avoid walls and your own tail
        - Try to beat your high score!
        
        **Controls:**
        - ⬆️⬇️⬅️➡️ Arrow keys or WASD to move snake
        - Click arrow buttons as backup
        - Adjust speed with slider
        """)
    
    # Main game area
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Keyboard input detection using query params
        query_params = st.experimental_get_query_params()
        if 'key' in query_params:
            key = query_params['key'][0]
            if key != st.session_state.get('last_key_press'):
                if key == 'up':
                    st.session_state.snake.up()
                elif key == 'down':
                    st.session_state.snake.down()
                elif key == 'left':
                    st.session_state.snake.left()
                elif key == 'right':
                    st.session_state.snake.right()
                st.session_state.last_key_press = key
        
        # Control buttons (backup method)
        st.markdown("### 🎮 Game Controls")
        control_col1, control_col2, control_col3, control_col4, control_col5 = st.columns(5)
        
        with control_col2:
            if st.button("⬆️", key="up", help="Move Up", use_container_width=True):
                st.session_state.snake.up()
        
        with control_col1:
            if st.button("⬅️", key="left", help="Move Left", use_container_width=True):
                st.session_state.snake.left()
        
        with control_col3:
            if st.button("⬇️", key="down", help="Move Down", use_container_width=True):
                st.session_state.snake.down()
        
        with control_col4:
            if st.button("➡️", key="right", help="Move Right", use_container_width=True):
                st.session_state.snake.right()
        
        # Game display with keyboard controls
        st.markdown("### 🎯 Game Area")
        st.markdown("*Click on the game area and use arrow keys or WASD to control the snake*")
        
        # Add keyboard event listener
        keyboard_html = """
        <script>
        let lastKey = '';
        document.addEventListener('keydown', function(event) {
            const key = event.key;
            let direction = '';
            
            if (key === 'ArrowUp' || key === 'w' || key === 'W') {
                direction = 'up';
                event.preventDefault();
            } else if (key === 'ArrowDown' || key === 's' || key === 'S') {
                direction = 'down';
                event.preventDefault();
            } else if (key === 'ArrowLeft' || key === 'a' || key === 'A') {
                direction = 'left';
                event.preventDefault();
            } else if (key === 'ArrowRight' || key === 'd' || key === 'D') {
                direction = 'right';
                event.preventDefault();
            }
            
            if (direction && direction !== lastKey) {
                lastKey = direction;
                // Use Streamlit's query params to communicate key press
                const url = new URL(window.location);
                url.searchParams.set('key', direction);
                url.searchParams.set('timestamp', Date.now());
                window.history.replaceState({}, '', url);
                window.location.reload();
            }
        });
        </script>
        <div style="padding: 10px; text-align: center; background: #f0f0f0; border-radius: 5px; margin: 10px 0;">
            Press arrow keys or WASD to control the snake
        </div>
        """
        
        html(keyboard_html, height=100)
        game_container = st.container()
        
        with game_container:
            # Game logic update
            if st.session_state.game_running:
                current_time = time.time()
                if current_time - st.session_state.last_update > st.session_state.speed:
                    st.session_state.snake.move()
                    collision = check_collisions()
                    st.session_state.last_update = current_time
                    
                    if collision == "food":
                        st.balloons()
            
            # Create and display game using HTML
            html_display = create_html_game_display(
                st.session_state.snake, 
                st.session_state.food,
                st.session_state.scoreboard.score,
                st.session_state.scoreboard.high_score,
                st.session_state.scoreboard.game_over_flag
            )
            st.markdown(html_display, unsafe_allow_html=True)
            
            # Game status
            if st.session_state.game_running:
                st.success("🎮 Game Running - Use arrow buttons to control!")
                # Auto-refresh for continuous gameplay
                time.sleep(0.1)
                st.rerun()
            else:
                st.error("💀 Game Over!")
                
                # Show final stats
                col_stats1, col_stats2, col_stats3 = st.columns(3)
                with col_stats1:
                    st.metric("Final Score", st.session_state.scoreboard.score)
                with col_stats2:
                    st.metric("High Score", st.session_state.scoreboard.high_score)
                with col_stats3:
                    if st.session_state.scoreboard.score == st.session_state.scoreboard.high_score and st.session_state.scoreboard.score > 0:
                        st.success("🏆 NEW HIGH SCORE!")
                    else:
                        st.info("Try again!")
                
                if st.button("🎯 Play Again", type="primary", key="play_again"):
                    init_game()
                    st.rerun()

    # Game info
    st.markdown("---")
    
    # Display current game state
    with st.expander("🔍 Game Debug Info"):
        st.write(f"Snake Head Position: ({st.session_state.snake.head.x}, {st.session_state.snake.head.y})")
        st.write(f"Snake Direction: {st.session_state.snake.direction}")
        st.write(f"Food Position: ({st.session_state.food.position.x}, {st.session_state.food.position.y})")
        st.write(f"Snake Length: {len(st.session_state.snake.segments)}")
        st.write(f"Game Running: {st.session_state.game_running}")
    
    st.info("💡 **Tip:** Use keyboard arrow keys (↑↓←→) or WASD keys to control your snake! The buttons below are backup controls.")

if __name__ == "__main__":
    main()
