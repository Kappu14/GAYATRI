import turtle
t = turtle.Turtle()
t.screen.bgcolor("black")
t.speed(0)
t.pensize(1)
colors = ["pink", "hotpink", "deeppink", "palevioletred"]
for x in range(150):
    t.color(colors[x % 4])
    t.circle(x)
    t.left(30)
t.hideturtle()
turtle.done()    