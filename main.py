from core import TetrisBoard, Tetromino, Pentomino, ColorMap, RandomBag
from render import *
import pygame
from sys import exit
from random import choice
from math import sqrt
import os

TETSIS_HS_FILENAME = "tetris_hs"
PENTIX_HS_FILENAME = "pentix_hs"


def load_sound(name):
    fullname = os.path.join('data/sounds', name)
    sound = pygame.mixer.Sound(fullname)
    return sound


def load_highscores(highscores_filename):
    if os.path.isfile(highscores_filename):
        with open(highscores_filename) as f:
            data = f.read().strip()
        if data:
            h_score, h_level = map(int, data.split())
        else:
            h_score, h_level = 0, 0
    else:
        h_score, h_level = 0, 0
    return (h_score, h_level)


class GameWindow(object):
    def __init__(self, size: tuple):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(size)
        main_menu = Menu(self.screen)
        main_menu.run()


class Menu(object):
    def __init__(self, surface):
        # Save init params
        self.surface = surface
        # Initialise additional windows
        self.tetris = Tetris(surface, Tetromino, TETSIS_HS_FILENAME)
        self.pentris = Tetris(surface, Pentomino, PENTIX_HS_FILENAME)
        self.hs = HighScores(surface)
        # Initialise pygame renderers
        self.background = pygame.sprite.Group()
        PygamePicture((-50, -50), self.background, "menu_background.png")
        self.tetris_start_butt = PygamePushButton((250, 300), (200, 70), 50,
                                                  ColorMap.WHITE, ColorMap.WHITE,
                                                  5, None, self.tetris.run, "TETRIS")
        self.pentris_start_butt = PygamePushButton((250, 400), (200, 70), 50,
                                                   ColorMap.WHITE, ColorMap.WHITE,
                                                   5, None, self.pentris.run, "PENTIX")
        self.highscores_butt = PygamePushButton((250, 500), (200, 70), 40,
                                                ColorMap.WHITE, ColorMap.WHITE,
                                                5, None, self.hs.run, "HIGHSCORES")
        self.exit_butt = PygamePushButton((250, 600), (200, 70), 50,
                                          ColorMap.WHITE, ColorMap.WHITE,
                                          5, None, self.exit, "EXIT")
        self.menu_rect = PygameFillingRect(
            (200, 0), (300, 700), ColorMap.CLEAR, 0)
        self.logo = pygame.sprite.Group()
        PygamePicture((200, 0), self.logo, "logo.png", 0.25)
        # Set fps
        self.fps = 30
        # Ininitalize clock
        self.clock = pygame.time.Clock()

    def reset(self):
        self.exit = False

    def key_handler(self, key):
        pass

    def exit(self):
        self.exit = True

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.background.draw(self.surface)
        self.menu_rect.render(self.surface)
        self.logo.draw(self.surface)
        self.tetris_start_butt.render(self.surface)
        self.pentris_start_butt.render(self.surface)
        self.highscores_butt.render(self.surface)
        self.exit_butt.render(self.surface)
        pygame.display.flip()

    def run(self):
        self.reset()
        while True:
            print("menu")
            if self.exit:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.tetris_start_butt.check_click(event.pos)
                    self.pentris_start_butt.check_click(event.pos)
                    self.highscores_butt.check_click(event.pos)
                    self.exit_butt.check_click(event.pos)
            self.render()
            self.clock.tick(self.fps)


