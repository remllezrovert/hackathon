import time
import pygame
from math import *

def drawgraph(equationStr = "d[0]=sin(50*x)*50"):
    plotPoints = []
    x = 0
    y = 0
    for x in range(-500, 500):
        x = x + 500
        d = [0]
        exec(equationStr)
        y = d[0]
        y = -y + 300
        plotPoints.append([x, y])

    pygame.init()
    screen = pygame.display.set_mode([1000, 600])
    screen.fill([255, 255, 255])
    pygame.draw.lines(screen, [255, 0, 0], False, plotPoints, 2)
    sphere_radius = 5
    sphere_color = [0, 0, 255]  # Blue sphere

    current_index = 0

    running = True
    while running:
        screen.fill([255, 255, 255])  # Clear the screen
        
        pygame.draw.lines(screen, [255, 0, 0], False, plotPoints, 2)

        if current_index < len(plotPoints):
            sphere_x, sphere_y = plotPoints[current_index]
            pygame.draw.circle(screen, sphere_color, (int(sphere_x), int(sphere_y)), sphere_radius)

            current_index += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        time.sleep(0.01)

    pygame.quit()

def exitbutton():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

# Run the graph drawing function
drawgraph()
exitbutton()
