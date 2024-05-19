import pygame
from typing import List, Tuple, Callable

# Scaling Axis enum
class AxisType:
    BOTH = 0
    X = 1
    Y = 2

# Helper function to calculate a child rect from parent coords and size.
# TODO: Maybe uneeded if only used in UIObject.draw()
def rect_from_p(c_x : float, c_y : float, c_width : float, c_height : float,
        p_x : float, p_y : float, p_width : float, p_height : float,
        scaling_axis : int, coord_axis : int) -> pygame.Rect:
    match scaling_axis:
        case AxisType.BOTH: 
            width_scalar = p_width
            height_scalar = p_height
        case AxisType.X:
            width_scalar = p_width
            height_scalar = p_width
        case AxisType.Y:
            width_scalar = p_height
            height_scalar = p_height
    match coord_axis:
        case AxisType.BOTH:
            x_scalar = p_width
            y_scalar = p_height
        case AxisType.X:
            x_scalar = p_width
            y_scalar = p_width
        case AxisType.Y:
            x_scalar = p_height
            y_scalar = p_height
    x : int = (c_x * x_scalar) + p_x
    y : int = (c_y * y_scalar) + p_y
    width : int = c_width * width_scalar
    height : int = c_height * height_scalar

    return pygame.Rect(x, y, width, height)

# def rect_from_p(child, parent) -> pygame.Rect:
#     return rect_from_p(child.x, child.y, child.width, child.height,
#         parent.x, parent.y, parent.width, parent.height, child.scaling_axis, child.coord_axis)

# Checks whether a single point is within a rectangle.
def point_in_bounds(x1 : int, y1 : int, w1 : int, h1 : int, x2 : int, y2 : int) -> bool:
    in_x : bool = (x2 > x1) and (x2 < (x1 + w1))
    in_y : bool = (y2 > y1) and (y2 < (y1 + h1))
    return in_x and in_y

def point_in_rect(rect : pygame.Rect, point : Tuple[int]) -> bool:
    return point_in_bounds(rect.x, rect.y, rect.width, rect.height, point[0], point[1])

# A drawable UI Object. Coords (x, y) and size (width, height) are percentages (0-1)
# of its parent widget.
# Scaling axis: can be BOTH (0), X (1), or Y (2). Determines what axis will be used for size scaling.
# BOTH means that x will be scaled by parent width, and y by parent height. X means that
# both will be scaled by width, and Y means both will be scaled by height. This is useful,
# for example, if you want an object to be a square no matter how the window resizes.
# Coord axis is the same but for coordinates.
class UIObject:
    def __init__(self, x : float = 0, y : float = 0,
            width : float = 0, height : float = 0, bg_color : Tuple[int] = (0, 0, 0),
            scaling_axis : int = AxisType.BOTH, coord_axis : int = AxisType.BOTH) -> None:
        self.x : float = x
        self.y : float = y
        self.width : float = width
        self.height : float = height
        self.bg_color : Tuple[int] = bg_color
        self.scaling_axis : int = scaling_axis
        self.coord_axis : int = coord_axis

        # Whether the object has changed since last frame and we need to re-draw it.
        self.changed : bool = True

        self.clickable : bool = False   # So that we do not have to check for type Clickable.
    
    # Draws the object on the provided screen. The parent coords and size are in pixels,
    # not percentages.
    def draw(self, surface : pygame.Surface, p_x : float = 0, p_y : float = 0,
            p_width : float = 0, p_height : float = 0) -> None:
        if self.changed:
            rect = rect_from_p(self.x, self.y, self.width, self.height,
                p_x, p_y, p_width, p_height, scaling_axis = self.scaling_axis, coord_axis=self.coord_axis)
            pygame.draw.rect(surface, self.bg_color, rect)
            self.changed = False
    
    def set_all_changed(self, changed : bool = True):
        self.changed = changed
    
    def activate_click(self, pos : Tuple[int], p_rect : pygame.Rect):
        pass

