import copy
import glob
import itertools
import pygame
import random
import re
import sys
from collections import namedtuple
from enum import Enum, auto
from pathlib import Path
from pygame.locals import *


SCREEN = Rect(0, 0, 700, 600)
# block area position
BLOCK_AREA_LEFT = 100
BLOCK_AREA_RIGHT = 300
BLOCK_AREA_BOTTOM = 495
BLOCK_AREA_TOP = 100
# score position
SCORE_X = 390
SCORE_Y = 360
# next block display
NEXT_BLOCK_AREA_LEFT = 410
NEXT_BLOCK_AREA_BOTTOM = 230
DISPLAY_X = 410
DISPLAY_Y = 130
NEXT_TEXT_X = 440
NEXT_TEXT_Y = 110
# pause screen
PAUSE_TEXT_X = 280
PAUSE_TEXT_Y = 210
PAUSE_IMAGE_LEFT = 250
PAUSE_IMAGE_TOP = 260
# start screen
TITLE_X = 360
TITLE_Y = 150
START_TEXT_X = 410
START_TEXT_Y = 300
# the number of columns and rows in block area
COLS = 10
ROWS = 20
# block size
BLOCK_SIZE = 20
# text color
TEXT_WHITE = (255, 255, 250)
TEXT_PINK = (235, 107, 212)
# button position
RESTART_LEFT = 310
RESTART_TOP = 330
STOP_LEFT = 630
STOP_TOP = 10
PAUSE_LEFT = 580
PAUSE_TOP = 10
START_LEFT = 430
START_TOP = 350


BlockSet = namedtuple('BlockSet', 'file next coordinates')


class ImageFiles(Enum):

    START = 'button_start.png'
    STOP = 'button_stop.png'
    PAUSE = 'button_pause.png'
    PLATE = 'plate.png'
    START_SCREEN = 'start.png'
    BLUE = 'blue25.png'
    DARK = 'dark25.png'
    GREEN = 'green25.png'
    ORANGE = 'orange25.png'
    PURPLE = 'purple25.png'
    RED = 'red25.png'
    YELLOW = 'yellow25.png'

    def __init__(self, name):
        self._name = name

    @property
    def path(self):
        return Path('images', self._name)


BLUE = BlockSet(ImageFiles.BLUE, [[1, 2.5], [2, 2.5], [3, 2.5], [4, 2.5]],
                [[[-1, 4], [0, 4], [1, 4], [2, 4]], [[-1, 4], [-1, 5], [-1, 6], [-1, 7]], [[-1, 4], [0, 4], [1, 4], [2, 4]], [[-1, 4], [-1, 5], [-1, 6], [-1, 7]]])
DARK = BlockSet(ImageFiles.DARK, [[2, 1.5], [3, 1.5], [3, 2.5], [3, 3.5]],
                [[[-1, 3], [0, 3], [0, 4], [0, 5]], [[-1, 4], [0, 4], [1, 4], [1, 3]], [[-1, 3], [-1, 4], [-1, 5], [0, 5]], [[-1, 4], [-1, 5], [0, 4], [1, 4]]])
GREEN = BlockSet(ImageFiles.GREEN, [[2, 1.5], [2, 2.5], [3, 2.5], [3, 3.5]],
                 [[[-1, 4], [-1, 5], [0, 3], [0, 4]], [[-1, 3], [0, 3], [0, 4], [1, 4]], [[-1, 4], [-1, 5], [0, 3], [0, 4]], [[-1, 3], [0, 3], [0, 4], [1, 4]]])
ORANGE = BlockSet(ImageFiles.ORANGE, [[2, 3.5], [3, 1.5], [3, 2.5], [3, 3.5]],
                  [[[-1, 5], [0, 3], [0, 4], [0, 5]], [[-1, 3], [-1, 4], [0, 4], [1, 4]], [[-1, 3], [-1, 4], [-1, 5], [0, 3]], [[-1, 4], [0, 4], [1, 4], [1, 5]]])
PURPLE = BlockSet(ImageFiles.PURPLE, [[2, 2.5], [3, 1.5], [3, 2.5], [3, 3.5]],
                  [[[-1, 4], [0, 3], [0, 4], [0, 5]], [[-1, 4], [0, 4], [1, 4], [0, 3]], [[-1, 3], [-1, 4], [-1, 5], [0, 4]], [[-1, 4], [0, 4], [1, 4], [0, 5]]])
