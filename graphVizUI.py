from typing import List, Tuple
from pyUI import *
from graph import Graph
from pyUI import AxisType, UIObject
import numpy as np

class GraphWidget(UIObject):
    def __init__(self, x : float = 0, y : float = 0, width : float = 0,height : float = 0,
            bg_color : Tuple[int] = (0, 0, 0), scaling_axis : int = AxisType.BOTH,
            coord_axis : int = AxisType.BOTH, graph : Graph = None,
            vertex_radius : int = 10, vertex_color : Tuple[int] = (255, 0, 0),
            edge_width : int = 1, edge_color : Tuple[int] = (255, 255, 255)) -> None:
        super().__init__(x, y, width, height, bg_color, scaling_axis, coord_axis)
        self.graph : Graph = graph
        self.vertex_radius : int = vertex_radius
        self.vertex_color : Tuple[int] = vertex_color
        self.edge_width : int = edge_width
        self.edge_color : Tuple[int] = edge_color

        # Eigenvector coords (from -1 to 1)
        self.vertex_coords : np.array = np.zeros((2, self.graph.size))
    
    def draw(self, surface : pygame.Surface, p_x : float = 0, p_y : float = 0,
            p_width : float = 0, p_height : float = 0) -> None:
        if self.graph.changed: self.changed = True  # TODO: Kinda jank
        if self.changed:
            if self.graph.changed:
                # We need to calculate new coords
                self.vertex_coords = self.graph.get_coords()
                self.graph.changed = False
            
            # Background
            rect = rect_from_p(self.x, self.y, self.width, self.height,
                p_x, p_y, p_width, p_height, scaling_axis = self.scaling_axis, coord_axis=self.coord_axis)
            pygame.draw.rect(surface, self.bg_color, rect)

            # Convert all coordinates to screen space
            coords = []
            i : int = 0
            for (x1, y1) in self.vertex_coords:
                # Normalize x, y from -1 to 1 to 0 to 1.
                x1 = (x1 + 1) / 2
                y1 = (y1 + 1) / 2

                # Scale and offset to UIObject
                x = (x1 * self.width * p_width) + (p_width * self.x) + p_x
                y = (y1 * self.height * p_height) + (p_height * self.y) + p_y

                coords.append([x, y])
                i += 1

            # Draw graph
            # Keep seperate surfaces so that the vertices are always drawn over the edges.
            vertex_surf = pygame.Surface((p_width, p_height), pygame.SRCALPHA)
            vertex_surf.fill((0, 0, 0, 0))

            edge_surf = pygame.Surface((p_width, p_height), pygame.SRCALPHA)
            edge_surf.fill((0, 0, 0, 0))
            
            vertex_index : int = 0
            for (x1, y1) in coords:
                # Draw edges
                # TODO: Draws duplicate edges (exactly twice as many)
                edge_index : int = 0
                for c in self.graph.get_connections(vertex_index):
                    if c:
                        (x2, y2) = coords[edge_index]
                        pygame.draw.line(edge_surf, self.edge_color, (x1, y1), (x2, y2), self.edge_width)
                    edge_index += 1

                # Draw vertex
                pygame.draw.circle(vertex_surf, self.vertex_color, (x1, y1), self.vertex_radius)
                vertex_index += 1

            surface.blit(edge_surf, (0, 0))
            surface.blit(vertex_surf, (0, 0))
            self.changed = False