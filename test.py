import numpy as np
import pygame
from typing import Tuple, List
import math
import random
from MagSim import update_object as apply_mag, update_objects as apply_mags_good
# import networkx as nx

SCALE = 200
SCROLL_AMT = 0.35
TEXT_PADDING = 10

# Number of digits to round eigenvalues to when finding two lowest values.
ROUND_DIGITS = 2
NODE_RADIUS = 15
CONNECTION_CHANCE = 0.3

# count intersecting points, for each pair of nodes that intersect, swap them.
RAND_MATRIX_SIZE = 7

# Cube matrix
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

def generate_random_graph(size : int):
    ret = np.zeros((size, size))
    for x in range(size):
        for y in range(size):
            if random.random() < CONNECTION_CHANCE and x != y:
                ret[x][y] = 1
                ret[y][x] = 1
    return ret

# matrix = generate_random_graph(RAND_MATRIX_SIZE)
# print(f"Generated random adjancency matrix of size {RAND_MATRIX_SIZE}: {matrix}")

def n_to_nth(n : int) -> str:
    if n == 11 or n == n == 12 or n == 13: return f"{n}th"
    if n % 10 == 1: return f"{n}st"
    if n % 10 == 2: return f"{n}nd"
    if n % 10 == 3: return f"{n}rd"
    return f"{n}th"

# Returns list of object coordinates after applying eigenvector conversions to cartesian coordinates.
# Format of array: each row is a node: [x, y]
def calc_graph_eig(adj_matrix : np.array, x_coords_index : int = 0,
        y_coords_index : int = 1) -> np.array:
    diag = np.diag(np.sum(adj_matrix, axis=0))
    laplacian = np.subtract(diag, adj_matrix)

    eigs = np.linalg.eig(laplacian).eigenvectors

    x_pos = eigs[:, x_coords_index]
    y_pos = eigs[:, y_coords_index]

    coords = np.flip(
        np.rot90([x_pos, y_pos], k=1),
        axis=0
    ).tolist()
    return coords

def draw_graph(coords : np.array, adj_matrix : np.array, screen : pygame.surface,
        x_offset : int = 0, y_offset : int = 0, scale : int = SCALE):
    node_s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    edge_s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    text_s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    node_i = 0
    for c in coords:
        edge_i = 0
        for e in adj_matrix[node_i]:
            if e:
                pygame.draw.line(edge_s, (255,255,255), (c[0] * scale + x_offset,
                    c[1] * scale + y_offset), (coords[edge_i][0] * scale + x_offset, 
                    coords[edge_i][1] * scale + y_offset))
            edge_i += 1
        v_x = c[0] * scale + x_offset
        v_y = c[1] * scale + y_offset
        pygame.draw.circle(node_s, (255,0,0), (v_x, v_y), NODE_RADIUS)

        label = font.render(str(node_i), True, (255, 255, 255))
        text_s.blit(label, (v_x - label.get_width()/2, v_y - label.get_height()/2))
        node_i += 1

    screen.blit(edge_s, (0,0))
    screen.blit(node_s, (0,0))
    screen.blit(text_s, (0,0))

    # x_text = font.render(f"X Coordinates: {n_to_nth(x_coords_index)} eigenvector", True, (255, 255, 255))
    # y_text = font.render(f"Y Coordinates: {n_to_nth(y_coords_index)} eigenvector", True, (255, 255, 255))
    
    # screen.blit(x_text, (TEXT_PADDING, TEXT_PADDING))
    # screen.blit(y_text, (TEXT_PADDING, TEXT_PADDING*2 + x_text.get_height()))

def find_smallest_eigs(adj_matrix : np.array) -> Tuple[int]:
    diag = np.diag(np.sum(adj_matrix, axis=0))
    laplacian = np.subtract(diag, adj_matrix)
    eig_vals = np.linalg.eig(laplacian).eigenvalues

    lowest_is = [0,0]
    lowest_vals = [math.inf, math.inf]
    i = -1
    for e in eig_vals:
        i += 1
        # We round because a number that is very close to 0 will result in a bad graph.
        e_r = round(e, ROUND_DIGITS)

        if e_r <= 0: continue
        if e_r < lowest_vals[0]:
            lowest_is = [i, lowest_is[0]]
            lowest_vals = [eig_vals[i], lowest_vals[0]]
            continue
        if e_r < lowest_vals[1]:
            lowest_is[1] = i
            lowest_vals[1] = eig_vals[i]
    print(lowest_is[0])
    return lowest_is

def apply_mags(coords : List[List[int]], adj_matrix : np.array) -> List[List[int]]:
    edges = adj_to_edge_list(coords, adj_matrix)
    updated_nodes = []
    c_i = 0
    for c in coords:
        others = coords[0:c_i] + coords[c_i + 1:] + get_edge_points(edges, c)
        updated_nodes.append(apply_mag(c, others))
        c_i += 1
    return updated_nodes

# Returns list of edges, as start and end coordinates. 
def adj_to_edge_list(coords : List[List[int]], adj_matrix : np.array):
    edges = []
    for r_i in range(len(adj_matrix)):
        for c_i in range(len(adj_matrix)):
            if adj_matrix[r_i][c_i]:
                edges.append([coords[r_i], coords[c_i]])
    return edges

