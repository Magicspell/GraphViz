from graphVizUI import GraphWidget
from graph import Graph
import numpy as np
import pygame

g = GraphWidget(0, 0, 1, 1, (0, 0, 0), graph = Graph(np.array([
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0]
])))

(WIDTH, HEIGHT) = (720, 720)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.init()

while True:
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                exit(0)
    g.draw(screen, 0, 0, WIDTH, HEIGHT)
    pygame.display.flip()