class Tetris(object):
    DROP_EVENT = pygame.USEREVENT + 1

    def __init__(self, surface, piece_type, highscore_filename):
        # Save init params
        self.surface = surface
        self.piece_type = piece_type
        self.highscore_filename = highscore_filename
        # Initialise additional windows
        self.pause_screen = Pause(surface, self)
        self.gameover_screen = GameOver(surface, self)
        # Initialise board
        self.board = TetrisBoard(ColorMap.CLEAR)
        # Innitialize pygame renderers
        self.board_renderer = PygameTileField(
            (150, -900), self.board, (40, 40), ColorMap.CLEAR)
        self.curr_piece_renderer = PygameTetrisPiece(
            (150, -900), None, (40, 40))
        self.ghost_piece_renderer = PygameTetrisPiece(
            (150, -900), None, (40, 40))
        self.next_piece_renderer = PygameTetrisPiece(
            (600, 50), None, (20, 20))
        self.hold_piece_renderer = PygameTetrisPiece(
            (600, 200), None, (20, 20))
        self.score_textbox = PygameTextBox(
            (10, 10), ColorMap.WHITE, 30, "Score: 0")
        self.level_textbox = PygameTextBox(
            (10, 40), ColorMap.WHITE, 30, "Level: 1")
        self.board_rect = PygameFillingRect(
            (150, -900), (400, 1600), ColorMap.BG, 0)
        self.score_rect = PygameFillingRect((5, 5), (140, 60), ColorMap.BG, 0)
        self.next_piece_rect = PygameFillingRect(
            (555, 5), (140, 140), ColorMap.BG, 0)
        self.next_piece_text = PygameTextBox(
            (600, 10), ColorMap.WHITE, 35, "Next")
        self.hold_piece_rect = PygameFillingRect(
            (555, 150), (140, 140), ColorMap.BG, 0)
        self.hold_piece_text = PygameTextBox(
            (600, 160), ColorMap.WHITE, 35, "Hold")
        # Initialise bg sprite
        self.background = pygame.sprite.Group()
        PygamePicture((-50, -50), self.background, "game_background.jpg")
        # Initialize randomzer
        self.randomizer = RandomBag(piece_type.SHAPES)
        # Set fps
        self.fps = 60
        # Debug
        self.lock_delay_textbox = PygameTextBox((100, 10), ColorMap.RED, 30)
        # Initialize clock
        self.clock = pygame.time.Clock()
        # Load all sounds
        self.main_theme = load_sound("main_theme.wav")
        self.main_theme.set_volume(0.3)
        self.hold_sound = load_sound("hold.wav")
        self.hard_drop_sound = load_sound("hard_drop.wav")
        self.rotate_sound = load_sound("rotate.wav")
        self.pause_sound = load_sound("pause.wav")
        self.gameover_sound = load_sound("gameover.wav")

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
        self.hard_drop_used = False
        self.exit = False
        self.restart = False
        self.board.new_piece(self.choose_piece())
        pygame.time.set_timer(self.DROP_EVENT, self.level_delay())
        self.lock_delay_frames = 0
        self.main_theme.play(-1)

    def hold(self):
        if self.hold_used:
            return
        self.hold_sound.play()
        self.clock.tick(5)
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
            self.hard_drop_sound.play()
            self.clock.tick(10)
            self.board.hard_drop_curr_piece()
            self.lock_delay_frames = self.fps
        elif key == pygame.K_DOWN:
            self.board.drop_curr_piece()
        elif key in (pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_z):
            self.board.rotate_curr_piece(False)
        elif key in (pygame.K_ESCAPE, pygame.K_F1):
            self.pause_sound.play()
            self.clock.tick(5)
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
        self.score_textbox.set_text(f"Score: {self.score}")
        self.level_textbox.set_text(f"Level: {self.level}")

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.background.draw(self.surface)
        self.board_rect.render(self.surface)
        self.score_rect.render(self.surface)
        self.next_piece_rect.render(self.surface)
        self.next_piece_text.render(self.surface)
        self.hold_piece_rect.render(self.surface)
        self.hold_piece_text.render(self.surface)
        self.board_renderer.render(self.surface)
        self.ghost_piece_renderer.render(self.surface)
        self.curr_piece_renderer.render(self.surface)
        self.next_piece_renderer.render(self.surface)
        self.hold_piece_renderer.render(self.surface)
        self.score_textbox.render(self.surface)
        self.level_textbox.render(self.surface)
        # Debug
        # self.lock_delay_textbox.render(self.surface)
        pygame.display.flip()

    def level_delay(self):
        return round(700 / sqrt(self.level))

    def choose_piece(self):
        return self.piece_type((0, 0), *next(self.randomizer))

    def run(self):
        self.reset()
        falling = False
        while True:
            print("game")
            if self.exit:
                self.main_theme.stop()
                self.save_score()
                break
            elif self.restart:
                self.main_theme.stop()
                self.save_score()
                self.reset()
            elif self.game_over:
                self.main_theme.stop()
                self.gameover_sound.play()
                self.gameover_screen.run()
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
            print(f"FD: {self.board.check_lock_delay()}")
            print(f"Falling: {falling}")
            print(f"LD frames: {self.lock_delay_frames}")
            if self.lock_delay_frames >= self.fps // 2:
                self.hold_used = False
                self.lock_delay_frames = 0
                self.board.put_curr_piece()
                self.board.clear_filled_rows(self.score_counter)
                self.next_piece.set_coords((4, 21))
                if self.board.piece_collides_tiles(self.next_piece):
                    self.game_over = True
                self.board.new_piece(self.next_piece)
                self.next_piece = self.choose_piece()
                print("Next piece")
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

    def get_score(self):
        return self.score

    def get_level(self):
        return self.level

    def save_score(self):
        if os.path.isfile(self.highscore_filename):
            with open(self.highscore_filename) as f:
                data = f.read().strip()
            if data:
                h_score, h_level = map(int, data.split())
            else:
                h_score, h_level = 0, 0
        else:
            h_score, h_level = 0, 0
        print(h_score, h_level)
        h_score = max(h_score, self.score)
        h_level = max(h_level, self.level)
        with open(self.highscore_filename, "w") as f:
            f.write(f"{h_score} {h_level}")


