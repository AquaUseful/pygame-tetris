import pygame
from operator import add
from random import shuffle
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
    WHITE = pygame.Color("white")
    GHOST = pygame.Color("darkgrey")

    # CLEAR = "clear"
    # RED = "red"
    # BLUE = "blue"
    # GREEN = "green"
    # YELLOW = "yellow"
    # MAGENTA = "magenta"
    # CYAN = "cyan"
    # ORANGE = "orange"


class Shape(object):
    def __init__(self, tiles: tuple, bbox_size: tuple, kick_data: dict):
        self.tiles = tiles
        self.bbox_size = bbox_size
        self.kick_data = kick_data

    def get_tiles(self) -> tuple:
        return self.tiles

    def calculate_rotation(self, rotation) -> tuple:
        box = [[False] * self.bbox_size[0] for _ in range(self.bbox_size[1])]
        for tile in self.tiles:
            box[tile[0]][tile[1]] = True
        for _ in range(4 - rotation):
            box = tuple(zip(*box[::-1]))
        tiles = []
        for x, line in enumerate(box):
            for y, el in enumerate(line):
                if el:
                    tiles.append((x, y))
        return tuple(tiles)

    def get_bbox_size(self) -> int:
        return self.bbox_size

    def get_kick_data(self, old_rot: int, new_rot: int) -> tuple:
        return self.kick_data[(old_rot, new_rot)]


class TetrisPiece(object):
    def __init__(self,
                 coords: tuple,
                 shape: Shape,
                 color: pygame.Color,
                 rotation=0):
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

    def get_rotation(self) -> int:
        return self.rotation

    def move(self, coords_delta: tuple) -> None:
        self.coords = tuple(map(add, self.coords, coords_delta))

    def get_tiles_coords(self) -> tuple:
        x, y = self.coords
        return tuple(map(lambda tile: (x + tile[0], y + tile[1]),
                         self.shape.calculate_rotation(self.rotation)))

    def get_shape(self) -> Shape:
        return self.shape

    def get_color(self) -> pygame.Color:
        return self.color

    def __copy__(self):
        return TetrisPiece(self.coords,
                           self.shape,
                           self.color,
                           self.rotation)

    def ghostify(self) -> None:
        self.color = ColorMap.GHOST

    def get_kick_data(self, old_rot, new_rot):
        return self.shape.get_kick_data(old_rot, new_rot)


class Tetromino(TetrisPiece):
    wall_kicks = {
        (0, 1): ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, 2)),
        (1, 0): ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
        (1, 2): ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
        (2, 1): ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)),
        (2, 3): ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
        (3, 2): ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
        (3, 0): ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
        (0, 3): ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2))
    }
    L_SH = (Shape(((0, 1), (1, 1), (2, 1), (2, 0)), (3, 3), wall_kicks),
            ColorMap.ORANGE)
    J_SH = (Shape(((0, 0), (0, 1), (1, 1), (2, 1)), (3, 3), wall_kicks),
            ColorMap.BLUE)
    O_SH = (Shape(((0, 0), (0, 1), (1, 0), (1, 1)), (2, 2), wall_kicks),
            ColorMap.YELLOW)
    T_SH = (Shape(((0, 1), (1, 1), (2, 1), (1, 0)), (3, 3), wall_kicks),
            ColorMap.MAGENTA)
    S_SH = (Shape(((1, 0), (0, 1), (1, 1), (2, 0)), (3, 3), wall_kicks),
            ColorMap.GREEN)
    Z_SH = (Shape(((0, 0), (1, 0), (1, 1), (2, 1)), (3, 3), wall_kicks),
            ColorMap.RED)
    wall_kicks = {
        (0, 1): ((0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)),
        (1, 0): ((0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)),
        (1, 2): ((0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)),
        (2, 1): ((0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)),
        (2, 3): ((0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)),
        (3, 2): ((0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)),
        (3, 0): ((0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)),
        (0, 3): ((0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1))
    }
    I_SH = (Shape(((0, 1), (1, 1), (2, 1), (3, 1)), (4, 4), wall_kicks),
            ColorMap.CYAN)
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

    def get_size(self):
        return (self.width, self.height)


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
        temp_piece = copy(self.curr_piece)
        curr_rot = temp_piece.get_rotation()
        temp_piece.rotate(rotation)
        new_rot = temp_piece.get_rotation()
        for kick in temp_piece.get_kick_data(curr_rot, new_rot):
            if self.piece_can_move(temp_piece, kick):
                self.curr_piece.rotate(rotation)
                self.move_curr_piece(kick)
                break

    def move_curr_piece(self, coords_delta: tuple) -> None:
        self.curr_piece.move(coords_delta)

    def horiz_move_curr_piece(self, right: bool) -> None:
        if right:
            if self.piece_can_move(self.curr_piece, (1, 0)):
                self.move_curr_piece((1, 0))
        else:
            if self.piece_can_move(self.curr_piece, (-1, 0)):
                self.move_curr_piece((-1, 0))

    def new_piece(self, piece):
        self.curr_piece = piece

    def put_curr_piece(self) -> None:
        for x, y in self.curr_piece.get_tiles_coords():
            self.tiles[x][y] = self.curr_piece.get_color()
        self.curr_piece = None

    def drop_curr_piece(self) -> None:
        if self.piece_can_move(self.curr_piece, (0, 1)):
            self.move_curr_piece((0, 1))

    def hard_drop_curr_piece(self) -> None:
        while self.piece_can_move(self.curr_piece, (0, 1)):
            self.curr_piece.move((0, 1))

    def piece_can_move(self, piece, coords_delta: tuple):
        temp_piece = copy(piece)
        temp_piece.move(coords_delta)
        return not (self.piece_collides_borders(temp_piece) or
                    self.piece_collides_tiles(temp_piece))

    def is_tile_empty(self, coords: tuple) -> bool:
        return self.tiles[coords[0]][coords[1]] == self.clear_val

    def is_tile_on_board(self, coords: tuple) -> bool:
        return 0 <= coords[0] < self.width and 0 <= coords[1] < self.height

    def piece_collides_tiles(self, piece: TetrisPiece) -> bool:
        return not all(map(lambda coords: self.is_tile_empty(coords),
                           piece.get_tiles_coords()))

    def piece_collides_borders(self, piece: TetrisPiece) -> bool:
        return not all(map(lambda coords: self.is_tile_on_board(coords),
                           piece.get_tiles_coords()))

    def is_row_full(self, row: int) -> bool:
        return not any(map(lambda x: self.is_tile_empty((x, row)), range(self.width)))

    def clear_filled_rows(self, scorecounter: callable = None):
        cleared_rows = 0
        for row in range(self.height):
            if self.is_row_full(row):
                self.clear_row(row)
                cleared_rows += 1
        if scorecounter is not None:
            scorecounter(cleared_rows)

    def get_curr_piece(self):
        return self.curr_piece

    def get_ghost_piece(self):
        ghost = copy(self.curr_piece)
        ghost.ghostify()
        while self.piece_can_move(ghost, (0, 1)):
            ghost.move((0, 1))
        return ghost

    def check_lock_delay(self):
        return not self.piece_can_move(self.curr_piece, (0, 1))

class RandomBag(object):
    def __init__(self, variants):
        self.variants = variants
        self.shuffle()

    def shuffle(self):
        self.seq = list(self.variants)
        shuffle(self.seq)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.seq:
            self.shuffle()
        return self.seq.pop()

    def get_sequence(self):
        return self.seq