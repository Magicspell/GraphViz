from graphVizUI import GraphUIObject, Spectrum
from pyUI import Screen
from graph import Graph
import numpy as np
import pygame

# g = GraphUIObject(0, 0, 1, 1, (0, 0, 0), graph = Graph(np.array([
#     [0, 1, 0],
#     [1, 0, 1],
#     [0, 1, 0]
# ])))


# s = Plotter(0, 0, 1, 1, (0, 0, 0), data = [0, 3, 4, 2])

(WIDTH, HEIGHT) = (720, 720)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.init()
default_font = pygame.font.Font('freesansbold.ttf', 20)

spectrum = Spectrum(0, 0, 1, 1, (0, 0, 0), font = default_font, graph = Graph(np.array([
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0]
])))

s = Screen(0, 0, WIDTH, HEIGHT, objects = [spectrum])

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