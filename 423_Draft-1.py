from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import numpy as np
from time import time

# Global variables
WINDOW_SIZE = 800
season = 0  # 0: Spring, 1: Summer, 2: Fall, 3: Winter
is_night = False
leaves = []
snowflakes = []
raindrops = []
animation_speed = 0.01

class Particle:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.active = True

def init():
    glClearColor(0.529, 0.808, 0.922, 1.0)  # Sky blue color
    gluOrtho2D(0, WINDOW_SIZE, 0, WINDOW_SIZE)

def midpoint_line(x1, y1, x2, y2):
    points = []
    dx = x2 - x1
    dy = y2 - y1
    
    if abs(dx) > abs(dy):
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        dx = x2 - x1
        dy = y2 - y1
        y = y1
        d = 2 * abs(dy) - dx
        
        for x in range(int(x1), int(x2) + 1):
            points.append((x, y))
            if d > 0:
                y += 1 if dy > 0 else -1
                d -= 2 * dx
            d += 2 * abs(dy)
    else:
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            
        dx = x2 - x1
        dy = y2 - y1
        x = x1
        d = 2 * abs(dx) - dy
        
        for y in range(int(y1), int(y2) + 1):
            points.append((x, y))
            if d > 0:
                x += 1 if dx > 0 else -1
                d -= 2 * dy
            d += 2 * abs(dx)
    
    return points

def midpoint_circle(xc, yc, radius):
    points = []
    x = radius
    y = 0
    d = 1 - radius
    
    while x >= y:
        points.extend([
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x),
            (xc + y, yc - x), (xc - y, yc - x)
        ])
        
        y += 1
        if d < 0:
            d += 2 * y + 1
        else:
            x -= 1
            d += 2 * (y - x) + 1
    
    return points

def draw_tree(x, y, length, angle, depth):
    if depth > 0:
        x2 = x + length * math.cos(math.radians(angle))
        y2 = y + length * math.sin(math.radians(angle))
        
        # Draw branch
        points = midpoint_line(x, y, x2, y2)
        glColor3f(0.545, 0.271, 0.075)  # Brown color
        glBegin(GL_POINTS)
        for point in points:
            glVertex2f(point[0], point[1])
        glEnd()
        
        # Recursively draw smaller branches
        draw_tree(x2, y2, length * 0.7, angle - 30, depth - 1)
        draw_tree(x2, y2, length * 0.7, angle + 30, depth - 1)

def draw_leaves():
    global leaves
    
    if season == 2:  # Fall
        colors = [(1.0, 0.0, 0.0), (1.0, 0.5, 0.0), (1.0, 1.0, 0.0)]  # Red, Orange, Yellow
    else:
        colors = [(0.0, 0.8, 0.0), (0.0, 0.6, 0.0), (0.0, 1.0, 0.0)]  # Different shades of green
    
    for leaf in leaves:
        if leaf.active:
            glColor3f(*random.choice(colors))
            points = midpoint_circle(int(leaf.x), int(leaf.y), 3)
            glBegin(GL_POINTS)
            for point in points:
                glVertex2f(point[0], point[1])
            glEnd()
            
            if season == 2:  # Fall animation
                leaf.y -= leaf.speed
                leaf.x += math.sin(time() * 2) * 0.5
                
                if leaf.y < 0:
                    leaf.active = False

def draw_grass():
    grass_colors = {
        0: (0.0, 0.8, 0.0),  # Spring - Bright green
        1: (0.0, 0.6, 0.0),  # Summer - Dark green
        2: (0.7, 0.5, 0.0),  # Fall - Brown
        3: (1.0, 1.0, 1.0)   # Winter - White
    }
    
    glColor3f(*grass_colors[season])
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_SIZE, 0)
    glVertex2f(WINDOW_SIZE, 100)
    glVertex2f(0, 100)
    glEnd()

def update_particles():
    global snowflakes, raindrops
    
    if season == 3:  # Winter
        # Update snowflakes
        for flake in snowflakes:
            if flake.active:
                flake.y -= flake.speed
                flake.x += math.sin(time() * 2) * 0.5
                
                if flake.y < 0:
                    flake.y = WINDOW_SIZE
                    flake.x = random.randint(0, WINDOW_SIZE)
    else:
        # Update raindrops
        for drop in raindrops:
            if drop.active:
                drop.y -= drop.speed
                
                if drop.y < 0:
                    drop.y = WINDOW_SIZE
                    drop.x = random.randint(0, WINDOW_SIZE)

def draw_particles():
    global snowflakes, raindrops
    
    if season == 3:  # Winter
        glColor3f(1.0, 1.0, 1.0)  # White for snow
        for flake in snowflakes:
            if flake.active:
                points = midpoint_circle(int(flake.x), int(flake.y), 2)
                glBegin(GL_POINTS)
                for point in points:
                    glVertex2f(point[0], point[1])
                glEnd()
    elif random.random() < 0.3:  # 30% chance of rain
        glColor3f(0.7, 0.7, 1.0)  # Light blue for rain
        for drop in raindrops:
            if drop.active:
                points = midpoint_line(drop.x, drop.y, drop.x, drop.y - 10)
                glBegin(GL_POINTS)
                for point in points:
                    glVertex2f(point[0], point[1])
                glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Set background color based on time of day
    if is_night:
        glClearColor(0.0, 0.0, 0.2, 1.0)  # Dark blue for night
    else:
        glClearColor(0.529, 0.808, 0.922, 1.0)  # Sky blue for day
    
    # Draw grass
    draw_grass()
    
    # Draw tree
    draw_tree(WINDOW_SIZE//2, 100, 100, 90, 9)
    
    # Draw leaves
    draw_leaves()
    
    # Draw weather particles
    draw_particles()
    
    glutSwapBuffers()

def update(value):
    update_particles()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # 60 FPS

def keyboard(key, x, y):
    global is_night
    
    if key == b'd':  
        is_night = False
    elif key == b'n':  # Night
        is_night = True
    
    glutPostRedisplay()

def special_keys(key, x, y):
    global season
    
    if key == GLUT_KEY_RIGHT:
        season = (season + 1) % 4
    elif key == GLUT_KEY_LEFT:
        season = (season - 1) % 4
    
    glutPostRedisplay()

def init_particles():
    global leaves, snowflakes, raindrops
    
    # Initialize leaves
    leaves = [Particle(random.randint(WINDOW_SIZE//2 - 100, WINDOW_SIZE//2 + 100),
                      random.randint(200, 400),
                      random.uniform(0.5, 2.0)) for _ in range(100)]
    
    # Initialize snowflakes
    snowflakes = [Particle(random.randint(0, WINDOW_SIZE),
                          random.randint(0, WINDOW_SIZE),
                          random.uniform(1.0, 3.0)) for _ in range(100)]
    
    # Initialize raindrops
    raindrops = [Particle(random.randint(0, WINDOW_SIZE),
                         random.randint(0, WINDOW_SIZE),
                         random.uniform(5.0, 10.0)) for _ in range(200)]

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE)
    glutCreateWindow(b"Four Seasons Tree")
    
    init()
    init_particles()
    
    glutDisplayFunc(display)
    glutSpecialFunc(special_keys)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, update, 0)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
