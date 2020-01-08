from core import TetrisBoard, Tetromino, Pentomino, ColorMap, RandomBag
from render import *
import pygame
from sys import exit
from random import choice
from math import sqrt


class GameWindow(object):
    def __init__(self, size: tuple):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(size)
        main_menu = Menu(self.screen)
        main_menu.run()


class Menu(object):
    def __init__(self, surface):
        self.surface = surface
        self.fps = 30
        self.tetris = Tetris(surface, Tetromino)
        self.pentris = Tetris(surface, Pentomino)
        self.background = pygame.sprite.Group()
        PygamePicture((-50, -50), self.background, "menu_background.png")
        self.tetris_start_butt = PygamePushButton((250, 300), (200, 70), 70,
                                                  ColorMap.WHITE, ColorMap.WHITE,
                                                  5, None, self.tetris.run, "START")
        self.pentris_start_butt = PygamePushButton((250, 400), (200, 70), 70,
                                                   ColorMap.WHITE, ColorMap.WHITE,
                                                   5, None, self.pentris.run, "START")
        self.menu_rect = PygameFillingRect(
            (200, 0), (300, 700), ColorMap.CLEAR, 0)
        self.logo = pygame.sprite.Group()
        PygamePicture((200, 0), self.logo, "logo.png", 0.25)

    def key_handler(self, key):
        pass

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.background.draw(self.surface)
        self.menu_rect.render(self.surface)
        self.logo.draw(self.surface)
        self.tetris_start_butt.render(self.surface)
        self.pentris_start_butt.render(self.surface)
        pygame.display.flip()

    def run(self):
        self.clock = pygame.time.Clock()
        while True:
            self.render()
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.tetris_start_butt.check_click(event.pos)
                    self.pentris_start_butt.check_click(event.pos)


class Tetris(object):
    DROP_EVENT = pygame.USEREVENT + 1

    def __init__(self, surface, piece_type):
        self.surface = surface
        self.board = TetrisBoard(ColorMap.CLEAR)
        self.piece_type = piece_type
        self.board_renderer = PygameTileField(
            (150, -900), self.board, (40, 40), ColorMap.CLEAR)
        self.curr_piece_renderer = PygameTetrisPiece(
            (150, -900), None, (40, 40))
        self.ghost_piece_renderer = PygameTetrisPiece(
            (150, -900), None, (40, 40))
        self.next_piece_renderer = PygameTetrisPiece(
            (600, 20), None, (20, 20))
        self.score_textbox = PygameTextBox(
            (10, 10), ColorMap.WHITE, 30, "0")
        self.level_textbox = PygameTextBox(
            (10, 30), ColorMap.WHITE, 30, "1")
        self.randomizer = RandomBag(piece_type.SHAPES)
        self.fps = 60
        # Debug
        self.lock_delay_textbox = PygameTextBox((100, 10), ColorMap.RED, 30)
        self.reset()

    def reset(self):
        self.board.reset()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.combo = 0
        self.total_lines = 0
        self.hold_piece = None

    def hold_piece(self):
        pass

    def key_handler(self, key):
        if key == pygame.K_RIGHT:
            self.board.horiz_move_curr_piece(True)
        elif key == pygame.K_LEFT:
            self.board.horiz_move_curr_piece(False)
        elif key in (pygame.K_UP, pygame.K_x):
            self.board.rotate_curr_piece(True)
        elif key == pygame.K_SPACE:
            self.board.hard_drop_curr_piece()
            self.lock_delay_frames = self.fps
        elif key == pygame.K_DOWN:
            self.board.drop_curr_piece()
        elif key in (pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_z):
            self.board.rotate_curr_piece(False)
        elif key in (pygame.K_ESCAPE, pygame.K_F1):
            print("pause")

    def score_counter(self, cleared_rows):
        if cleared_rows == 0:
            self.combo = 0
        elif cleared_rows == 1:
            self.score += 100 * self.level
            self.total_lines += 1
        elif cleared_rows == 2:
            self.score += 300 * self.level
            self.total_lines += 3
        elif cleared_rows == 3:
            self.score += 500 * self.level
            self.total_lines += 5
        elif cleared_rows == 4:
            self.score += 800 * self.level
            self.total_lines += 8
        if self.combo > 1:
            self.score += self.combo * self.level + 50 * self.level
        if self.total_lines >= self.level * 5:
            self.total_lines = 0
            self.level += 1
            pygame.time.set_timer(self.DROP_EVENT, self.level_delay())
        self.score_textbox.set_text(str(self.score))
        self.level_textbox.set_text(str(self.level))

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.board_renderer.render(self.surface, True)
        self.ghost_piece_renderer.render(self.surface)
        self.curr_piece_renderer.render(self.surface)
        self.next_piece_renderer.render(self.surface)
        self.score_textbox.render(self.surface, True)
        self.level_textbox.render(self.surface, True)
        # Debug
        self.lock_delay_textbox.render(self.surface, True)
        pygame.display.flip()

    def level_delay(self):
        return round(1000 / sqrt(self.level))

    def check_game_over(self):
        if self.game_over:
            print("Gameover")

    def choose_piece(self, coords):
        return self.piece_type(coords, *next(self.randomizer))

    def run(self):
        next_piece = self.choose_piece((0, 0))
        self.board.new_piece(self.choose_piece((4, 22)))
        self.clock = pygame.time.Clock()
        pygame.time.set_timer(self.DROP_EVENT, self.level_delay())
        self.lock_delay_frames = 0
        falling = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == self.DROP_EVENT:
                    self.board.drop_curr_piece()
                elif event.type == pygame.KEYDOWN:
                    self.key_handler(event.key)
            if self.board.check_lock_delay():
                self.lock_delay_frames += 1
            else:
                self.lock_delay_frames = 0
                falling = True
            if self.lock_delay_frames >= self.fps // 2:
                if not falling:
                    self.game_over = True
                self.lock_delay_frames = 0
                falling = False
                self.board.put_curr_piece()
                self.board.clear_filled_rows(self.score_counter)
                next_piece.move((4, 22))
                self.board.new_piece(next_piece)
                next_piece = self.choose_piece((0, 0))
            self.check_game_over()
            curr_piece = self.board.get_curr_piece()
            self.curr_piece_renderer.set_piece(curr_piece)
            ghost_piece = self.board.get_ghost_piece()
            self.ghost_piece_renderer.set_piece(ghost_piece)
            self.next_piece_renderer.set_piece(next_piece)
            # Debug
            self.lock_delay_textbox.set_text(str(self.lock_delay_frames))
            # Debug end
            self.render()
            self.clock.tick(self.fps)


class Pause(object):
    def __init__(self, surface):
        self.surface = surface

    def render(self):
        pass

    def run(self):
        pass


def main():
    window = GameWindow((700, 700))


if __name__ == "__main__":
    main()
