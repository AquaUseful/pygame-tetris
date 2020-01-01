import pygame


class ColorMap(object):
    CLEAR = pygame.Color("black")
    RED = pygame.Color("red")
    BLUE = pygame.Color("blue")
    GREEN = pygame.Color("green")
    YELLOW = pygame.Color("yellow")
    MAGENTA = pygame.Color("magenta")
    CYAN = pygame.Color("cyan")
    ORANGE = pygame.Color("orange")


class Shape(object):
    def __init__(self, tiles: tuple, bbox_size: tuple):
        self.tiles = tiles
        self.bbox_size = bbox_size

    def get_tiles(self) -> tuple:
        return self.tiles

    def calculate_rotation(self, rotation) -> tuple:
        box = [[False] * self.bbox_size[0] for _ in range(self.bbox_size[1])]
        for tile in self.tiles:
            box[tile[1]][tile[0]] = True
        for _ in range(rotation):
            box = tuple(zip(*box[::-1]))
        tiles = []
        for x, line in enumerate(box):
            for y, el in enumerate(line):
                if el:
                    tiles.append((y, x))
        return tuple(tiles)


class TetrisPiece(object):
    def __init__(self, coords: tuple, shape, color: pygame.Color):
        self.coords = coords
        self.shape = shape
        self.color = color
        self.rotation = rotation

    def draw(self, field) -> None:
        for x, y in self.shape.calculate_rotation(self.rotation):
            field.set_tile((self.shape[0] + x, self.shape[1] + y), self.color)

    def rotate(self, direction: bool) -> None:
        if direction:
            self.rotation = (self.rotation + 1) % 4
        else:
            self.rotation = (self.rotation - 1) % 4


class Tetromino(TetrisPiece):
    L_SH = (Shape(((0, 1), (1, 1), (2, 1), (2, 0)), (3, 3)), ColorMap.ORANGE)
    J_SH = (Shape(((0, 0), (1, 1), (2, 1), (2, 0)), (3, 3)), ColorMap.BLUE)
    O_SH = (Shape(((0, 0), (0, 1), (1, 0), (1, 1)), (2, 2)), ColorMap.YELLOW)
    T_SH = (Shape(((0, 1), (1, 1), (2, 1), (1, 0)), (3, 3)), ColorMap.MAGENTA)
    S_SH = (Shape(((0, 0), (1, 1), (2, 1), (2, 0)), (3, 3)), ColorMap.GREEN)
    Z_SH = (Shape(((0, 0), (1, 1), (2, 1), (2, 0)), (3, 3)), ColorMap.RED)
    I_SH = (Shape(((0, 1), (1, 1), (2, 1), (3, 1)), (4, 4)), ColorMap.CYAN)
    SHAPES = (L_SH, J_SH, O_SH, T_SH, S_SH, Z_SH, I_SH)


class Pentomino(TetrisPiece):
    pass


class BaseTileField(object):
    def __init__(self):
        self.rows = []
        self.width = 0
        self.height = 0

    def set_size(self, cols: int, rows: int) -> None:
        self.width = cols
        self.height = rows
        self.clear()

    def clear(self) -> None:
        self.rows = [[ColorMap.CLEAR] * self.width for _ in range(self.height)]

    def set_tile(self, coords: tuple, color: pygame.Color) -> None:
        if 0 <= coords[0] < self.width and 0 <= coords[1] < self.height:
            self.rows[coords[1]][coords[0]] = color
