import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLU as glu
import math
import random
import time

# Window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GROUND_HEIGHT = 100

# Sun/Moon properties
SUN_RADIUS = 30
MOON_RADIUS = 20
STAR_COUNT = 50
sun_position = 0  # 0 to 180 degrees
is_day = True

# Grass variables
grass_blades = []
wind_strength = 0
wind_direction = 0

# Wind variables
wind_strength = 0
wind_direction = 0

# Global variables For Rain
raindrops = []  # List of current raindrops
rain_bend = 0.0  # Directional bend for raindrops
max_raindrops = 250  # Maximum number of raindrops at any given time

# Global variables for Tree, Leaves, Snow, Day, Season
falling_leaves = []
is_falling = False
is_paused = False
leaf_positions = []
current_season = 1  # 1: Summer, 2: Rainy, 3: Winter
# raindrops = []
snowflakes = []
leaf_fall_timer = 0
leaf_fall_interval = 10


class Leaf:
    def __init__(self, x, y, season):
        self.x = x
        self.y = y
        self.speed = 2
        self.swing = random.uniform(-1, 1)
        self.season = season
        self.set_color()

    def set_color(self):
        if self.season == 1:  # Summer
            self.start_color = [0.0, 0.8, 0.0]
            self.end_color = [0.0, 0.8, 0.0]
        elif self.season == 2:  # Rainy
            self.start_color = [1.0, 0.941, 0.941]
            self.end_color = [1.0, 0.941, 0.941]
        else:  # Winter
            self.start_color = [1.0, 0.7176, 0.7725]  # Pink
            self.end_color = [1.0, 0.7176, 0.7725]  # Orange
        self.color = self.start_color.copy()

    def update(self):
        if not is_paused:
            self.y -= self.speed
            self.x += math.sin(self.y / 20) * self.swing

            # Change color gradually as it falls
            if self.y > 100:
                fall_progress = (600 - self.y) / 500
                for i in range(3):
                    self.color[i] = self.start_color[i] + (self.end_color[i] - self.start_color[i]) * fall_progress

        return self.y > 100


class Raindrop:
    def __init__(self):
        self.x = random.uniform(-400, 1200)
        self.y = 600
        self.speed = 8

    def update(self):
        if not is_paused:
            self.y -= self.speed
            self.x += rain_bend * 1.5
        return self.y > 0


class Snowflake:
    def __init__(self):
        self.x = random.randint(0, 800)
        self.y = random.randint(600, 1200)  # Start above the visible screen
        self.speed = random.uniform(2, 4)  # Random speed for each snowflake
        self.swing = random.uniform(-0.5, 0.5)

    def update(self):
        if not is_paused:
            self.y -= self.speed
            self.x += self.swing + math.sin(self.y / 80) * 0.3

            # Reset snowflake position when it falls below the screen
            if self.y < 0:
                self.x = random.randint(0, 800)
                self.y = random.randint(600, 1200)
                self.speed = random.uniform(2, 4)
                self.swing = random.uniform(-0.5, 0.5)

        return True


