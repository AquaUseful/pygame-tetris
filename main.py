from core import TetrisBoard, Tetromino, Pentomino, ColorMap
from render import PygameTileField, PygameTetrisPiece
import pygame
from sys import exit


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
        self.piece_type = piece_type
        self.board = TetrisBoard(ColorMap.CLEAR)
        self.board_renderer = PygameTileField(
            (0, 50), self.board, (10, 10), ColorMap.CLEAR)
        self.curr_piece_renderer = PygameTetrisPiece(
            (0, 50), None, (10, 10))
        self.ghost_piece_renderer = PygameTetrisPiece(
            (0, 50), None, (10, 10))
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
            self.board.rotate_curr_piece(False)
        elif key == pygame.K_SPACE:
            self.board.hard_drop_curr_piece()
            self.lock_delay_frames = self.fps

    def score_counter(self, cleared_rows):
        pass

    def render(self):
        self.surface.fill(ColorMap.CLEAR)
        self.board_renderer.render(self.surface, True)
        self.curr_piece_renderer.render(self.surface)
        self.ghost_piece_renderer.render(self.surface)
        pygame.display.flip()

    def level_delay(self):
        return 500

    def run(self):
        self.board.new_piece(self.piece_type)
        self.clock = pygame.time.Clock()
        pygame.time.set_timer(self.DROP_EVENT, self.level_delay())
        self.lock_delay_frames = 0
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
            if self.lock_delay_frames >= self.fps // 2:
                self.lock_delay_frames = 0
                self.board.put_curr_piece()
                self.board.clear_filled_rows()
                self.board.new_piece(self.piece_type)
            print(self.lock_delay_frames)
            curr_piece = self.board.get_curr_piece()
            self.curr_piece_renderer.set_piece(curr_piece)
            ghost_piece = self.board.get_ghost_piece()
            self.ghost_piece_renderer.set_piece(ghost_piece)
            self.render()
            self.clock.tick(self.fps)


def main():
    window = GameWindow((700, 700))


if __name__ == "__main__":
    main()