RED = BlockSet(ImageFiles.RED, [[2, 2.5], [2, 3.5], [3, 1.5], [3, 2.5]],
               [[[-1, 3], [-1, 4], [0, 4], [0, 5]], [[-1, 4], [0, 3], [0, 4], [1, 3]], [[-1, 3], [-1, 4], [0, 4], [0, 5]], [[-1, 4], [0, 3], [0, 4], [1, 3]]])
YELLOW = BlockSet(ImageFiles.YELLOW, [[2, 2], [2, 3], [3, 2], [3, 3]],
                  [[[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]]])
BLOCKSETS = [BLUE, DARK, GREEN, ORANGE, PURPLE, RED, YELLOW]


class Status(Enum):
    START = auto()
    PLAY = auto()
    PAUSE = auto()
    GAMEOVER = auto()


class PyTetris:

    def __init__(self, screen):
        self.screen = screen
        self.matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.blocks = [None for _ in range(4)]
        self.create_play_screen()
        self.create_start_screen()
        self.create_pause_screen()
        self.create_gameover_screen()
        self.status = Status.START
        self.update = self.start_screen.draw

    def initialize(self):
        self.all_blocks_clear()
        self.score.score = 0
        self.index = 0
        self.drop_timer = 20
        self.ground_timer = 60
        self.judge_timer = 20
        self.next_blockset = None
        self.update = self.update_moving_block
        self.create_block()

    def all_blocks_clear(self):
        for row in itertools.chain((r for r in self.matrix), [self.blocks]):
            for i, block in enumerate(row):
                if block:
                    row[i] = block.kill()
        self.next_block_display.delete_blocks()

    def create_play_screen(self):
        _ = Plate(ImageFiles.PLATE.path)
        self.score = Score(self.screen)
        self.next_block_display = NextBlockDisplay(ImageFiles.PLATE.path, self.screen)
        self.stop_button = StopButton(ImageFiles.STOP.path, STOP_LEFT, STOP_TOP)
        self.pause_button = StopButton(ImageFiles.PAUSE.path, PAUSE_LEFT, PAUSE_TOP)

    def create_pause_screen(self):
        self.pause_screen = Pause('images', self.screen)
        self.restart_button = RestartButton(
            ImageFiles.START.path, RESTART_LEFT, RESTART_TOP)

    def create_start_screen(self):
        self.start_screen = Start(ImageFiles.START_SCREEN.path, self.screen)
        self.start_button = StartButton(
            ImageFiles.START.path, START_LEFT, START_TOP)

    def create_gameover_screen(self):
        self.repeat_button = RepeatButton(ImageFiles.START.path, 0, 0)
        self.gameover_screen = GameOver(
            'images/gameover.png', self.screen, self.repeat_button)

    def get_blockset(self):
        index = random.randint(0, len(BLOCKSETS) - 1)
        blockset = BLOCKSETS[index]
        return blockset

    def create_block(self):
        if self.next_blockset is None:
            blockset = self.get_blockset()
        else:
            blockset = self.next_blockset
        self.next_blockset = self.get_blockset()
        self.next_block_display.show_next(self.next_blockset)
        for i, (row, col) in enumerate(blockset.coordinates[0]):
            self.blocks[i] = Block(blockset.file.path, row, col)
        self.blockset = copy.deepcopy(blockset.coordinates)

    def set_block_center(self, block):
        block.rect.centerx = BLOCK_AREA_LEFT + block.col * BLOCK_SIZE
        block.rect.centery = BLOCK_AREA_TOP + block.row * BLOCK_SIZE

    def update_moving_block(self):
        self.drop_timer -= 1
        if self.drop_timer == 0:
            self.move_down()
            self.drop_timer = 20

        for block in self.blocks:
            self.set_block_center(block)

        self.judge_timer -= 1
        if self.judge_timer == 0:
            self.judge_timer = 20
            if any(self.judge_ground(block) for block in self.blocks):
                self.update_matrix()

                if any(all(row) for row in self.matrix):
                    self.ground_timer = 60
                    self.update = self.update_ground_blocks
                # Game over
                elif any(block for block in self.matrix[0]):
                    self.status = Status.GAMEOVER
                    pygame.time.wait(1000)
                    self.update = self.gameover_screen.draw
                else:
                    self.create_block()
                    self.drop_timer = 1

    def update_ground_blocks(self):
        self.ground_timer -= 1
        if self.ground_timer == 40:
            if deleted_rows := self.delete_blocks():
                self.score.add_score(self.calculate_score(deleted_rows))
        if self.ground_timer == 20:
            self.move_ground_blocks()
        if self.ground_timer == 0:
            self.create_block()
            self.drop_timer = 1
            self.update = self.update_moving_block

    def delete_blocks(self):
        deleted_rows = 0
        for row in self.matrix:
            if all(row):
                deleted_rows += 1
                for i, block in enumerate(row):
                    row[i] = block.kill()
        return deleted_rows

    def move_ground_blocks(self):
        self.matrix.sort(key=lambda row: 1 if any(row) else 0)
        for i, row in enumerate(self.matrix):
            for block in row:
                if block:
                    block.row = i
                    self.set_block_center(block)

    def check_matrix(self, block, new_row, new_col):
        # Check whether the block is not contained in self.blocks.
        if (new_row, new_col) not in self.blockset[self.index]:
            if self.matrix[new_row][new_col]:
                return True

    def judge_left(self, block):
        new_col = block.col - 1
        if new_col < 0 or self.check_matrix(block, block.row, new_col):
            return False
        return True

    def judge_right(self, block):
        new_col = block.col + 1
        if new_col >= COLS or self.check_matrix(block, block.row, new_col):
            return False
        return True

    def judge_down(self, block):
        new_row = block.row + 1
        if new_row >= ROWS or self.check_matrix(block, new_row, block.col):
            return False
        return True

    def judge_ground(self, block):
        if block.row == ROWS - 1 or self.check_matrix(block, block.row + 1, block.col):
            return True
        return False

    def update_matrix(self):
        for block in self.blocks:
            self.matrix[block.row][block.col] = block

    def update_matrix_row(self, step):
        for block in self.blockset:
            for row_col in block:
                row_col[0] += step

    def update_matrix_col(self, step):
        for block in self.blockset:
            for row_col in block:
                row_col[1] += step

    def move_right(self):
        if all(self.judge_right(block) for block in self.blocks):
            self.update_matrix_col(1)
            for block in self.blocks:
                block.col += 1

    def move_left(self):
        if all(self.judge_left(block) for block in self.blocks):
            self.update_matrix_col(-1)
            for block in self.blocks:
                block.col -= 1

    def move_down(self, step=1):
        if all(self.judge_down(block) for block in self.blocks):
            self.update_matrix_row(step)
            for block in self.blocks:
                block.row += step

    def move_up(self):
        self.update_row(-1)
        for block in self.blocks:
            block.row -= 1

    def judge_rotate(self, rotated_pos):
        # Check right side
        if (over := max(col - (COLS - 1) for _, col in rotated_pos)) > 0:
            if any(self.matrix[row][col - over] for row, col in rotated_pos):
                return False, 0
            return True, over
        # Check left side
        elif (over := min(col for _, col in rotated_pos)) < 0:
            if any(self.matrix[row][col - over] for row, col in rotated_pos):
                return False, 0
            return True, over
        else:
            if any(self.matrix[row][col] for row, col in rotated_pos):
                return False, 0
            return True, 0

    def rotate(self):
        next_index = self.index + 1
        if next_index > 3:
            next_index = 0
        rotated_pos = self.blockset[next_index]
        rotatable, over = self.judge_rotate(rotated_pos)
        if rotatable:
            self.index = next_index
            for block, (row, col) in zip(self.blocks, rotated_pos):
                block.row = row
                block.col = col - over

    def click(self, x, y):
        if self.status == Status.PLAY and \
                self.stop_button.rect.collidepoint(x, y):
            self.status = Status.START
            self.update = self.start_screen.draw
        elif self.status == Status.PLAY and \
                self.pause_button.rect.collidepoint(x, y):
            self.before_method = self.update
            self.status = Status.PAUSE
            self.update = self.pause_screen.draw
        elif self.status == Status.PAUSE and \
                self.restart_button.rect.collidepoint(x, y):
            self.status = Status.PLAY
            self.update = self.before_method
        elif self.status == Status.START and \
                self.start_button.rect.collidepoint(x, y):
            self.status = Status.PLAY
            self.initialize()

    def calculate_score(self, deleted_rows):
        if deleted_rows == 1:
            return 40
        elif deleted_rows == 2:
            return 100
        elif deleted_rows == 3:
            return 300
        else:
            return 1200

    def game_over(self):
        self.sysfont = pygame.font.SysFont(None, 70)
        img = self.sysfont.render('GAME OVER', True, TEXT_WHITE)
        self.screen.blit(img, (300, 500))

    def pause(self):
        img = self.pause_sysfont.render('PAUSE', True, TEXT_WHITE)
        # self.screen.blit(img, (280, 230))
        self.screen.blit(img, (PAUSE_TEXT_X, PAUSE_TEXT_Y))


