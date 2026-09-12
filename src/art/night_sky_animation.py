import turtle
import random
import time
# ____________________
# Screen Setup
# ____________________
screen = turtle.Screen()
screen.setup(900, 700)
screen.bgcolor("#020824")
screen.title("Moon & Night Sky Animation")
screen.tracer(0)
# ____________________
# Moon
# ____________________
moon = turtle.Turtle()
moon.hideturtle()
moon.penup()
moon.goto(250, 180)
moon.color("#FFFACD")
moon.begin_fill()
moon.circle(60)
moon.end_fill()
# Moon glow
glow = turtle.Turtle()
glow.hideturtle()
glow.penup()
for r in range(90, 60, -5):
    glow.goto(250, 180-r+60)
    glow.color("#E6E6FA")
    glow.pensize(2)
    glow.circle(r)
# ____________________
# Stars
# ____________________
stars = []
for i in range(70):
    star = turtle.Turtle()
    star.shape("circle")
    star.shapesize(0.15)
    star.penup()
    star.speed(0)
    star.color("white")
    star.goto(random.randint(-430,430), random.randint(-320,320))
    stars.append(star)
# ____________________
# Clouds
# ____________________
cloud = turtle.Turtle()
cloud.speed(0)
cloud.penup()
cloud.color("gray90")
cloud.hideturtle()
cloud_x = -500
# ____________________
# Ground
# ____________________
ground = turtle.Turtle()
ground.hideturtle()
ground.penup()
ground.goto(-450,-250)
ground.color("#013220")
ground.begin_fill()
ground.pendown()
ground.forward(900)
ground.right(90)
ground.forward(200)
ground.right(90)
ground.forward(900)
ground.right(90)
ground.forward(200)
ground.end_fill()
# ____________________
# Animation Loop
# ____________________
while True:
    # Twinkling stars
    for star in stars:
        if random.randint(0,8)==0:
            star.color("white")
            star.shapesize(random.uniform(0.1,0.35))
        else:
            star.shapesize(0.15)
    # Moving cloud
    cloud.clear()
    cloud.penup()
    cloud.goto(cloud_x,150)
    for i in range(5):
        cloud.dot(50)
        cloud.forward(25)
    cloud_x += 2
    if cloud_x > 500:
        cloud_x = -550
    screen.update()
    time.sleep(0.03)                   