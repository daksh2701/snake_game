
# Move the snake
# control the snake
# detect the collision with food
# create a scorecard
# detect collision with wall
# detect collision with body
import os
import time
os.environ['TCL_LIBRARY'] = r'C:\Program Files\Python313\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Program Files\Python313\tcl\tk8.6'
from turtle import Screen, Turtle
from food import Food
from snake import Snake
from scoreboard import Scoreboard

screen = Screen()
screen.setup(width=800, height = 800)
screen.bgcolor("black")
screen.title("Snake Game")
screen.tracer(0)

snake = Snake()
food = Food()
scoreboard = Scoreboard()

screen.listen()
screen.onkey(snake.up,"Up")
screen.onkey(snake.down,"Down")
screen.onkey(snake.left,"Left")
screen.onkey(snake.right,"Right")


game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(0.1)
    snake.move()

# collision with food
    if snake.head.distance(food) < 20:
        print("nom nom nom")
        food.refresh()
        snake.extend_snake()
        scoreboard.increase_score()

# detect collision with wall
    if snake.head.xcor() > 380 or snake.head.xcor() < -380 or snake.head.ycor() > 380 or snake.head.ycor() < -380:
        game_is_on = False
        scoreboard.game_over()

# detect collision with tail
#     if head collides with any segmnet in the tail then game over
    for segment in snake.segments:
        if segment == snake.head:
            pass
        elif snake.head.distance(segment) < 15:
            game_is_on = False
            scoreboard.game_over()

screen.exitonclick()