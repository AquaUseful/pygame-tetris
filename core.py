import pygame
from operator import add
from random import choice
from copy import copy


class ColorMap(object):
    CLEAR = pygame.Color("black")
    RED = pygame.Color("red")
    BLUE = pygame.Color("blue")
    GREEN = pygame.Color("green")
    YELLOW = pygame.Color("yellow")
    MAGENTA = pygame.Color("magenta")
    CYAN = pygame.Color("cyan")
    ORANGE = pygame.Color("orange")

    #CLEAR = "clear"
    #RED = "red"
    #BLUE = "blue"
    #GREEN = "green"
    #YELLOW = "yellow"
    #MAGENTA = "magenta"
    #CYAN = "cyan"
    #ORANGE = "orange"


class Shape(object):
    def __init__(self, tiles: tuple, bbox_size: tuple):
        self.tiles = tiles
        self.bbox_size = bbox_size

    def get_tiles(self) -> tuple:
        return self.tiles

    def calculate_rotation(self, rotation) -> tuple:
        box = [[False] * self.bbox_size[0] for _ in range(self.bbox_size[1])]
        for tile in self.tiles:
            box[tile[0]][tile[1]] = True
        for _ in range(rotation):
            box = tuple(zip(*box[::-1]))
        tiles = []
        for x, line in enumerate(box):
            for y, el in enumerate(line):
                if el:
                    tiles.append((x, y))
        return tuple(tiles)

    def get_bbox_size(self) -> int:
        return self.bbox_size


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

    def move(self, coords_delta: tuple) -> None:
        self.coords = tuple(map(add, self.coords, coords_delta))

    def get_tiles_coords(self) -> tuple:
        x, y = self.coords
        return tuple(map(lambda tile: (x + tile[0], y + tile[1]), self.shape.get_tiles()))

    def get_shape(self) -> Shape:
        return self.shape

    def get_color(self) -> pygame.Color:
        return self.color

    def __copy__(self):
        return TetrisPiece(self.coords, self.shape, self.color)

    def ghostify(self, alpha: int) -> None:
        pass


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
    def __init__(self, cols, rows):
        self.width = cols
        self.height = rows
        self.clear()

    def clear(self) -> None:
        self.tiles = [[ColorMap.CLEAR] *
                      self.height for _ in range(self.width)]

    def set_tile(self, coords: tuple, color: pygame.Color) -> None:
        if 0 <= coords[0] < self.width and 0 <= coords[1] < self.height:
            self.tiles[coords[0]][coords[1]] = color

    def get_tile(self, coords) -> pygame.Color:
        return self.tiles[coords[0]][coords[1]]

    def get_tiles(self) -> list:
        return self.tiles


class TetrisBoard(BaseTileField):
    def __init__(self, clear_val=ColorMap.CLEAR):
        super().__init__(10, 40)
        self.clear_val = clear_val
        self.reset()

    def reset(self) -> None:
        self.curr_piece = None
        self.clear()

    def clear_tile(self, coords: tuple) -> None:
        self.tiles[coords[0]][coords[1]] = ColorMap.CLEAR
        for y in range(coords[1], 0, -1):
            self.tiles[coords[0]][y] = self.tiles[coords[0]][y - 1]
        self.tiles[coords[0]][0] = ColorMap.CLEAR

    def clear_row(self, row: int) -> None:
        for x in range(self.width):
            self.clear_tile((x, row))

    def rotate_curr_piece(self, rotation) -> None:
        self.curr_piece.rotate(rotation)

    def move_curr_piece(self, coords_delta: tuple) -> None:
        self.curr_piece.move(coords_delta)

    def new_piece(self, piece_class) -> None:
        shape = choice(piece_class.SHAPES)
        self.curr_piece = piece_class((4, 20), shape)

    def put_curr_piece(self) -> None:
        for x, y in self.curr_piece.get_tiles():
            self.tiles[x][y] = self.curr_piece.get_color()
        self.curr_piece = None

    def drop_curr_piece(self) -> None:
        self.curr_piece.move((0, 1))

    def hard_drop_curr_piece(self) -> None:
        while self.curr_piece_can_drop():
            self.drop_curr_piece()

    def curr_piece_can_drop(self) -> None:
        temp_piece = copy(self.curr_piece)
        temp_piece.move(1, 0)
        return not (self.piece_collides_borders(temp_piece) or
                    self.piece_collides_tiles(temp_piece))

    def is_tile_empty(self, coords: tuple) -> bool:
        return self.tiles[coords[0]][coords[1]] == self.clear_val

    def is_tile_on_board(self, coords: tuple) -> bool:
        return 0 <= coords[0] < self.width and 0 <= coords[1] < self.width

    def piece_collides_tiles(self, piece: TetrisPiece) -> bool:
        return not all(map(lambda coords: self.is_tile_empty(coords),
                           piece.get_tiles_coords()))

    def piece_collides_borders(self, piece: TetrisPiece) -> bool:
        return not all(map(lambda coords: self.is_tile_on_board(coords),
                           piece.get_tiles_coords()))

    def is_row_full(self, row: int) -> bool:
        return not any(map(lambda col: self.is_tile_empty((row, col)),
                           range(self.width)))

    def clear_filled_rows(self, scorecounter: callable = None):
        cleared_rows = 0
        for row in range(self.height):
            if self.is_row_full(row):
                self.clear_row(row)
                cleared_rows += 1
        if scorecounter is not None:
            scorecounter(cleared_rows)

