from core import TetrisBoard, Tetromino, Pentomino, ColorMap, RandomBag
from render import PygameTileField, PygameTetrisPiece, PygameTextBox
import pygame
from sys import exit
from random import choice


class GameWindow(object):
    def __init__(self, size: tuple):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(size)
        main_menu = Menu(self.screen)


class Menu(object):
    def __init__(self, surface):
        self.tetris = Tetris(surface, Tetromino)
        self.tetris.run()


class Tetris(object):
    DROP_EVENT = pygame.USEREVENT + 1

    def __init__(self, surface, piece_type):
        self.surface = surface
        self.board = TetrisBoard(ColorMap.CLEAR)
        self.piece_type = piece_type
        self.board_renderer = PygameTileField(
            (0, -100), self.board, (20, 20), ColorMap.CLEAR)
        self.curr_piece_renderer = PygameTetrisPiece(
            (0, -100), None, (20, 20))
        self.ghost_piece_renderer = PygameTetrisPiece(
            (0, -100), None, (20, 20))
        self.next_piece_renderer = PygameTetrisPiece(
            (300, 20), None, (20, 20))
        self.score_textbox = PygameTextBox(
            (10, 10), ColorMap.WHITE, 30)
        self.randomizer = RandomBag(piece_type.SHAPES)
        self.fps = 60
        self.reset()

    def reset(self):
        self.board.reset()
        self.game_over = False
        self.score = 0
        self.level = 1

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
        # elif key == pygame.

    def score_counter(self, cleared_rows):
        self.score += cleared_rows ** 2 * 100
        self.score_textbox.set_text(self.score)

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.board_renderer.render(self.surface, True)
        self.ghost_piece_renderer.render(self.surface)
        self.curr_piece_renderer.render(self.surface)
        self.next_piece_renderer.render(self.surface)
        self.score_textbox.render(self.surface, True)
        pygame.display.flip()

    def level_delay(self):
        return 500

    def check_game_over(self):
        if self.game_over:
            print("Gameover")

    def choose_piece(self, coords):
        return self.piece_type(coords, *next(self.randomizer))

    def run(self):
        next_piece = self.choose_piece((0, 0))
        self.board.new_piece(self.choose_piece((4, 20)))
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
                next_piece.move((4, 20))
                self.board.new_piece(next_piece)
                next_piece = self.choose_piece((0, 0))
            self.check_game_over()
            curr_piece = self.board.get_curr_piece()
            self.curr_piece_renderer.set_piece(curr_piece)
            ghost_piece = self.board.get_ghost_piece()
            self.ghost_piece_renderer.set_piece(ghost_piece)
            self.next_piece_renderer.set_piece(next_piece)
            self.render()
            self.clock.tick(self.fps)


def main():
    window = GameWindow((700, 700))


if __name__ == "__main__":
    main()
