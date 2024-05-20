from typing import List, Tuple
from pyUI import *
from graph import Graph, EigMode
from pyUI import AxisType, UIObject
import numpy as np

class GraphUIObject(UIObject):
    def __init__(self, x : float = 0, y : float = 0, width : float = 0, height : float = 0,
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

# Plots lists of numbers
class Plotter(UIObject):
    def __init__(self, x : float = 0, y : float = 0, width : float = 0, height : float = 0,
            bg_color : Tuple[int] = (0, 0, 0), scaling_axis : int = AxisType.BOTH,
            coord_axis : int = AxisType.BOTH, data : List[float] = [],
            line_color : Tuple[int] = (255, 255, 255), point_color : Tuple[int] = (150, 150, 255),
            line_width : int = 1, point_radius : int = 5,
            draw_lines : bool = True, draw_points : bool = False) -> None:
        super().__init__(x, y, width, height, bg_color, scaling_axis, coord_axis)

        self.line_color : Tuple[int] = line_color
        self.point_color : Tuple[int] = point_color
        self.line_width : int = line_width
        self.point_radius : int = point_radius
        self.draw_lines : bool = draw_lines
        self.draw_points : bool = draw_points

        self.data : List[float] = data

    def draw(self, surface : pygame.Surface, p_x : float = 0, p_y : float = 0,
            p_width : float = 0, p_height : float = 0) -> None:
        if self.changed:
            # Background
            rect = rect_from_p(self.x, self.y, self.width, self.height,
                p_x, p_y, p_width, p_height, scaling_axis = self.scaling_axis, coord_axis=self.coord_axis)
            pygame.draw.rect(surface, self.bg_color, rect)

            scale_x = rect.width / len(self.data)
            scale_y = rect.height / (abs(max(self.data)) + abs(min(self.data)))
            y_offset = min(self.data) * scale_y

            # Draw plot
            line_surf = pygame.Surface((p_width, p_height), pygame.SRCALPHA)
            line_surf.fill((0, 0, 0, 0))

            point_surf = pygame.Surface((p_width, p_height), pygame.SRCALPHA)
            point_surf.fill((0, 0, 0, 0))

            i = 0
            prev_pos = (0, 0)
            for v in self.data:
                x = (int) (i * scale_x)
                y = rect.height - (int) ((v * scale_y) - y_offset)
                if self.draw_lines: pygame.draw.line(line_surf, self.line_color, prev_pos, (x, y), self.line_width)
                if self.draw_points: pygame.draw.circle(point_surf, self.point_color, (x, y), self.point_radius)
                prev_pos = (x, y)
                i += 1
            surface.blit(line_surf, (rect.x, rect.y))
            surface.blit(point_surf, (rect.x, rect.y))
            self.changed = False

# Plots the sprectum of the eigenvalues of a graph.
class Spectrum(Widget):
    ROUNDING : int = 2      # Number of digits to round to
    def __init__(self, x : float = 0, y : float = 0, width : float = 0, height : float = 0,
            bg_color : Tuple[int] = (0, 0, 0), objects : List[UIObject] = [],
            scaling_axis : int = AxisType.BOTH, coord_axis : int = AxisType.BOTH,
            graph : Graph = None, line_color : Tuple[int] = (255, 255, 255),
            point_color : Tuple[int] = (150, 150, 255),
            line_width : int = 1, point_radius : int = 5,
            draw_lines : bool = True, draw_points : bool = False,
            eig_mode : int = EigMode.ADJ, plotter_padding : float = 0.1,
            font : pygame.font.Font = None) -> None:
        super().__init__(x, y, width, height, bg_color, objects, scaling_axis, coord_axis)

        self.graph : Graph = graph
        self.eig_mode : int = eig_mode
        self.plotter_padding : float = plotter_padding
        self.font : pygame.font = font

        # TODO: Again, need to fix bg color not transparent.
        self.plotter : Plotter = Plotter(plotter_padding, plotter_padding,
            1 - (plotter_padding * 2), 1 - (plotter_padding * 2), self.bg_color,
            line_color = line_color, point_color = point_color, line_width = line_width,
            point_radius = point_radius, draw_lines = draw_lines,
            draw_points = draw_points)
        self.plotter.data = self.graph.get_eig_vals(self.eig_mode)
        self.objects.append(self.plotter)

        data_max : float = max(self.plotter.data)
        data_min : float = min(self.plotter.data)
        data_mid : float = (data_max + data_min) / 2

        self.max_text : Text = Text(self.plotter_padding / 4, plotter_padding,
            bg_color = self.bg_color, text = str(round(data_max, self.ROUNDING)),
            font = self.font)
        self.objects.append(self.max_text)

        self.min_text : Text = Text(self.plotter_padding / 4, 1 - plotter_padding,
            bg_color = self.bg_color, text = str(round(data_min, self.ROUNDING)),
            font = self.font)
        self.objects.append(self.min_text)

        # Dont have text for 0 if the min or the max is 0.
        if round(data_max, self.ROUNDING) != 0 and round(data_min, self.ROUNDING) != 0:
            self.zero_text : Text = Text(self.plotter_padding / 4,
                map_range(0, data_min, data_max, self.plotter_padding,
                    1 - self.plotter_padding),
                bg_color = self.bg_color, text = "0", font = self.font)
            self.objects.append(self.zero_text)
        else:
            self.zero_text = None

        # Dont have mid text if the mid is 0, max, or min.
        if (round(data_max, self.ROUNDING) != round(data_mid, self.ROUNDING)
                and round(data_min, self.ROUNDING) != round(data_mid, self.ROUNDING)
                and round(data_mid, self.ROUNDING) != 0):
            self.mid_text : Text = Text(self.plotter_padding / 4,
                map_range(data_mid, data_min, data_max, self.plotter_padding,
                    1 - self.plotter_padding),
                bg_color = self.bg_color, text = str(round(data_mid, self.ROUNDING)), font = self.font)
            self.objects.append(self.mid_text)
        else:
            self.mid_text = None

# Helper function for mapping a number from one range to another
def map_range(x, min1, max1, min2, max2):
    r1 = max1 - min1
    r2 = max2 - min2
    scale = abs(r2 / r1)
    return ((x - min1) * scale) + min2