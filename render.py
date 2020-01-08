from typing import Iterable
import pygame
from core import TetrisPiece, TetrisBoard, ColorMap, Tetromino
import os


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    return image


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
                 size: tuple,
                 font_size: int,
                 color: pygame.Color,
                 font_color: pygame.Color,
                 border_width: int,
                 font,
                 action: callable,
                 text: str = ""):
        self.coords = coords
        self.size = size
        self.font_size = font_size
        self.color = color
        self.font_color = font_color
        self.border_width = border_width
        self.font = font
        self.action = action
        self.text = text
        self._prepare()

    def _prepare(self):
        self.rect = pygame.Rect(self.coords, self.size)
        font = pygame.font.Font(self.font, self.font_size)
        self.pygame_text = font.render(self.text, 1, self.font_color)
        text_w = self.pygame_text.get_width()
        text_h = self.pygame_text.get_height()
        self.text_coords = (self.coords[0] + self.size[0] // 2 - text_w // 2,
                            self.coords[1] + self.size[1] // 2 - text_h // 2)

    def render(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, self.border_width)
        surface.blit(self.pygame_text, self.text_coords)

    def check_click(self, mouse_coords):
        if self.rect.collidepoint(mouse_coords):
            self.action()

    def set_text(self, text: str):
        self.text = text

    def set_action(self, action: callable):
        self.action = action


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
        self.text = text

    def render(self, surface, render_border: bool = False) -> None:
        text = self.font.render(self.text, 1, self.color)
        surface.blit(text, self.coords)
        if render_border:
            rect = pygame.Rect(
                self.coords, (text.get_width(), text.get_height()))
            pygame.draw.rect(surface, ColorMap.WHITE, rect, 1)


class PygamePicture(pygame.sprite.Sprite):
    def __init__(self, coords, group, filename, scale: float = 1.0):
        super().__init__(group)
        self.image = load_image(filename)
        if scale != 1.0:
            x = round(self.image.get_width() * scale)
            y = round(self.image.get_height() * scale)
            self.image = pygame.transform.smoothscale(self.image, (x, y))
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]


class PygameFillingRect(object):
    def __init__(self, coords, size, color, border):
        self.coords = coords
        self.size = size
        self.color = color
        self.border = border
        self._prepare()

    def _prepare(self):
        self.rect = pygame.Rect(self.coords, self.size)

    def render(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, self.border)