def get_edge_points(edges : List[List[List[int]]], point : List[int]):
    edge_points = []
    for e in edges:
        edge_points.append(calc_perp(e[0], e[1], point))
    print(edge_points)
    return edge_points

def calc_perp(p1 : List[int], p2 : List[int], p3 : List[int] ) -> List[int]:
    [x1, y1] = p1
    [x2, y2] = p2
    [x3, y3] = p3

    m = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else (y2 - y1) / 0.001
    b = y1 - (m * x1)
    x = ((x3 / m) + y3 - b) / (m + (1 / m)) if m != 0 else x1
    y = (m * x) + b

    low_x = x1 if x1 < x2 else x2
    high_x = x1 if x1 > x2 else x2
    low_y = y1 if y1 < y2 else y2
    high_y = y1 if y1 > y2 else y2

    if x < low_x: x = low_x
    if x > high_x: x = high_x
    if y < low_y: y = low_y
    if y > high_y: y = high_y
    return [x, y]

# Sets up graph for drawing, returns coordinates for nodes.
def setup(matrix : np.array):
    (x_coords_index, y_coords_index) =  find_smallest_eigs(matrix)
    return calc_graph_eig(matrix, x_coords_index, y_coords_index)

# pygame.display.set_caption("Graph Plotting with Eigenvectors")
# (WIDTH, HEIGHT) = (720, 720)
# screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
# mainclock = pygame.time.Clock()
# pygame.init()
# font = pygame.font.Font('freesansbold.ttf', 20)

# scale = SCALE
# x_offset = WIDTH/2
# y_offset = HEIGHT/2
# mouse_down = False
# prev_mouse_pos = (0,0)

# coords = setup(matrix)

# sim_mag = False

# while True:
#     for event in pygame.event.get():
#         match event.type:
#             case pygame.QUIT:
#                 exit(0)
#             case pygame.KEYDOWN:
#                 match event.key:
#                     case pygame.K_UP:
#                         y_coords_index += 1
#                         if y_coords_index >= len(matrix): y_coords_index = 0
#                         coords = calc_graph_eig(matrix, x_coords_index, y_coords_index)
#                     case pygame.K_DOWN:
#                         y_coords_index -= 1
#                         if y_coords_index < 0: y_coords_index = len(matrix) - 1
#                         coords = calc_graph_eig(matrix, x_coords_index, y_coords_index)
#                     case pygame.K_LEFT:
#                         x_coords_index -= 1
#                         if x_coords_index < 0: x_coords_index = len(matrix) - 1
#                         coords = calc_graph_eig(matrix, x_coords_index, y_coords_index)
#                     case pygame.K_RIGHT:
#                         x_coords_index += 1
#                         if x_coords_index >= len(matrix): x_coords_index = 0
#                         coords = calc_graph_eig(matrix, x_coords_index, y_coords_index)
#                     case pygame.K_r:
#                         matrix = generate_random_graph(RAND_MATRIX_SIZE)
#                         print(f"Generated random adjancency matrix of size {RAND_MATRIX_SIZE}: {matrix}")
#                         (x_coords_index,y_coords_index) = find_smallest_eigs(matrix)
#                         coords = calc_graph_eig(matrix, x_coords_index, y_coords_index)
#                     case pygame.K_e:
#                         coords = calc_graph_eig(matrix, x_coords_index, y_coords_index)
#                     case pygame.K_l:
#                         # coords = apply_mags(coords, matrix)
#                         coords = apply_mags_good(coords, diag.diagonal())
#                     case pygame.K_SPACE:
#                         sim_mag = not sim_mag
#             case pygame.VIDEORESIZE:
#                 WIDTH = screen.get_width()
#                 HEIGHT = screen.get_height()
#                 # coords = calc_graph_eig(matrix, x_coords_index, y_coords_index)                        
#             case pygame.MOUSEWHEEL:
#                 mul = 1
#                 if event.y < 0: mul = -1
#                 scroll_amt = mul * SCROLL_AMT * scale
#                 scale += scroll_amt
#                 if scale <= 1: scale = 1
#                 # coords = calc_graph_eig(matrix, x_coords_index, y_coords_index)
#             case pygame.MOUSEBUTTONDOWN:
#                 if event.button == 1:
#                     mouse_down = True
#                     prev_mouse_pos = pygame.mouse.get_pos()
#             case pygame.MOUSEBUTTONUP:
#                 if event.button == 1: mouse_down = False
#     if mouse_down:
#         pos = pygame.mouse.get_pos()
#         x_dist = pos[0] - prev_mouse_pos[0]
#         y_dist = pos[1] - prev_mouse_pos[1]
#         x_offset += x_dist
#         y_offset += y_dist

#         # coords = calc_graph_eig(matrix, x_coords_index, y_coords_index)
#         prev_mouse_pos = pos

#     if sim_mag:
#         # coords = apply_mags(coords, matrix)
#         coords = apply_mags_good(coords, diag.diagonal())

#     screen.fill((0,0,0))
#     draw_graph(coords, matrix, screen, x_offset, y_offset, scale)
#     pygame.display.flip()
#     mainclock.tick(60)