class Pause(object):
    def __init__(self, surface, game_field):
        self.surface = surface
        self.game_field = game_field
        self.resume_butt = PygamePushButton((250, 300), (200, 70), 50,
                                            ColorMap.WHITE, ColorMap.WHITE,
                                            5, None, self.resume_game, "Resume")
        self.exit_butt = PygamePushButton((250, 500), (200, 70), 50,
                                          ColorMap.WHITE, ColorMap.WHITE,
                                          5, None, self.exit_game, "Exit")
        self.restart_butt = PygamePushButton((250, 400), (200, 70), 50,
                                             ColorMap.WHITE, ColorMap.WHITE,
                                             5, None, self.restart_game, "Restart")
        self.pause_pic = pygame.sprite.Group()
        PygamePicture((-76, -100), self.pause_pic, "pause.jpg")
        self.fps = 30
        self.clock = pygame.time.Clock()

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.pause_pic.draw(self.surface)
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


class GameOver(object):
    def __init__(self, surface, game_field):
        self.surface = surface
        self.game_field = game_field
        self.exit_butt = PygamePushButton((250, 500), (200, 70), 50,
                                          ColorMap.WHITE, ColorMap.WHITE,
                                          5, None, self.exit_game, "Exit")
        self.restart_butt = PygamePushButton((250, 400), (200, 70), 50,
                                             ColorMap.WHITE, ColorMap.WHITE,
                                             5, None, self.restart_game, "Restart")
        self.score_textbox = PygameTextBox((250, 290), ColorMap.WHITE, 50, "0")
        self.gameover_pic = pygame.sprite.Group()
        PygamePicture((-76, -100), self.gameover_pic, "gameover.jpg")
        self.fps = 30
        self.clock = pygame.time.Clock()

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.gameover_pic.draw(self.surface)
        self.exit_butt.render(self.surface)
        self.restart_butt.render(self.surface)
        self.score_textbox.render(self.surface)
        pygame.display.flip()

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
        self.score_textbox.set_text(
            "Score: " + str(self.game_field.get_score()))

    def run(self):
        self.reset()
        while True:
            print("gameover")
            if self.exit:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.exit_butt.check_click(event.pos)
                    self.restart_butt.check_click(event.pos)
            self.render()
            self.clock.tick(self.fps)
        if self.exit_game:
            self.game_field.set_exit_flag()
        elif self.restart_game:
            self.game_field.set_restart_flag()


class HighScores(object):
    def __init__(self, surface):
        # Save init params
        self.surface = surface
        # Create renderers
        self.tetris_highscore_textbox = PygameTextBox(
            (0, 0), ColorMap.WHITE, 50)
        self.pentix_highscore_textbox = PygameTextBox(
            (0, 100), ColorMap.WHITE, 50)
        self.tetris_highlevel_textbox = PygameTextBox(
            (300, 50), ColorMap.WHITE, 50)
        self.pentix_highlevel_textbox = PygameTextBox(
            (300, 150), ColorMap.WHITE, 50)
        self.exit_butt = PygamePushButton((250, 400), (200, 70), 70,
                                          ColorMap.WHITE, ColorMap.WHITE,
                                          5, None, self.window_exit, "Exit")
        # Set fps
        self.fps = 15
        # Initialise clock
        self.clock = pygame.time.Clock()

    def window_exit(self):
        self.exit = True

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.tetris_highscore_textbox.render(self.surface)
        self.tetris_highlevel_textbox.render(self.surface)
        self.pentix_highscore_textbox.render(self.surface)
        self.pentix_highlevel_textbox.render(self.surface)
        self.exit_butt.render(self.surface)
        pygame.display.flip()

    def reset(self):
        self.exit = False
        h_score, h_level = load_highscores(TETSIS_HS_FILENAME)
        self.tetris_highscore_textbox.set_text(f"Tetris highscore: {h_score}")
        self.tetris_highlevel_textbox.set_text(f"Tetris max level: {h_level}")
        h_score, h_level = load_highscores(PENTIX_HS_FILENAME)
        self.pentix_highscore_textbox.set_text(f"Pentix highscore: {h_score}")
        self.pentix_highlevel_textbox.set_text(f"Pentix max level: {h_level}")

    def run(self):
        self.reset()
        while True:
            print("highscores")
            if self.exit:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.exit_butt.check_click(event.pos)
            self.render()
            self.clock.tick(self.fps)


def main():
    window = GameWindow((700, 700))


if __name__ == "__main__":
    main()