# A type of UIObject that has other UIObjects.
class Widget(UIObject):
    def __init__(self, x: float = 0, y: float = 0,
            width: float = 0, height: float = 0,
            bg_color : Tuple[int] = (0, 0, 0),
            objects : List[UIObject] = [],
            scaling_axis : int = AxisType.BOTH,
            coord_axis : int = AxisType.BOTH) -> None:
        super().__init__(x, y, width, height, bg_color, scaling_axis, coord_axis)
        self.objects = objects
    def draw(self, surface : pygame.Surface, p_x : float = 0, p_y : float = 0,
            p_width : float = 0, p_height : float = 0) -> None:
        rect = rect_from_p(self.x, self.y, self.width, self.height,
            p_x, p_y, p_width, p_height, scaling_axis = self.scaling_axis, coord_axis=self.coord_axis)
        if self.changed:
            # TODO: bad to not call super().draw? 
            pygame.draw.rect(surface, self.bg_color, rect)
            self.changed = False
        for o in self.objects:
            o.draw(surface, rect.x, rect.y, rect.width, rect.height)

    # Recursively sets this object's and all of its children's changed.
    def set_all_changed(self, changed : bool = True):
        self.changed = changed
        for o in self.objects:
            o.set_all_changed(changed)
    
    def activate_click(self, pos : Tuple[int], p_rect : pygame.Rect):
        new_p_rect = rect_from_p(self.x, self.y, self.width, self.height,
            p_rect.x, p_rect.y, p_rect.width, p_rect.height, self.scaling_axis, self.coord_axis)
        for o in self.objects:
            rect = rect_from_p(o.x, o.y, o.width, o.height,
                new_p_rect.x, new_p_rect.y, new_p_rect.width, new_p_rect.height, o.scaling_axis, o.coord_axis)
            if point_in_rect(rect, pos):
                o.activate_click(pos, new_p_rect)

# A widget that (should) fill the entire window and be at (0, 0).
# Its width and height are in pixels, NOT percentages.
# Can be switched to/from.
class Screen(Widget):
    def __init__(self, x: float = 0, y: float = 0, width: float = 0,
            height: float = 0,
            bg_color : Tuple[int] = (0, 0, 0),
            objects: List[UIObject] = [],
            scaling_axis : int = AxisType.BOTH,
            coord_axis : int = AxisType.BOTH) -> None:
        super().__init__(x, y, width, height, bg_color, objects, scaling_axis, coord_axis)
    def draw(self, surface : pygame.Surface):
        if self.changed:
            # Doesn't use Widget's draw because its coords are in pixels,
            # might be bad to do it this way.
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(surface, self.bg_color, rect)
            self.changed = False
        for o in self.objects:
            o.draw(surface, self.x, self.y, self.width, self.height)
    def activate_click(self, pos: Tuple[int]):
        new_p_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for o in self.objects:
            rect = rect_from_p(o.x, o.y, o.width, o.height,
                new_p_rect.x, new_p_rect.y, new_p_rect.width, new_p_rect.height, o.scaling_axis, o.coord_axis)
            if point_in_rect(rect, pos):
                o.activate_click(pos, new_p_rect)
# ________________________________
# ----- More Objects/Widgets -----
# ________________________________

class Clickable(Widget):
    def __init__(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0,
            bg_color: Tuple[int] = (0, 0, 0), objects: List[UIObject] = [],
            scaling_axis: int = AxisType.BOTH, coord_axis: int = AxisType.BOTH,
            on_click: Callable = lambda : print(f"Hello World")) -> None:
        super().__init__(x, y, width, height, bg_color, objects, scaling_axis, coord_axis)
        self.on_click : Callable = lambda : print(f"Hello World from id {id(self)}")

        self.clickable = True

    def activate_click(self, pos : Tuple[int], p_rect : pygame.Rect):
        self.on_click()
        super().activate_click(pos, p_rect)

# TODO: make text size resize to fit within its rect (as an option).
# But before this, probably need to keep pixel values and update them for all objs.
# TODO: text centering
class Text(UIObject):
    def __init__(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0,
            bg_color: Tuple[int] = (0, 0, 0), scaling_axis: int = AxisType.BOTH,
            coord_axis: int = AxisType.BOTH, text : str = "", font : pygame.font = None) -> None:
        super().__init__(x, y, width, height, bg_color, scaling_axis, coord_axis)

        self.text : str = text
        self.font : pygame.font = font
    def draw(self, surface : pygame.Surface, p_x : float = 0, p_y : float = 0,
            p_width : float = 0, p_height : float = 0) -> None:
        if self.changed:
            rect = rect_from_p(self.x, self.y, self.width, self.height,
                p_x, p_y, p_width, p_height, scaling_axis = self.scaling_axis, coord_axis=self.coord_axis)
            pygame.draw.rect(surface, self.bg_color, rect)
            text_rect = self.font.render(self.text, False, 1)
            surface.blit(text_rect, (rect.x, rect.y))
            self.changed = False

# Clickable with text
class Button(Clickable):
    def __init__(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0,
            bg_color: Tuple[int] = (0, 0, 0), objects: List[UIObject] = [],
            scaling_axis: int = AxisType.BOTH, coord_axis: int = AxisType.BOTH,
            on_click: Callable = lambda : print(f"Hello World"),
            text : str ="", font : pygame.font = None) -> None:
        super().__init__(x, y, width, height, bg_color, objects, scaling_axis, coord_axis, on_click)

        self.text : str = text
        self.font : pygame.font = font
        # TODO: do NOT use self.bg_color, need to have an option for no color.
        self.text_object : Text = Text(0, 0, 1, 1, self.bg_color, text = self.text, font = self.font)
        self.objects.append(self.text_object)