import streamlit as st
import time
import random
import json
import os
from datetime import datetime
from dataclasses import dataclass
import streamlit.components.v1 as components

# Configure Streamlit
st.set_page_config(
    page_title="🐍 Snake Game",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
MOVE_DISTANCE = 20
BOUNDARY = 180  # Reduced for better display
BOARD_SIZE = 400

@dataclass
class Position:
    x: float
    y: float

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
        tail_position = self.segments[-1]
        self.add_segment(tail_position)
    
    def move(self):
        for i in range(len(self.segments) - 1, 0, -1):
            self.segments[i].x = self.segments[i-1].x
            self.segments[i].y = self.segments[i-1].y
        
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

class StreamlitFood:
    def __init__(self):
        self.position = Position(0, 0)
        self.refresh()
    
    def refresh(self):
        self.position.x = random.randint(-160, 160)
        self.position.y = random.randint(-160, 160)
        self.position.x = round(self.position.x / 20) * 20
        self.position.y = round(self.position.y / 20) * 20

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

def create_game_display(snake, food, score, high_score, game_over):
    """Create a visual representation using HTML/CSS"""
    
    scale = 1
    canvas_width = BOARD_SIZE
    canvas_height = BOARD_SIZE
    
    html_content = f"""
    <div style="
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 0 30px rgba(0,255,0,0.3);
        margin: 20px;
    ">
        <h2 style="color: {'#ff4444' if game_over else '#44ff44'}; margin: 10px; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            {'💀 GAME OVER' if game_over else '🐍 SNAKE GAME'}
        </h2>
        <div style="color: #ffffff; margin: 10px; font-size: 18px; text-align: center;">
            Score: <span style="color: #44ff44; font-weight: bold;">{score}</span> | 
            High Score: <span style="color: #ffd700; font-weight: bold;">{high_score}</span>
        </div>
        <div style="
            position: relative; 
            width: {canvas_width}px; 
            height: {canvas_height}px; 
            background: linear-gradient(45deg, #000000, #1a1a1a);
            border: 4px solid #44ff44; 
            border-radius: 10px;
            box-shadow: inset 0 0 20px rgba(0,255,0,0.2);
            margin: 10px;
        ">
    """
    
    # Add snake segments
    for i, segment in enumerate(snake.segments):
        x = segment.x + canvas_width // 2
        y = canvas_height // 2 - segment.y
        
        is_head = i == 0
        size = 18 if is_head else 16
        
        if is_head:
            color = "#44ff44"
            shadow = "0 0 10px #44ff44"
        else:
            color = "#88ff88"
            shadow = "0 0 5px #88ff88"
        
        html_content += f"""
            <div style="
                position: absolute; 
                left: {x-size//2}px; 
                top: {y-size//2}px; 
                width: {size}px; 
                height: {size}px; 
                background-color: {color}; 
                border-radius: 50%; 
                box-shadow: {shadow};
                border: 2px solid #226622;
            "></div>
        """
    
    # Add food
    fx = food.position.x + canvas_width // 2
    fy = canvas_height // 2 - food.position.y
    
    html_content += f"""
        <div style="
            position: absolute; 
            left: {fx-10}px; 
            top: {fy-10}px; 
            width: 20px; 
            height: 20px; 
            background: radial-gradient(circle, #ff4444, #cc0000);
            border-radius: 50%; 
            box-shadow: 0 0 15px #ff4444;
            border: 2px solid #990000;
        "></div>
    """
    
    html_content += """
        </div>
        <div style="color: #cccccc; margin: 10px; font-size: 14px; text-align: center;">
            Use the arrow buttons below to control the snake
        </div>
    </div>
    """
    
    return html_content

def init_game():
    st.session_state.snake = StreamlitSnake()
    st.session_state.food = StreamlitFood()
    st.session_state.scoreboard = StreamlitScoreboard()
    st.session_state.game_running = True
    st.session_state.last_update = time.time()
    st.session_state.speed = 0.4
    st.session_state.move_count = 0

if 'snake' not in st.session_state:
    init_game()

def check_collisions():
    snake = st.session_state.snake
    food = st.session_state.food
    scoreboard = st.session_state.scoreboard
    
    # Check food collision
    if snake.distance(food.position) < 20:
        food.refresh()
        snake.extend_snake()
        scoreboard.increase_score()
        return "food"
    
    # Check wall collision
    head = snake.head
    if (head.x > BOUNDARY or head.x < -BOUNDARY or 
        head.y > BOUNDARY or head.y < -BOUNDARY):
        scoreboard.game_over()
        st.session_state.game_running = False
        return "wall"
    
    # Check self collision
    for segment in snake.segments[1:]:
        if abs(snake.head.x - segment.x) < 15 and abs(snake.head.y - segment.y) < 15:
            scoreboard.game_over()
            st.session_state.game_running = False
            return "self"
    
    return None

def main():
    st.title("🐍 Enhanced Snake Game")
    st.markdown("*Use the control buttons to play the classic Snake game!*")
    
    # Sidebar
    with st.sidebar:
        st.header("🎮 Game Stats")
        st.metric("Current Score", st.session_state.scoreboard.score)
        st.metric("High Score", st.session_state.scoreboard.high_score)
        
        total_games = st.session_state.scoreboard.get_total_games()
        if total_games > 0:
            st.metric("Total Games", total_games)
        
        st.header("🎛️ Controls")
        
        game_speed = st.slider("Speed", 0.1, 0.8, st.session_state.speed, 0.1)
        st.session_state.speed = game_speed
        
        if st.button("🔄 New Game", type="primary", use_container_width=True):
            init_game()
            st.rerun()
        
        if st.button("🗑️ Reset High Score", use_container_width=True):
            try:
                if os.path.exists("high_score.json"):
                    os.remove("high_score.json")
                st.session_state.scoreboard.high_score = 0
                st.success("High score reset!")
                time.sleep(1)
                st.rerun()
            except:
                pass
        
        st.header("📖 How to Play")
        st.markdown("""
        - Use arrow buttons to control snake
        - Eat red food to grow and score
        - Avoid walls and your own tail
        - Try to beat your high score!
        """)
    
    # Main game area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Game display
        game_html = create_game_display(
            st.session_state.snake,
            st.session_state.food,
            st.session_state.scoreboard.score,
            st.session_state.scoreboard.high_score,
            st.session_state.scoreboard.game_over_flag
        )
        
        st.markdown(game_html, unsafe_allow_html=True)
        
        # Control buttons in a nice layout
        st.markdown("### 🎮 Game Controls")
        
        # Create a 3x3 grid for controls
        button_cols = st.columns([1, 1, 1])
        
        with button_cols[1]:  # Top button
            if st.button("⬆️", key="up_btn", help="Move Up", use_container_width=True):
                if st.session_state.game_running:
                    st.session_state.snake.up()
                    st.rerun()
        
        control_row = st.columns([1, 1, 1])
        with control_row[0]:  # Left button
            if st.button("⬅️", key="left_btn", help="Move Left", use_container_width=True):
                if st.session_state.game_running:
                    st.session_state.snake.left()
                    st.rerun()
        
        with control_row[1]:  # Spacer or additional control
            st.markdown("<div style='text-align: center; color: #666;'>🎮</div>", unsafe_allow_html=True)
        
        with control_row[2]:  # Right button
            if st.button("➡️", key="right_btn", help="Move Right", use_container_width=True):
                if st.session_state.game_running:
                    st.session_state.snake.right()
                    st.rerun()
        
        down_cols = st.columns([1, 1, 1])
        with down_cols[1]:  # Bottom button
            if st.button("⬇️", key="down_btn", help="Move Down", use_container_width=True):
                if st.session_state.game_running:
                    st.session_state.snake.down()
                    st.rerun()
    
    # Auto-move logic
    if st.session_state.game_running:
        current_time = time.time()
        if current_time - st.session_state.last_update > st.session_state.speed:
            st.session_state.snake.move()
            collision = check_collisions()
            st.session_state.last_update = current_time
            st.session_state.move_count += 1
            
            if collision == "food":
                st.balloons()
            
            # Auto-refresh for continuous gameplay
            time.sleep(0.1)
            st.rerun()
        else:
            # Small delay and refresh to keep game running
            time.sleep(0.05)
            st.rerun()
    
    # Game over screen
    if not st.session_state.game_running:
        st.error("💀 Game Over!")
        
        final_cols = st.columns(3)
        with final_cols[0]:
            st.metric("Final Score", st.session_state.scoreboard.score)
        with final_cols[1]:
            st.metric("High Score", st.session_state.scoreboard.high_score)
        with final_cols[2]:
            if (st.session_state.scoreboard.score == st.session_state.scoreboard.high_score 
                and st.session_state.scoreboard.score > 0):
                st.success("🏆 NEW HIGH SCORE!")
            else:
                st.info("🎯 Try Again!")
        
        if st.button("🎮 Play Again", type="primary", use_container_width=True):
            init_game()
            st.rerun()
    
    # Game status
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        if st.session_state.game_running:
            st.success("🟢 Game Running")
        else:
            st.error("🔴 Game Over")
    
    with status_col2:
        st.info(f"Direction: {st.session_state.snake.direction}")
    
    # Debug info (collapsible)
    with st.expander("🔧 Debug Info"):
        st.write(f"Snake Position: ({st.session_state.snake.head.x}, {st.session_state.snake.head.y})")
        st.write(f"Food Position: ({st.session_state.food.position.x}, {st.session_state.food.position.y})")
        st.write(f"Snake Length: {len(st.session_state.snake.segments)}")
        st.write(f"Moves: {st.session_state.move_count}")

if __name__ == "__main__":
    main()