# Drawing Grass
class GrassBlade:
    def __init__(self, x, y, height, width, color):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = color
        self.bend = 0

    def draw(self):
        bend_x = self.x + self.bend
        gl.glColor3f(*self.color)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(self.x, self.y)
        gl.glVertex2f((bend_x - self.width // 2), (self.y + self.height))
        gl.glVertex2f(self.x, self.y)
        gl.glVertex2f((bend_x + self.width // 2), (self.y + self.height))
        gl.glEnd()

    def update(self, wind_strength, wind_direction):
        self.bend += wind_strength * wind_direction
        self.bend += random.uniform(-0.5, 0.5)
        self.bend = max(min(self.bend, self.height // 2), -self.height // 2)


class GrassField:
    def __init__(self, blade_count=100):
        self.blades = []
        self.wind_strength = 0
        self.wind_direction = 0
        self.initialize_blades(blade_count)

    def initialize_blades(self, blade_count=300):
        self.blades = []
        for _ in range(blade_count):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, GROUND_HEIGHT)
            height = 30
            width = random.randint(5, 20)
            green = random.uniform(0.4, 1.0)
            color = (0, green, 0)
            self.blades.append(GrassBlade(x, y, height, width, color))

    def update_and_draw(self):
        for blade in self.blades:
            blade.update(self.wind_strength, self.wind_direction)
            blade.draw()
        self.wind_strength *= 0.5


# Grass instance
grass_field = GrassField()


def init():
    global grass_field
    # Set OpenGL projection matrix
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)

    # Initialize grass blades
    grass_field.initialize_blades(100)


# Helper function to assist Midpoint Line Algo in drawing the pixels
def draw_pixel(x, y):
    gl.glBegin(gl.GL_POINTS)
    gl.glVertex2f(x, y)
    gl.glEnd()


# Midpoint Line Algo
def midpoint_line(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1

    x_inc = 1 if x2 > x1 else -1
    y_inc = 1 if y2 > y1 else -1

    if dx > dy:
        p = 2 * dy - dx
        for _ in range(dx):
            draw_pixel(x, y)
            if p >= 0:
                y += y_inc
                p -= 2 * dx
            x += x_inc
            p += 2 * dy
    else:
        p = 2 * dx - dy
        for _ in range(dy):
            draw_pixel(x, y)
            if p >= 0:
                x += x_inc
                p -= 2 * dy
            y += y_inc
            p += 2 * dx
    draw_pixel(x, y)


# Midpoint Circle Algo
def midpoint_circle(center_x, center_y, radius):
    x, y = 0, radius
    p = 1 - radius

    def plot_circle_points(cx, cy, x, y):
        draw_pixel(cx + x, cy + y)
        draw_pixel(cx - x, cy + y)
        draw_pixel(cx + x, cy - y)
        draw_pixel(cx - x, cy - y)
        draw_pixel(cx + y, cy + x)
        draw_pixel(cx - y, cy + x)
        draw_pixel(cx + y, cy - x)
        draw_pixel(cx - y, cy - x)

    while x <= y:
        plot_circle_points(center_x, center_y, x, y)
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1


# Drawing the tree
def draw_stem(x, y):
    gl.glColor3f(0.545, 0.271, 0.075)  # Stem color
    midpoint_line(int(x) - 15, int(y), int(x) - 15, int(y) + 108)
    midpoint_line(int(x) + 15, int(y), int(x) + 15, int(y) + 108)
    midpoint_line(int(x) - 14, int(y), int(x) - 14, int(y) + 108)
    midpoint_line(int(x) + 14, int(y), int(x) + 14, int(y) + 108)


def draw_tree(x, y, length, angle, depth):
    if depth > 0:
        x2 = x + length * math.cos(math.radians(angle))
        y2 = y + length * math.sin(math.radians(angle))

        # Draw branch
        gl.glColor3f(0.545, 0.271, 0.075)  # Branch color
        if angle != 90:
            midpoint_line(int(x), int(y), int(x2), int(y2))
            midpoint_line(int(x) - 1, int(y) + 1, int(x2) + 1, int(y2) + 1)

        new_length = length * 0.7
        draw_tree(x2, y2, new_length, angle - 20, depth - 3)
        draw_tree(x2, y2, new_length, angle + 20, depth - 3)
        draw_tree(x2, y2, new_length - 1, angle - 60, depth - 3)
        draw_tree(x2, y2, new_length - 1, angle + 60, depth - 3)


min_distance = 12  # Minimum distance between the centers of the leaves


def draw_leaves(x_center, y_center, radius):
    global leaf_positions
    leaf_radius = 8  # Radius of individual leaves

    if not leaf_positions and not is_falling:
        num_leaves = 400  # Number of leaves (can adjust as needed)
        for i in range(num_leaves):
            # Calculate the angle for this leaf's position (evenly spaced around the circle)
            angle = random.uniform(0, 2 * math.pi)

            # Increase spread by adjusting the radius differently for x and y axes
            x_distance = random.uniform(0, radius * 2.4)  # Wider spread on x-axis
            y_distance = random.uniform(0, radius + 22)  # Normal spread on y-axis

            # Calculate the potential new leaf's position using polar coordinates
            leaf_x = x_center + x_distance * math.cos(angle)
            leaf_y = y_center + y_distance * math.sin(angle)

            # Ensure no new leaf is too close to an existing one
            too_close = False
            for existing_x, existing_y in leaf_positions:
                distance = math.sqrt((leaf_x - existing_x) ** 2 + (leaf_y - existing_y) ** 2)
                if distance < min_distance:  # Check if the new leaf is too close
                    too_close = True
                    break

            if too_close:
                continue

            # Store the leaf's position
            leaf_positions.append((int(leaf_x), int(leaf_y)))

    # Draw the leaves from the stored positions

    if current_season == 1:
        gl.glColor3f(0.0, 0.8, 0.0)  # for summer
    elif current_season == 2:
        gl.glColor3f(1.0, 0.941, 0.941)  # for rainy season
    else:
        gl.glColor3f(1.0, 0.7176, 0.7725)  # for winter

    for leaf_x, leaf_y in leaf_positions:
        midpoint_circle(leaf_x, leaf_y, leaf_radius)


# Celestial class containing sun, moon, stars, night and day funtions
class CelestialBodyManager:
    def __init__(self):
        self.sun_position = 0
        self.is_day = True
        self.stars = [
            (
                random.uniform(0, WINDOW_WIDTH), random.uniform(WINDOW_HEIGHT // 2, WINDOW_HEIGHT)
            ) for _ in range(STAR_COUNT)]

    def update_background_color(self):
        """Set the background color based on the time of day and sun position."""
        progress = math.sin(self.sun_position * math.pi / 180)
        if self.is_day:
            # Daytime color transition
            if progress < 0.3:
                r = 0.8 - progress
                g = 0.6 - progress * 0.3
                b = progress + 0.4
            else:
                r = 0.4 * (1 - progress)
                g = 0.7 * (1 - progress * 0.3)
                b = 0.9
        else:
            # Nighttime color
            r = 0.05
            g = 0.05
            b = 0.2
        gl.glClearColor(r, g, b, 1.0)

    def toggle_day_night(self):
        """Switch between day and night."""
        self.sun_position += 5
        if self.sun_position >= 180:
            self.sun_position = 0
            self.is_day = not self.is_day

    def draw_sun_or_moon(self):
        """Draw the sun or moon based on the current time of day."""
        x = WINDOW_WIDTH * self.sun_position / 180
        y = GROUND_HEIGHT + (WINDOW_HEIGHT * 3 // 4) * math.sin(self.sun_position * math.pi / 180)
        if self.is_day:
            gl.glColor3f(1.0, 1.0, 0.0)  # Yellow for sun
        else:
            gl.glColor3f(0.9, 0.9, 1.0)  # White for moon
        # Use GL_POINTS for the circle drawing
        radius = SUN_RADIUS if is_day else MOON_RADIUS
        midpoint_circle(x, y, radius)

    def draw_stars(self):
        """Draw stars at night."""
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glBegin(gl.GL_POINTS)
        for x, y in self.stars:
            gl.glVertex2f(x, y)
        gl.glEnd()

    def update_and_draw(self):
        """Update and draw the celestial bodies."""
        self.update_background_color()
        self.draw_sun_or_moon()
        if not self.is_day:
            self.draw_stars()


# celestialBody Instance
celestial_manager = CelestialBodyManager()


# Drawing the ground
def draw_ground():
    gl.glColor3f(0.0, 0.8, 0.0)
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2f(0, 0)
    gl.glVertex2f(800, 0)
    gl.glVertex2f(800, 100)
    gl.glVertex2f(0, 100)
    gl.glEnd()


def draw_falling_leaves():
    for leaf in falling_leaves:
        gl.glColor3f(leaf.color[0], leaf.color[1], leaf.color[2])
        midpoint_circle(int(leaf.x), int(leaf.y), 8)


# Drawing Rain
def draw_rain():
    gl.glColor3f(0.5, 0.5, 1.0)  # Light blue for rain
    gl.glLineWidth(2.0)
    gl.glBegin(gl.GL_LINES)
    for raindrop in raindrops:
        gl.glVertex2f(raindrop.x, raindrop.y)
        gl.glVertex2f(raindrop.x + rain_bend * 1, raindrop.y - 15)  # Slanted rain
    gl.glEnd()


def update_rain():
    global raindrops
    if not is_paused:
        raindrops = [raindrop for raindrop in raindrops if raindrop.update()]
        if len(raindrops) < max_raindrops:
            raindrops.append(Raindrop())


def draw_snow():
    gl.glColor3f(1.0, 1.0, 1.0)  # White for snow
    gl.glPointSize(3.0)
    gl.glBegin(gl.GL_POINTS)
    for snowflake in snowflakes:
        gl.glVertex2f(snowflake.x, snowflake.y)
    gl.glEnd()


def update_falling_leaves():
    global falling_leaves, leaf_fall_timer
    if not is_paused and is_falling:
        falling_leaves = [leaf for leaf in falling_leaves if leaf.update()]

        # Add new leaves one by one
        leaf_fall_timer += 1
        if leaf_fall_timer >= leaf_fall_interval and leaf_positions:
            x, y = leaf_positions.pop(random.randint(0, len(leaf_positions) - 1))
            falling_leaves.append(Leaf(x, y, current_season))
            leaf_fall_timer = 0


def update_snow():
    global snowflakes
    if not is_paused:
        snowflakes = [snowflake for snowflake in snowflakes if snowflake.update()]
        if len(snowflakes) < 100:
            snowflakes.append(Snowflake())


def mouse_click(button, state, x, y):
    global is_falling
    if button == glut.GLUT_LEFT_BUTTON and state == glut.GLUT_DOWN:
        is_falling = True


def keyboard(key, x, y):
    global is_paused, is_falling, falling_leaves, current_season, raindrops, snowflakes, leaf_positions, is_day, sun_position
    if key == b' ':
        is_paused = not is_paused  # Toggle pause
    elif key == b'r' or key == b'R':
        is_paused = False
        is_falling = False
        falling_leaves.clear()
        raindrops.clear()
        snowflakes.clear()
        leaf_positions.clear()
    elif key in [b'1', b'2', b'3']:
        current_season = int(key)
        # is_falling = False
        # falling_leaves.clear()
        # raindrops.clear()
        # snowflakes.clear()
        # leaf_positions.clear()
    elif key == b'd' or key == b'D':
        celestial_manager.toggle_day_night()
        if sun_position >= 180:
            sun_position = 0
            is_day = not is_day

    glut.glutPostRedisplay()


# Special Keys For Rain Control
def special_keys(key, x, y):
    global rain_bend
    if key == glut.GLUT_KEY_LEFT:
        if rain_bend > -2:
            rain_bend -= 1
    elif key == glut.GLUT_KEY_RIGHT:
        if rain_bend < 2:
            rain_bend += 1


def display():
    gl.glPointSize(2.0)
    global grass_field, wind_strength, sun_position, is_day

    celestial_manager.update_background_color()
    if not celestial_manager.is_day:
        celestial_manager.draw_stars()

    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    draw_ground()
    celestial_manager.update_and_draw()
    grass_field.update_and_draw()

    # Gradually reduce wind strength
    wind_strength *= 0.99

    draw_stem(600, 100)
    draw_tree(600, 100, 100, 90, 9)
    draw_leaves(600, 250, 50)

    if is_falling:
        draw_falling_leaves()
        update_falling_leaves()
    if current_season == 2:  # Rainy season
        draw_rain()
        update_rain()
    elif current_season == 3:  # Winter
        draw_snow()
        update_snow()

    glut.glutSwapBuffers()
    glut.glutPostRedisplay()


def main():
    glut.glutInit()
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB)
    glut.glutInitWindowSize(800, 600)
    glut.glutCreateWindow(b"Seasonal Tree Animation")
    glut.glutDisplayFunc(display)
    glut.glutMouseFunc(mouse_click)
    glut.glutKeyboardFunc(keyboard)
    glut.glutSpecialFunc(special_keys)
    init()
    glut.glutMainLoop()


# print(grass_blades)
if __name__ == "__main__":
    main()