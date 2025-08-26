import streamlit as st
import time
import random
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np

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

# Game visualization
def create_game_plot(snake, food, score, high_score, game_over):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-400, 400)
    ax.set_ylim(-400, 400)
    ax.set_aspect('equal')
    ax.set_facecolor('black')
    
    # Draw boundary
    boundary = patches.Rectangle((-380, -380), 760, 760, 
                                linewidth=3, edgecolor='white', 
                                facecolor='none')
    ax.add_patch(boundary)
    
    # Draw snake
    for i, segment in enumerate(snake.segments):
        color = 'lime' if i == 0 else 'lightgreen'
        size = 18 if i == 0 else 16
        circle = patches.Circle((segment.x, segment.y), size/2, 
                               facecolor=color, edgecolor='darkgreen')
        ax.add_patch(circle)
        
        # Add eyes to head
        if i == 0:
            eye1_x = segment.x - 5 if snake.direction in ["LEFT", "RIGHT"] else segment.x - 3
            eye1_y = segment.y + 3 if snake.direction in ["UP", "DOWN"] else segment.y + 5
            eye2_x = segment.x + 5 if snake.direction in ["LEFT", "RIGHT"] else segment.x + 3
            eye2_y = segment.y + 3 if snake.direction in ["UP", "DOWN"] else segment.y - 5
            
            ax.plot(eye1_x, eye1_y, 'ko', markersize=3)
            ax.plot(eye2_x, eye2_y, 'ko', markersize=3)
    
    # Draw food
    food_circle = patches.Circle((food.position.x, food.position.y), 10, 
                                facecolor='red', edgecolor='darkred')
    ax.add_patch(food_circle)
    
    # Add title and score
    title_color = 'red' if game_over else 'white'
    title_text = 'GAME OVER' if game_over else 'SNAKE GAME'
    ax.text(0, 350, title_text, color=title_color, fontsize=24, 
            fontweight='bold', ha='center')
    ax.text(0, 320, f'Score: {score}', color='white', fontsize=16, ha='center')
    ax.text(0, 290, f'High Score: {high_score}', color='gold', fontsize=14, ha='center')
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    
    return fig

# Initialize session state
def init_game():
    st.session_state.snake = StreamlitSnake()
    st.session_state.food = StreamlitFood()
    st.session_state.scoreboard = StreamlitScoreboard()
    st.session_state.game_running = True
    st.session_state.last_update = time.time()
    st.session_state.speed = 0.2

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
    
    # Check self collision (distance < 15 from original)
    for segment in snake.segments[1:]:  # Skip head
        if snake.head.x == segment.x and snake.head.y == segment.y:
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
        game_speed = st.slider("Game Speed", 0.05, 0.5, st.session_state.speed, 0.05)
        st.session_state.speed = game_speed
        
        if st.button("🔄 New Game", type="primary"):
            init_game()
            st.rerun()
        
        if st.button("🗑️ Reset High Score"):
            if os.path.exists("high_score.json"):
                os.remove("high_score.json")
            st.session_state.scoreboard.high_score = 0
            st.success("High score reset!")
            st.rerun()
        
        st.header("📖 Instructions")
        st.markdown("""
        **How to Play:**
        - Use the arrow buttons to control the snake
        - Eat red food to grow and score points
        - Avoid walls and your own tail
        - Try to beat your high score!
        
        **Controls:**
        - ⬆️⬇️⬅️➡️ Move snake
        - Adjust speed with slider
        - Reset game anytime
        """)
    
    # Main game area
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        # Control buttons
        control_col1, control_col2, control_col3, control_col4, control_col5 = st.columns(5)
        
        with control_col2:
            if st.button("⬆️", key="up", help="Move Up"):
                st.session_state.snake.up()
        
        with control_col1:
            if st.button("⬅️", key="left", help="Move Left"):
                st.session_state.snake.left()
        
        with control_col3:
            if st.button("⬇️", key="down", help="Move Down"):
                st.session_state.snake.down()
        
        with control_col4:
            if st.button("➡️", key="right", help="Move Right"):
                st.session_state.snake.right()
        
        # Game display
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
            
            # Create and display game
            fig = create_game_plot(
                st.session_state.snake, 
                st.session_state.food,
                st.session_state.scoreboard.score,
                st.session_state.scoreboard.high_score,
                st.session_state.scoreboard.game_over_flag
            )
            st.pyplot(fig, clear_figure=True)
            
            # Game status
            if st.session_state.game_running:
                st.success("🎮 Game Running - Use arrow buttons to control!")
                # Auto-refresh for continuous gameplay
                time.sleep(0.05)
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
                    if st.session_state.scoreboard.score == st.session_state.scoreboard.high_score:
                        st.success("🏆 NEW HIGH SCORE!")
                    else:
                        st.info("Try again!")
                
                if st.button("🎯 Play Again", type="primary", key="play_again"):
                    init_game()
                    st.rerun()

    # Keyboard controls instructions
    st.markdown("---")
    st.info("💡 **Tip:** For better gameplay experience, click on the arrow buttons to control the snake. The game auto-refreshes to provide smooth movement!")

if __name__ == "__main__":
    main()