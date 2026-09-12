import random
import time
import turtle


screen = turtle.Screen()
screen.setup(900, 700)
screen.bgcolor("#1b1035")
screen.title("Love Letter Animation")
screen.tracer(0)

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)

letter = turtle.Turtle()
letter.hideturtle()
letter.speed(0)

writer = turtle.Turtle()
writer.hideturtle()
writer.penup()
writer.color("red")


def draw_envelope():
    pen.clear()
    pen.penup()
    pen.goto(-170, 120)
    pen.color("white", "white")
    pen.begin_fill()
    pen.pendown()
    for _ in range(2):
        pen.forward(340)
        pen.left(90)
        pen.forward(200)
        pen.left(90)
    pen.end_fill()

    pen.penup()
    pen.goto(-170, 80)
    pen.color("lightgray", "lightgray")
    pen.begin_fill()
    pen.pendown()
    pen.goto(0, -10)
    pen.goto(170, 80)
    pen.goto(-170, 80)
    pen.end_fill()

    pen.penup()
    pen.goto(0, -15)
    pen.color("red")
    pen.write("❤", align="center", font=("Arial", 32, "bold"))


def draw_letter(y):
    letter.clear()
    letter.penup()
    letter.goto(-140, y)
    letter.color("#FFF8DC", "#FFF8DC")
    letter.begin_fill()
    letter.pendown()
    for _ in range(2):
        letter.forward(280)
        letter.left(90)
        letter.forward(170)
        letter.left(90)
    letter.end_fill()


def draw_message():
    messages = [
        "Dear Love, ❤",
        "Every day with you",
        "is my favorite adventure.",
        "Thank you for being",
        "part of my life",
        "Forever Yours ❤",
    ]

    y = 180
    for line in messages:
        writer.goto(0, y)
        writer.write(line, align="center", font=("Arial", 18, "bold"))
        y -= 30
        screen.update()
        time.sleep(0.6)


hearts = []
for _ in range(18):
    heart = turtle.Turtle()
    heart.hideturtle()
    heart.penup()
    heart.color("pink")
    heart.goto(random.randint(-400, 400), random.randint(-320, 320))
    hearts.append(heart)


def animate_floating_hearts():
    while True:
        for heart in hearts:
            x, y = heart.position()
            heart.clear()
            heart.goto(x, y + 3)
            heart.write("❤", align="center", font=("Arial", 14, "bold"))
            if y > 340:
                heart.goto(random.randint(-420, 420), -340)
        screen.update()
        time.sleep(0.03)


if __name__ == "__main__":
    draw_envelope()
    for y in range(-120, 70, 4):
        draw_letter(y)
        screen.update()
        time.sleep(0.03)

    draw_message()
    animate_floating_hearts()
