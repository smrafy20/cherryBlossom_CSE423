from OpenGL.GL import *
from OpenGL.GLUT import *
import random

from OpenGL.raw.GLU import gluOrtho2D


def int_FindZone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    zone = 0

    if abs(dx) > abs(dy):
        if dx >= 0 and dy > 0:
            zone = 0
        elif dx <= 0 and dy >= 0:
            zone = 3
        elif dx < 0 and dy < 0:
            zone = 4
        elif dx > 0 and dy < 0:
            zone = 7

    else:
        if dx >= 0 and dy > 0:
            zone = 1
        elif dx < 0 and dy > 0:
            zone = 2
        elif dx < 0 and dy < 0:
            zone = 5
        elif dx >= 0 and dy < 0:
            zone = 6
    return zone


def convertToZero(x, y, zone):
    if zone == 1:
        X, Y = y, x
    elif zone == 2:
        X, Y = y, -x
    elif zone == 3:
        X, Y = -x, y
    elif zone == 4:
        X, Y = -x, -y
    elif zone == 5:
        X, Y = -y, -x
    elif zone == 6:
        X, Y = -y, x
    elif zone == 7:
        X, Y = x, -y
    return int(X), int(Y)


def convertToOriginal(x, y, zone):
    if zone == 1:
        X, Y = y, x
    elif zone == 2:
        X, Y = -y, x
    elif zone == 3:
        X, Y = -x, y
    elif zone == 4:
        X, Y = -x, -y
    elif zone == 5:
        X, Y = -y, -x
    elif zone == 6:
        X, Y = y, -x
    elif zone == 7:
        X, Y = x, -y
    return int(X), int(Y)


def drawPoint(x, y, size=2):
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(int(x), int(y))
    glEnd()


def drawLine(x1, y1, x2, y2, color):
    glColor3f(*color)
    zone = int_FindZone(x1, y1, x2, y2)
    if zone != 0:
        x1, y1 = convertToZero(x1, y1, zone)
        x2, y2 = convertToZero(x2, y2, zone)
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    y = y1

    for x in range(int(x1), int(x2)):
        if zone != 0:
            original_x, original_y = convertToOriginal(x, y, zone)
            drawPoint(original_x, original_y)
        else:
            drawPoint(x, y)
        if d > 0:
            d = d + incNE
            y += 1
        else:
            d = d + incE


def drawGrassBlade(x, y, height, width, color):
    # Draw left side of the grass blade
    drawLine(x, y, x - width // 2, y + height, color)
    # Draw right side of the grass blade
    drawLine(x, y, x + width // 2, y + height, color)


def display():
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw multiple grass blades
    for _ in range(100):  # Draw 100 grass blades
        x = random.randint(0, 800)  # Random x position
        y = random.randint(0, 100)  # Random y position near the bottom
        height = random.randint(20,60)  # Random height (shorter)
        width = random.randint(5, 20)  # Random width (slightly narrower)

        # Generate a random shade of green
        green = random.uniform(0.4, 1.0)
        color = (0, green, 0)  # Green color with varying intensity

        drawGrassBlade(x, y, height, width, color)

    glFlush()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Grass Field")

    glClearColor(0.529, 0.808, 0.922, 0.0)  # Sky blue background
    gluOrtho2D(0, 800, 0, 600)

    glutDisplayFunc(display)
    glutMainLoop()


if __name__ == "__main__":
    main()

