from OpenGL.GL import *
from OpenGL.GLUT import *
import random
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
wind_strength = 0  # Global variable to track wind strength
wind_direction = 0  # 0 for no wind, -1 for left to right, 1 for right to left


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
    glVertex2f(x / WINDOW_WIDTH * 2 - 1, y / WINDOW_HEIGHT * 2 - 1)
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


def drawGrassBlade(x, y, height, width, color, bend):
    # Calculate the bend at the top of the grass blade
    bend_x = x + bend

    # Draw left side of the grass blade
    drawLine(x, y, bend_x - width // 2, y + height, color)
    # Draw right side of the grass blade
    drawLine(x, y, bend_x + width // 2, y + height, color)


grass_blades = []


def initializeGrass():
    global grass_blades
    grass_blades = []
    for _ in range(100):  # Create 100 grass blades
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT // 6)
        height = random.randint(20, 60)
        width = random.randint(5, 20)
        green = random.uniform(0.4, 1.0)
        color = (0, green, 0)
        grass_blades.append({
            'x': x,
            'y': y,
            'height': height,
            'width': width,
            'color': color,
            'bend': 0
        })


def display():
    global grass_blades, wind_strength, wind_direction
    glClear(GL_COLOR_BUFFER_BIT)

    for blade in grass_blades:
        # Update the bend of each grass blade based on wind
        blade['bend'] += wind_strength * wind_direction
        # Add some randomness to the movement
        blade['bend'] += random.uniform(-0.5, 0.5)
        # Limit the maximum bend
        blade['bend'] = max(min(blade['bend'], blade['height'] // 2), -blade['height'] // 2)

        drawGrassBlade(blade['x'], blade['y'], blade['height'], blade['width'], blade['color'], blade['bend'])

    # Gradually reduce wind strength
    wind_strength *= 0.99

    glutSwapBuffers()
    glutPostRedisplay()


def keyboard(key, x, y):
    global wind_strength, wind_direction
    if key == GLUT_KEY_LEFT:
        wind_direction = -1  # Wind blows from left to right
        wind_strength = min(wind_strength + 0.5, 10)
    elif key == GLUT_KEY_RIGHT:
        wind_direction = 1  # Wind blows from right to left
        wind_strength = min(wind_strength + 0.5, 10)

    glutPostRedisplay()


def reshape(width, height):
    glViewport(0, 0, width, height)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Grass Wind Animation")

    glClearColor(0.529, 0.808, 0.922, 0.0)  # Sky blue background

    initializeGrass()

    glutDisplayFunc(display)
    glutSpecialFunc(keyboard)  # Handle special key presses (arrow keys)
    glutReshapeFunc(reshape)
    glutMainLoop()


if __name__ == "__main__":
    main()