class Block(pygame.sprite.Sprite):

    def __init__(self, filename, row, col):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.row = row
        self.col = col
        self.stop = False


class Plate(pygame.sprite.Sprite):

    def __init__(self, filename):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, (200, 5))
        self.rect = self.image.get_rect()
        self.rect.left = BLOCK_AREA_LEFT - 10
        self.rect.bottom = BLOCK_AREA_BOTTOM


class NextBlockDisplay(pygame.sprite.Sprite):

    def __init__(self, path, screen):
        super().__init__(self.containers)
        # self.image = pygame.image.load(filename).convert()
        self.image = pygame.image.load(path).convert()
        self.image = pygame.transform.scale(self.image, (100, 5))
        self.rect = self.image.get_rect()
        self.rect.left = NEXT_BLOCK_AREA_LEFT
        self.rect.bottom = NEXT_BLOCK_AREA_BOTTOM
        self.sysfont = pygame.font.SysFont(None, 30)
        self.screen = screen
        self.next_blocks = []

    def draw(self):
        text = self.sysfont.render(
            'next', True, TEXT_WHITE)
        self.screen.blit(text, (NEXT_TEXT_X, NEXT_TEXT_Y))

    def show_next(self, block_set):
        self.delete_blocks()
        for row, col in block_set.next:
            block = Block(block_set.file.path, row, col)
            block.rect.centerx = DISPLAY_X + block.col * BLOCK_SIZE
            block.rect.centery = DISPLAY_Y + block.row * BLOCK_SIZE
            self.next_blocks.append(block)

    def delete_blocks(self):
        while self.next_blocks:
            block = self.next_blocks.pop()
            block.kill()


