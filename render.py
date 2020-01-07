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
                pygame.draw.rect(surface, tile_color, tile_rect)
        if render_border:
            field_size = self.field.get_size()
            border = pygame.Rect(self.coords,
                                 (field_size[0] * self.tile_size[0],
                                  field_size[1] * self.tile_size[1]))
            pygame.draw.rect(surface, ColorMap.WHITE, border, 1)


class PygameTetrisPiece(object):
    def __init__(self, coords: tuple, piece: TetrisPiece, tile_size: tuple):
        self.coords = coords
        self.piece = piece
        self.tile_size = tile_size

    def set_piece(self, piece: TetrisPiece):
        self.piece = piece

    def render(self, surface) -> None:
        if self.piece is None:
            return
        color = self.piece.get_color()
        for x, y in self.piece.get_tiles_coords():
            tile_rect = pygame.Rect(x * self.tile_size[0] + self.coords[0],
                                    y * self.tile_size[1] + self.coords[1],
                                    self.tile_size[0], self.tile_size[1])
            pygame.draw.rect(surface, color, tile_rect)


class PygamePushButton(object):
    def __init__(self,
                 coords: tuple,
                 color,
                 font_color):
        pass


class PygameTextBox(object):
    def __init__(self,
                 coords: tuple,
                 color,
                 font_size: int,
                 text: str = "",
                 font=None):
        self.coords = coords
        self.font = pygame.font.Font(font, font_size)
        self.color = color
        self.text = text

    def set_text(self, text: str) -> None:
        self.text = str(text)

    def render(self, surface, render_border: bool = False) -> None:
        text = self.font.render(self.text, 1, self.color)
        surface.blit(text, self.coords)
        if render_border:
            rect = pygame.Rect(
                self.coords, (text.get_width(), text.get_height()))
            pygame.draw.rect(surface, ColorMap.WHITE, rect, 1)
