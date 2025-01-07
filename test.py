from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Window dimensions
width, height = 800, 600

# Define the leaf shape (ellipse)
def draw_leaf():
    leaf_center = (400, 300)
    leaf_width = 200
    leaf_height = 100

    glBegin(GL_POINTS)
    for angle in range(0, 360, 2):  # Generate points along the leaf's ellipse
        x = leaf_center[0] + leaf_width * math.cos(math.radians(angle))
        y = leaf_center[1] + leaf_height * math.sin(math.radians(angle))
        glVertex2f(x, y)
    glEnd()

# Draw veins as points along lines
def draw_veins():
    veins = [
        # Main vein
        [(400, 300), (400, 100)],  # Central vein
        [(400, 300), (400, 500)],  # Central vein bottom

        # Side veins (diagonal)
        [(400, 300), (550, 400)],  # Upper right side vein
        [(400, 300), (250, 400)],  # Upper left side vein
        [(400, 300), (550, 200)],  # Lower right side vein
        [(400, 300), (250, 200)],  # Lower left side vein
    ]
    
    glBegin(GL_POINTS)
    for vein in veins:
        x1, y1 = vein[0]
        x2, y2 = vein[1]
        # Interpolate points along the line between (x1, y1) and (x2, y2)
        steps = 20
        for i in range(steps):
            t = i / (steps - 1)
            x = x1 * (1 - t) + x2 * t
            y = y1 * (1 - t) + y2 * t
            glVertex2f(x, y)
    glEnd()

# Initialize OpenGL and GLUT settings
def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)  # Set background to white
    glPointSize(5)  # Increase point size for visibility
    glOrtho(0, width, 0, height, -1, 1)  # Orthogonal projection
    glEnable(GL_POINT_SMOOTH)  # Enable point smoothing

# Display function for rendering
def display():
    glClear(GL_COLOR_BUFFER_BIT)  # Clear the screen

    # Draw a single debug point in the center to check if rendering works
    glBegin(GL_POINTS)
    glVertex2f(width // 2, height // 2)  # Draw a point in the center of the screen
    glEnd()

    draw_leaf()  # Draw the leaf
    draw_veins()  # Draw the veins

    glFlush()  # Finish rendering
    glutSwapBuffers()  # Swap buffers to display the result

# Main function to set up GLUT and OpenGL
def main():
    glutInit()  # Initialize GLUT
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  # Set display mode
    glutInitWindowSize(width, height)  # Set window size
    glutCreateWindow(b"Leaf with Veins")  # Create window with title (as byte string)
    init()  # Initialize OpenGL settings
    glutDisplayFunc(display)  # Register display callback function
    glutMainLoop()  # Start the GLUT main loop

if __name__ == "__main__":
    main()
