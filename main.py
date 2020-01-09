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
        self.clock = pygame.time.Clock()

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
        while True:
            print("menu")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.tetris_start_butt.check_click(event.pos)
                    self.pentris_start_butt.check_click(event.pos)
            self.render()
            self.clock.tick(self.fps)


class Tetris(object):
    DROP_EVENT = pygame.USEREVENT + 1

    def __init__(self, surface, piece_type):
        self.surface = surface
        self.pause_screen = Pause(surface, self)
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
        self.hold_piece_renderer = PygameTetrisPiece(
            (600, 100), None, (20, 20))
        self.score_textbox = PygameTextBox(
            (10, 10), ColorMap.WHITE, 30, "0")
        self.level_textbox = PygameTextBox(
            (10, 30), ColorMap.WHITE, 30, "1")
        self.randomizer = RandomBag(piece_type.SHAPES)
        self.fps = 60
        # Debug
        self.lock_delay_textbox = PygameTextBox((100, 10), ColorMap.RED, 30)
        # Debug end
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.board.reset()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.combo = 0
        self.total_lines = 0
        self.randomizer.shuffle()
        self.hold_piece = None
        self.next_piece = self.choose_piece()
        self.hold_used = False
        self.exit = False
        self.restart = False
        self.board.new_piece(self.choose_piece())
        pygame.time.set_timer(self.DROP_EVENT, self.level_delay())
        self.lock_delay_frames = 0

    def hold(self):
        if self.hold_used:
            return
        self.hold_used = True
        if self.hold_piece is None:
            self.hold_piece = self.board.get_curr_piece()
            self.board.new_piece(self.next_piece)
            self.next_piece = self.choose_piece()
        else:
            new_hold_piece = self.board.get_curr_piece()
            self.board.new_piece(self.hold_piece)
            self.hold_piece = new_hold_piece
        self.hold_piece.set_coords((0, 0))
        self.hold_piece_renderer.set_piece(self.hold_piece)

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
            self.pause_screen.run()
        elif key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_c):
            self.hold()

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
        self.hold_piece_renderer.render(self.surface)
        self.score_textbox.render(self.surface, True)
        self.level_textbox.render(self.surface, True)
        # Debug
        self.lock_delay_textbox.render(self.surface, True)
        pygame.display.flip()

    def level_delay(self):
        return round(1000 / sqrt(self.level))

    def choose_piece(self):
        return self.piece_type((0, 0), *next(self.randomizer))

    def run(self):
        self.reset()
        falling = False
        while True:
            print("game")
            if self.exit:
                break
            elif self.restart:
                self.reset()
            elif self.game_over:
                exit()
                break
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
                falling = False
                self.hold_used = False
                self.lock_delay_frames = 0
                self.board.put_curr_piece()
                self.board.clear_filled_rows(self.score_counter)
                self.board.new_piece(self.next_piece)
                self.next_piece = self.choose_piece()
            curr_piece = self.board.get_curr_piece()
            self.curr_piece_renderer.set_piece(curr_piece)
            ghost_piece = self.board.get_ghost_piece()
            self.ghost_piece_renderer.set_piece(ghost_piece)
            self.next_piece_renderer.set_piece(self.next_piece)
            # Debug
            self.lock_delay_textbox.set_text(str(self.lock_delay_frames))
            # Debug end
            self.render()
            self.clock.tick(self.fps)

    def set_exit_flag(self):
        self.exit = True

    def set_restart_flag(self):
        self.restart = True


class Pause(object):
    def __init__(self, surface, game_field):
        self.surface = surface
        self.game_field = game_field
        self.resume_butt = PygamePushButton((250, 300), (200, 70), 70,
                                            ColorMap.WHITE, ColorMap.WHITE,
                                            5, None, self.resume_game, "Resume")
        self.exit_butt = PygamePushButton((250, 400), (200, 70), 70,
                                          ColorMap.WHITE, ColorMap.WHITE,
                                          5, None, self.exit_game, "Exit")
        self.restart_butt = PygamePushButton((250, 500), (200, 70), 70,
                                             ColorMap.WHITE, ColorMap.WHITE,
                                             5, None, self.restart_game, "Restart")
        self.fps = 30
        self.clock = pygame.time.Clock()

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.resume_butt.render(self.surface)
        self.exit_butt.render(self.surface)
        self.restart_butt.render(self.surface)
        pygame.display.flip()

    def resume_game(self):
        self.exit = True

    def exit_game(self):
        self.exit_game = True
        self.exit = True

    def restart_game(self):
        self.restart_game = True
        self.exit = True

    def reset(self):
        self.restart_game = False
        self.exit_game = False
        self.exit = False

    def run(self):
        self.reset()
        while True:
            print("paused")
            if self.exit:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.resume_butt.check_click(event.pos)
                    self.exit_butt.check_click(event.pos)
                    self.restart_butt.check_click(event.pos)
            self.render()
            self.clock.tick(self.fps)
        if self.exit_game:
            self.game_field.set_exit_flag()
        elif self.restart_game:
            self.game_field.set_restart_flag()


def main():
    window = GameWindow((700, 700))


if __name__ == "__main__":
    main()
