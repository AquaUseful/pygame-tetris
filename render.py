from typing import Iterable
import pygame
from core import TetrisPiece, TetrisBoard, ColorMap, Tetromino


class PygameTileField(object):
    def __init__(self, coords: tuple, field, tile_size: tuple, clear_val):
        self.coords = coords
        self.tile_size = tile_size
        self.field = field
        self.clear_val = clear_val

    def render(self, surface, render_border=False):
        for x, row in enumerate(self.field.get_tiles()):
            for y, tile_color in enumerate(row):
                if tile_color == self.clear_val:
                    continue
                tile_rect = pygame.Rect(x * self.tile_size[0] + self.coords[0],
                                        y * self.tile_size[1] +
                                        self.coords[1],
                                        self.tile_size[0], self.tile_size[1])
                print(tile_color)
                pygame.draw.rect(surface, tile_color, tile_rect)


class PygameTerisPiece(object):
    def __init__(self, coords: tuple, piece: TetrisPiece, tile_size: tuple):
        self.coords = coords
        self.piece = piece
        self.tile_size = tile_size

    def set_piece(self, piece: TetrisPiece):
        self.piece = piece

    def render(self, surface):
        color = self.piece.get_color()
        for x, y in self.piece.get_tiles_coords():
            tile_rect = pygame.Rect(x * self.tile_size[0] + self.coords[0],
                                    y * self.tile_size[1] + self.coords[1],
                                    self.tile_size[0], self.tile_size[1])
            pygame.draw.rect(surface, color, tile_rect)


class PygamePushButton(object):
    pass


b = TetrisBoard()
b.set_tile((3, 3), ColorMap.BLUE)
b.set_tile((3, 2), ColorMap.RED)
print(*b.tiles, sep="\n")
print()
b.clear_row(3)
print(*b.tiles, sep="\n")
pygame.init()
screen = pygame.display.set_mode((500, 500))
renderer = PygameTileField((10, 10), b, (10, 10), ColorMap.CLEAR)
renderer.render(screen)
pygame.display.flip()
input()
piece = Tetromino((0, 0), )
pygame.exit()