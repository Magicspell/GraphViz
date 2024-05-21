from graphVizUI import GraphUIObject, Spectrum, GraphVisualizer
from pyUI import Screen
from graph import Graph
import numpy as np
import pygame

(WIDTH, HEIGHT) = (1440, 720)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.init()
default_font = pygame.font.Font('freesansbold.ttf', 20)

matrix = np.array([
    [0, 1, 0, 1, 1, 0, 0, 0],
    [1, 0, 1, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0, 1, 0],
    [1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1],
    [0, 1, 0, 0, 1, 0, 1, 0],
    [0, 0, 1, 0, 0, 1, 0, 1],
    [0, 0, 0, 1, 1, 0, 1, 0]
])

graph = Graph(matrix)

g = GraphVisualizer(0, 0, 1, 1, (0, 0, 0), graph = graph, font = default_font)


s = Screen(0, 0, WIDTH, HEIGHT, objects = [g])

while True:
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                exit(0)
            case pygame.VIDEORESIZE:
                s.width = screen.get_width()
                s.height = screen.get_height()
                s.set_all_changed()
    # s.draw(screen, 0, 0, WIDTH, HEIGHT)
    s.draw(screen)
    pygame.display.flip()