class Button(pygame.sprite.Sprite):

    def __init__(self, file_path, width, height):
        super().__init__(self.containers)
        self.image = pygame.image.load(file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()


class StopButton(Button):

    def __init__(self, file_path, left, top, width=40, height=40):
        super().__init__(file_path, width, height)
        self.rect.left = left
        self.rect.top = top


class RestartButton(Button):

    def __init__(self, file_path, left, top, width=50, height=50):
        super().__init__(file_path, width, height)
        self.rect.left = left
        self.rect.top = top


class StartButton(Button):

    def __init__(self, file_path, left, top, width=50, height=50):
        super().__init__(file_path, width, height)
        self.rect.left = left
        self.rect.top = top


class RepeatButton(Button):

    def __init__(self, file_path, center_x, center_y, width=50, height=50):
        super().__init__(file_path, width, height)
        self.rect.centerx = 350
        self.rect.centery = 400


class Pause(pygame.sprite.Sprite):

    def __init__(self, root, screen):
        super().__init__(self.containers)
        self.screen = screen
        self.images = [image for image in self.create_image(root)]
        self.images_count = len(self.images)
        self.timer = 20
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.left = PAUSE_IMAGE_LEFT
        self.rect.top = PAUSE_IMAGE_TOP
        self.pause_sysfont = pygame.font.SysFont(None, 50)

    def create_image(self, root):
        pattern = re.compile('pause\d+\.png')
        for path in glob.iglob(f'{root}/*'):
            file_path = Path(path)
            if pattern.match(file_path.name):
                yield pygame.image.load(file_path.as_posix()).convert()

    def draw(self):
        text = self.pause_sysfont.render('PAUSE', True, TEXT_WHITE)
        self.screen.blit(text, (PAUSE_TEXT_X, PAUSE_TEXT_Y))

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            if self.index >= self.images_count:
                self.index = 0
            self.image = self.images[self.index]
            self.index += 1
            self.timer = 20


class Start(pygame.sprite.Sprite):

    def __init__(self, filename, screen):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
        self.rect = self.image.get_rect()
        self.rect.left = 50
        self.rect.top = 50
        self.screen = screen
        self.timer = 20
        self.index = -1
        self.title_font = pygame.font.SysFont(None, 70)
        self.message_size = (40, 50, 40)

    def draw(self):
        self.timer -= 1
        if self.timer == 0:
            self.index += 1
            if self.index >= len(self.message_size):
                self.index = -1
            self.timer = 20

        size = self.message_size[self.index]
        message_font = pygame.font.SysFont(None, self.message_size[self.index])
        message = message_font.render('START', True, TEXT_PINK)
        delta = 10 if size == 50 else 0
        self.screen.blit(message, (START_TEXT_X - delta, START_TEXT_Y))
        title = self.title_font.render('TETRIS', True, TEXT_WHITE)
        self.screen.blit(title, (TITLE_X, TITLE_Y))


class GameOver(pygame.sprite.Sprite):

    def __init__(self, file_path, screen, repeat_button):
        super().__init__(self.containers)
        self.screen = screen
        self.image = pygame.image.load(file_path).convert()
        self.rect = self.image.get_rect()
        self.top = 0
        self.is_draw = False
        self.repeat_button = repeat_button
        self.timer = 20
        self.index = -1
        self.message_size = (40, 50, 40)

    def draw(self):
        # if self.is_draw:
        self.timer -= 1
        if self.timer == 0:
            self.index += 1
            if self.index >= len(self.message_size):
                self.index = -1
            self.timer = 20

        size = self.message_size[self.index]
        message_font = pygame.font.SysFont(None, self.message_size[self.index])
        message = message_font.render('START', True, TEXT_PINK)
        delta = 10 if size == 50 else 0
        self.screen.blit(message, (START_TEXT_X - delta, START_TEXT_Y))

    def update(self):
        if self.top <= 200:
            self.top += 20
        self.rect.left = 200
        self.rect.top = self.top


class Score:

    def __init__(self, screen):
        self.sysfont = pygame.font.SysFont(None, 40)
        self.screen = screen
        self.score = 0

    def draw(self):
        text = self.sysfont.render(
            f'SCORE {self.score}', True, TEXT_WHITE)
        self.screen.blit(text, (SCORE_X, SCORE_Y))

    def add_score(self, score):
        self.score += score


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    play = pygame.sprite.RenderUpdates()
    pause = pygame.sprite.RenderUpdates()
    start = pygame.sprite.RenderUpdates()
    gameover = pygame.sprite.RenderUpdates()
    Block.containers = play
    Plate.containers = play
    NextBlockDisplay.containers = play
    StopButton.containers = play
    Pause.containers = pause
    RestartButton.containers = pause
    Start.containers = start
    StartButton.containers = start
    GameOver.containers = gameover
    RepeatButton.containers = gameover

    tetris = PyTetris(screen)
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        screen.fill((0, 100, 0))

        tetris.update()

        if tetris.status == Status.PLAY:
            play.update()
            play.draw(screen)
            tetris.score.draw()
            tetris.next_block_display.draw()
        if tetris.status == Status.PAUSE:
            pause.update()
            pause.draw(screen)
        if tetris.status == Status.START:
            start.update()
            start.draw(screen)
        if tetris.status == Status.GAMEOVER:
            gameover.update()
            gameover.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                tetris.click(*event.pos)
            if tetris.status == Status.PLAY:
                if event.type == KEYDOWN:
                    if event.key == K_RIGHT:
                        tetris.move_right()
                    if event.key == K_LEFT:
                        tetris.move_left()
                    if event.key == K_DOWN:
                        tetris.move_down()
                    if event.key == K_UP:
                        tetris.rotate()

        pygame.display.update()


    # while True:
    #     clock.tick(60)
    #     screen.fill((0, 100, 0))

    #     tetris.update()
    #     play.update()
    #     play.draw(screen)
    #     score.draw()
    #     next_display.draw()

    #     for event in pygame.event.get():
    #         if event.type == QUIT:
    #             pygame.quit()
    #             sys.exit()
    #         if event.type == MOUSEBUTTONDOWN and event.button == 1:
    #             # x, y = event.pos
    #             tetris.click(*event.pos)
    #         if tetris.status == Status.PLAY:
    #             if event.type == KEYDOWN:
    #                 if event.key == K_RIGHT:
    #                     tetris.move_right()
    #                 if event.key == K_LEFT:
    #                     tetris.move_left()
    #                 if event.key == K_DOWN:
    #                     tetris.move_down()
    #                 if event.key == K_UP:
    #                     tetris.rotate()

    #     pygame.display.update()



if __name__ == '__main__':
    main()
