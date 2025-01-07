from OpenGL.GL import *
from OpenGL.GLUT import *
import random
import math

# Window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GROUND_HEIGHT = WINDOW_HEIGHT // 4

# Sun/Moon properties
SUN_RADIUS = 30
MOON_RADIUS = 20
STAR_COUNT = 50
sun_position = 0  # 0 to 180 degrees
is_day = True

# Wind properties
wind_strength = 0
wind_direction = 0

# Store star positions
stars = [(
    WINDOW_WIDTH * random.random(),
    WINDOW_HEIGHT * 3 / 4 * random.random() + WINDOW_HEIGHT / 4
) for _ in range(STAR_COUNT)]

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

def draw_circle(cx, cy, r):
    points = []
    x, y = 0, r
    d = 1 - r

    while x <= y:
        points.extend([
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x),
            (cx + y, cy - x), (cx - y, cy - x)
        ])

        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1

    glPointSize(2)
    glBegin(GL_POINTS)
    for px, py in points:
        glVertex2f(px / WINDOW_WIDTH * 2 - 1, py / WINDOW_HEIGHT * 2 - 1)
    glEnd()

grass_blades = []

def initializeGrass():
    global grass_blades
    grass_blades = []
    for _ in range(100):  # Create 100 grass blades
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, GROUND_HEIGHT)
        height = random.randint(20, 60)
        width = random.randint(5, 20)
        green = random.uniform(0.4, 1.0) if is_day else random.uniform(0.2, 0.5)
        color = (0, green, 0)
        grass_blades.append({
            'x': x,
            'y': y,
            'height': height,
            'width': width,
            'color': color,
            'bend': 0
        })

def draw_stars():
    glPointSize(2.0)
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 1.0)
    for x, y in stars:
        glVertex2f(x / WINDOW_WIDTH * 2 - 1, y / WINDOW_HEIGHT * 2 - 1)
    glEnd()

def get_background_color(sun_position):
    if is_day:
        progress = math.sin(sun_position * math.pi / 180)
        if progress < 0.3:
            r = 0.8 - progress
            g = 0.6 - progress * 0.3
            b = progress + 0.4
        else:
            r = 0.4 * (1 - progress)
            g = 0.7 * (1 - progress * 0.3)
            b = 0.9
    else:
        r = 0.05
        g = 0.05
        b = 0.2
    return r, g, b

def display():
    global grass_blades, wind_strength, wind_direction, sun_position

    # Set background color based on time of day
    bg_color = get_background_color(sun_position)
    glClearColor(*bg_color, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw stars if it's night
    if not is_day:
        draw_stars()

    # Draw sun/moon
    x = WINDOW_WIDTH * sun_position / 180
    y = GROUND_HEIGHT + (WINDOW_HEIGHT * 3 // 4) * math.sin(sun_position * math.pi / 180)

    if is_day:
        glColor3f(1.0, 1.0, 0.0)  # Yellow for sun
        draw_circle(int(x), int(y), SUN_RADIUS)
    else:
        glColor3f(0.9, 0.9, 1.0)  # White for moon
        draw_circle(int(x), int(y), MOON_RADIUS)

    # Update and draw grass
    for blade in grass_blades:
        # Update the bend of each grass blade based on wind
        blade['bend'] += wind_strength * wind_direction
        # Add some randomness to the movement
        blade['bend'] += random.uniform(-0.5, 0.5)
        # Limit the maximum bend
        blade['bend'] = max(min(blade['bend'], blade['height'] // 2), -blade['height'] // 2)

        drawGrassBlade(blade['x'], blade['y'], blade['height'], blade['width'],
                      blade['color'], blade['bend'])

    # Gradually reduce wind strength
    wind_strength *= 0.99

    glutSwapBuffers()
    glutPostRedisplay()

def keyboard(key, x, y):
    global wind_strength, wind_direction, sun_position, is_day
    if key == b'd':
        sun_position += 5
        if sun_position >= 180:
            sun_position = 0
            is_day = not is_day
            # Reinitialize grass with new colors for time of day
            initializeGrass()

    glutPostRedisplay()

def special_keys(key, x, y):
    global wind_strength, wind_direction
    if key == GLUT_KEY_LEFT:
        wind_direction = -1
        wind_strength = min(wind_strength + 0.5, 10)
    elif key == GLUT_KEY_RIGHT:
        wind_direction = 1
        wind_strength = min(wind_strength + 0.5, 10)

    glutPostRedisplay()

def reshape(width, height):
    glViewport(0, 0, width, height)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Day-Night Cycle with Grass Animation")

    initializeGrass()

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutReshapeFunc(reshape)
    glutMainLoop()

if __name__ == "__main__":
    main()