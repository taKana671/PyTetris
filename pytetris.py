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

import numpy as np

from pytetris_utils import update_blockset_row, update_blockset_col


SCREEN = Rect(0, 0, 700, 600)
# block area
BLOCK_AREA_LEFT = 150
BLOCK_AREA_RIGHT = 350
BLOCK_AREA_BOTTOM = 495
BLOCK_AREA_TOP = 100
# score area
SCORE_AREA_X = 430
SCORE_AREA_Y = 300
# next block area
NEXT_BLOCK_AREA_LEFT = 430
NEXT_BLOCK_AREA_BOTTOM = 230
DISPLAY_X = 430
DISPLAY_Y = 130
NEXT_TEXT_X = 430
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
# gameover screen
REPEAT_TEXT_X = 290
REPEAT_TEXT_Y = 330
GAMEOVER_TOP = 220
GAMEOVER_BOUND_TOP = 170
GAMEOVER_LEFT = 130
# the number of columns and rows in block area
COLS = 10
ROWS = 20
# block size
BLOCK_SIZE = 20
# text color
COLOR_WHITE = (255, 255, 250)
COLOR_PINK = (235, 107, 212)
COLOR_GREEN = (0, 100, 0)
# button position
RESTART_LEFT = 310
RESTART_TOP = 330
STOP_LEFT = 630
STOP_TOP = 10
PAUSE_LEFT = 580
PAUSE_TOP = 10
START_LEFT = 430
START_TOP = 350
REPEAT_X = 343
REPEAT_Y = 400


BlockSet = namedtuple('BlockSet', 'file next coordinates')


class Files(Enum):

    def __init__(self, name, dir):
        self._name = name
        self._dir = dir

    @property
    def path(self):
        return Path(self._dir, self._name)


class ImageFiles(Files):

    START = 'button_start.png'
    STOP = 'button_stop.png'
    PAUSE = 'button_pause.png'
    PLATE = 'plate.png'
    START_SCREEN = 'start.png'
    GAMEOVER_SCREEN = 'gameover.png'
    BLOCK_BLUE = 'block_blue.png'
    BLOCK_DARK = 'block_dark.png'
    BLOCK_GREEN = 'block_green.png'
    BLOCK_ORANGE = 'block_orange.png'
    BLOCK_PURPLE = 'block_purple.png'
    BLOCK_RED = 'block_red.png'
    BLOCK_YELLOW = 'block_yellow.png'
    PAUSE_0 = 'pause0.png'
    PAUSE_1 = 'pause1.png'
    PAUSE_2 = 'pause2.png'
    PAUSE_3 = 'pause3.png'
    PAUSE_4 = 'pause4.png'
    PAUSE_5 = 'pause5.png'
    PAUSE_6 = 'pause6.png'

    def __init__(self, name):
        super().__init__(name, 'images')


class SoundFiles(Files):

    ROTATE = 'rotate.wav'
    GAMEOVER = 'gameover.wav'
    FANFARE = 'fanfare.wav'

    def __init__(self, name):
        super().__init__(name, 'sounds')


BLUE = BlockSet(ImageFiles.BLOCK_BLUE, [[0.5, 2], [1.5, 2], [2.5, 2], [3.5, 2]],
                np.array([[[-1, 4], [0, 4], [1, 4], [2, 4]], [[-1, 4], [-1, 5], [-1, 6], [-1, 7]], [[-1, 4], [0, 4], [1, 4], [2, 4]], [[-1, 4], [-1, 5], [-1, 6], [-1, 7]]]))
DARK = BlockSet(ImageFiles.BLOCK_DARK, [[1.5, 1], [2.5, 1], [2.5, 2], [2.5, 3]],
                np.array([[[-1, 3], [0, 3], [0, 4], [0, 5]], [[-1, 4], [0, 4], [1, 4], [1, 3]], [[-1, 3], [-1, 4], [-1, 5], [0, 5]], [[-1, 4], [-1, 5], [0, 4], [1, 4]]]))
GREEN = BlockSet(ImageFiles.BLOCK_GREEN, [[1.5, 2], [1.5, 3], [2.5, 1], [2.5, 2]],
                 np.array([[[-1, 4], [-1, 5], [0, 3], [0, 4]], [[-1, 3], [0, 3], [0, 4], [1, 4]], [[-1, 4], [-1, 5], [0, 3], [0, 4]], [[-1, 3], [0, 3], [0, 4], [1, 4]]]))
ORANGE = BlockSet(ImageFiles.BLOCK_ORANGE, [[1.5, 3], [2.5, 1], [2.5, 2], [2.5, 3]],
                  np.array([[[-1, 5], [0, 3], [0, 4], [0, 5]], [[-1, 3], [-1, 4], [0, 4], [1, 4]], [[-1, 3], [-1, 4], [-1, 5], [0, 3]], [[-1, 4], [0, 4], [1, 4], [1, 5]]]))
PURPLE = BlockSet(ImageFiles.BLOCK_PURPLE, [[1.5, 2], [2.5, 1], [2.5, 2], [2.5, 3]],
                  np.array([[[-1, 4], [0, 3], [0, 4], [0, 5]], [[-1, 4], [0, 4], [1, 4], [0, 3]], [[-1, 3], [-1, 4], [-1, 5], [0, 4]], [[-1, 4], [0, 4], [1, 4], [0, 5]]]))
RED = BlockSet(ImageFiles.BLOCK_RED, [[1.5, 1], [1.5, 2], [2.5, 2], [2.5, 3]],
               np.array([[[-1, 3], [-1, 4], [0, 4], [0, 5]], [[-1, 4], [0, 3], [0, 4], [1, 3]], [[-1, 3], [-1, 4], [0, 4], [0, 5]], [[-1, 4], [0, 3], [0, 4], [1, 3]]]))
YELLOW = BlockSet(ImageFiles.BLOCK_YELLOW, [[1.5, 1.5], [1.5, 2.5], [2.5, 1.5], [2.5, 2.5]],
                  np.array([[[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]]]))
BLOCKSETS = [BLUE, DARK, GREEN, ORANGE, PURPLE, RED, YELLOW]


class Status(Enum):
    START = auto()
    PLAY = auto()
    PAUSE = auto()
    GAMEOVER = auto()
    REPEAT = auto()
    WAITING = auto()
    DROPPING = auto()


class PyTetris:

    def __init__(self, screen):
        self.screen = screen
        self.matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.blocks = [None for _ in range(4)]
        self.create_play_screen()
        self.create_start_screen()
        self.create_pause_screen()
        self.create_gameover_screen()
        self.create_sounds()
        self.block_status = Status.WAITING
        self.status = Status.START

    def initialize(self):
        self.all_blocks_clear()
        self.score.initialize()
        self.level = self.score.level
        self.timer_value = 40
        self.drop_timer = self.timer_value
        self.ground_timer = 60
        self.judge_timer = self.timer_value
        self.next_blockset = None
        self.create_block()
        self.block_status = Status.DROPPING
        self.status = Status.PLAY
        self.update = self.update_moving_block

    def all_blocks_clear(self):
        for row in itertools.chain((r for r in self.matrix), [self.blocks]):
            for i, block in enumerate(row):
                if block:
                    row[i] = block.kill()

    def create_sounds(self):
        self.rotate_sound = pygame.mixer.Sound(SoundFiles.ROTATE.path)
        self.break_sound = pygame.mixer.Sound(SoundFiles.FANFARE.path)
        self.gameover_sound = pygame.mixer.Sound(SoundFiles.GAMEOVER.path)

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
        self.repeat_button = RepeatButton(ImageFiles.START.path, REPEAT_X, REPEAT_Y)
        self.gameover_screen = GameOver(
            ImageFiles.GAMEOVER_SCREEN.path, self.screen, self)

    def get_blockset_index(self):
        index = random.randint(0, len(BLOCKSETS) - 1)
        return index

    def create_block(self):
        if self.next_blockset is None:
            blockset = BLOCKSETS[self.get_blockset_index()]
        else:
            blockset = self.next_blockset

        blockset_index = self.get_blockset_index()
        self.next_blockset = BLOCKSETS[blockset_index]
        self.next_block_display.set_images(blockset_index)
        for i, (row, col) in enumerate(blockset.coordinates[0]):
            self.blocks[i] = Block(blockset.file.path, row, col)
        self.blockset = copy.deepcopy(blockset.coordinates)
        # self.index is used to rotate blocks.
        self.index = 0

    def set_block_center(self, block):
        block.rect.centerx = BLOCK_AREA_LEFT + block.col * BLOCK_SIZE
        block.rect.centery = BLOCK_AREA_TOP + block.row * BLOCK_SIZE

    def update_moving_block(self):
        self.drop_timer -= 1
        if self.status == Status.PLAY and self.drop_timer == 0:
            self.move_down()
            self.drop_timer = self.timer_value
        if (lower := min(block.row for block in self.blocks)) < 0:
            self.correct_top(lower)

        for block in self.blocks:
            self.set_block_center(block)

        self.judge_timer -= 1
        if self.judge_timer == 0:
            self.judge_timer = self.timer_value
            if any(self.judge_ground(block) for block in self.blocks):
                self.update_matrix()
                if any(all(row) for row in self.matrix):
                    self.ground_timer = 50
                    self.block_status = Status.WAITING
                    self.update = self.update_ground_blocks
                # Game over
                elif any(block for block in self.matrix[0]):
                    self.status = Status.GAMEOVER
                    self.gameover_sound.play()
                else:
                    self.create_block()
                    self.drop_timer = 1

    def update_ground_blocks(self):
        self.ground_timer -= 1
        if self.ground_timer == 40:
            if deleted_rows := self.delete_blocks():
                self.break_sound.play()
                self.score.add(deleted_rows)
                if self.level != self.score.level:
                    self.timer_value -= 2
                    self.level = self.score.level
        if self.ground_timer == 20:
            self.move_ground_blocks()
        if self.ground_timer == 0:
            self.create_block()
            self.drop_timer = 1
            self.block_status = Status.DROPPING
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

    def check_matrix(self, new_row, new_col):
        if self.matrix[new_row][new_col]:
            return True

    def judge_left(self, block):
        new_col = block.col - 1
        if new_col < 0 or self.check_matrix(block.row, new_col):
            return False
        return True

    def judge_right(self, block):
        new_col = block.col + 1
        if new_col >= COLS or self.check_matrix(block.row, new_col):
            return False
        return True

    def judge_down(self, block):
        new_row = block.row + 1
        if new_row >= ROWS or self.check_matrix(new_row, block.col):
            return False
        return True

    def judge_ground(self, block):
        if block.row == ROWS - 1 or self.check_matrix(block.row + 1, block.col):
            return True
        return False

    def correct_top(self, lower):
        """If the blocks which rows are out of the block area are found in dropping blocks,
           correct their rows, and kill the blocks already in the matrix to make spaces
           for the dropping blocks.
           Args:
                lower: int, the number of rows out of the block area
        """
        for block in self.blocks:
            block.row += abs(lower)
        for block in self.blocks:
            if old_block := self.matrix[block.row][block.col]:
                old_block.kill()

    def update_matrix(self):
        for block in self.blocks:
            self.matrix[block.row][block.col] = block

    def move_right(self, step=1):
        if all(self.judge_right(block) for block in self.blocks):
            update_blockset_col(self.blockset, step)
            for block in self.blocks:
                block.col += 1

    def move_left(self, step=-1):
        if all(self.judge_left(block) for block in self.blocks):
            update_blockset_col(self.blockset, step)
            for block in self.blocks:
                block.col -= 1

    def move_down(self, step=1):
        if all(self.judge_down(block) for block in self.blocks):
            update_blockset_row(self.blockset, step)
            for block in self.blocks:
                block.row += step

    def move_up(self):
        self.update_row(-1)
        for block in self.blocks:
            block.row -= 1

    def judge_rotate(self, rotated_pos):
        """Check whether blocks can be rotated or not.
           Args:
                rotated_pos: list, the positions after rotated
        """
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
            self.rotate_sound.play()
            self.index = next_index
            for block, (row, col) in zip(self.blocks, rotated_pos):
                block.row = row
                block.col = col - over

    def click(self, x, y):
        """Changes status, when a button is clicked.
        """
        # stop button on play screen
        if self.status == Status.PLAY and \
                self.stop_button.rect.collidepoint(x, y):
            self.status = Status.START
        # pause button on play screen
        elif self.status == Status.PLAY and \
                self.pause_button.rect.collidepoint(x, y):
            self.update_before_pause = self.update
            self.status = Status.PAUSE
        # restart button on pause screen
        elif self.status == Status.PAUSE and \
                self.restart_button.rect.collidepoint(x, y):
            self.status = Status.PLAY
            self.update = self.update_before_pause
        # start button on start screen
        elif self.status == Status.START and \
                self.start_button.rect.collidepoint(x, y):
            self.initialize()
        # repeat button on gameover screen
        elif self.status == Status.REPEAT and \
                self.repeat_button.rect.collidepoint(x, y):
            self.gameover_screen.initialize()
            self.initialize()


class Block(pygame.sprite.Sprite):

    def __init__(self, filename, row, col):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
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

    def __init__(self, file_path, screen):
        super().__init__(self.containers)
        self.image = pygame.image.load(file_path).convert()
        self.image = pygame.transform.scale(self.image, (100, 5))
        self.rect = self.image.get_rect()
        self.rect.left = NEXT_BLOCK_AREA_LEFT
        self.rect.bottom = NEXT_BLOCK_AREA_BOTTOM
        self.sysfont = pygame.font.SysFont(None, 30)
        self.screen = screen
        self.assemble_blocks()

    def assemble_blocks(self):
        self.images = {}
        for i, blockset in enumerate(BLOCKSETS):
            self.images[i] = tuple(
                pygame.image.load(blockset.file.path).convert() for _ in range(4))

    def update(self):
        text = self.sysfont.render(
            'NEXT', True, COLOR_WHITE)
        self.screen.blit(text, (NEXT_TEXT_X, NEXT_TEXT_Y))

        for block, (row, col) in zip(self.next_blocks, self.positions):
            self.screen.blit(
                block, (DISPLAY_X + col * BLOCK_SIZE, DISPLAY_Y + row * BLOCK_SIZE))

    def set_images(self, blockset_index):
        self.next_blocks = self.images[blockset_index]
        blockset = BLOCKSETS[blockset_index]
        self.positions = blockset.next


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
        self.rect.centerx = center_x
        self.rect.centery = center_y


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
        for file in ImageFiles:
            if pattern.match(file.value):
                yield pygame.image.load(file.path).convert()

    def draw_text(self):
        text = self.pause_sysfont.render('PAUSE', True, COLOR_WHITE)
        self.screen.blit(text, (PAUSE_TEXT_X, PAUSE_TEXT_Y))

    def draw_image(self):
        self.timer -= 1
        if self.timer == 0:
            if self.index >= self.images_count:
                self.index = 0
            self.image = self.images[self.index]
            self.index += 1
            self.timer = 20

    def update(self):
        self.draw_image()
        self.draw_text()


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

    def draw_text(self):
        self.timer -= 1
        if self.timer == 0:
            self.index += 1
            if self.index >= len(self.message_size):
                self.index = -1
            self.timer = 20

        size = self.message_size[self.index]
        message_font = pygame.font.SysFont(None, self.message_size[self.index])
        message = message_font.render('START', True, COLOR_PINK)
        delta = 10 if size == 50 else 0
        self.screen.blit(message, (START_TEXT_X - delta, START_TEXT_Y))
        title = self.title_font.render('TETRIS', True, COLOR_WHITE)
        self.screen.blit(title, (TITLE_X, TITLE_Y))

    def update(self):
        self.draw_text()


class GameOver(pygame.sprite.Sprite):

    def __init__(self, file_path, screen, game):
        super().__init__(self.containers)
        self.screen = screen
        self.game = game
        self.image = pygame.image.load(file_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.index = -1
        self.message_size = (40, 50, 40)
        self.initialize()

    def initialize(self):
        self.status = None
        self.timer = 100
        self.top = 0
        self.is_drop = True
        self.stop = 0

    def draw_text(self):
        self.timer -= 1
        if self.timer == 0:
            self.index += 1
            if self.index >= len(self.message_size):
                self.index = -1
            self.timer = 20

        size = self.message_size[self.index]
        message_font = pygame.font.SysFont(None, self.message_size[self.index])
        message = message_font.render('REPEAT', True, COLOR_WHITE)
        delta = 10 if size == 50 else 0
        self.screen.blit(message, (REPEAT_TEXT_X - delta, REPEAT_TEXT_Y))

    def draw_image(self):
        if self.stop <= 2:
            if self.is_drop:
                if self.top <= GAMEOVER_TOP:
                    self.top += 20
                else:
                    self.stop += 1
                    self.is_drop = False
            if self.stop == 1 and not self.is_drop:
                if self.top >= GAMEOVER_BOUND_TOP:
                    self.top -= 5
                else:
                    self.is_drop = True
        self.rect.left = GAMEOVER_LEFT
        self.rect.top = self.top

    def update(self):
        if self.status == Status.REPEAT:
            self.draw_text()
        self.draw_image()
        if self.status != Status.REPEAT:
            self.timer -= 1
            if self.timer == 0:
                self.timer = 20
                self.game.status = Status.REPEAT
                self.status = Status.REPEAT


class Score:

    def __init__(self, screen):
        self.sysfont = pygame.font.SysFont(None, 30)
        self.screen = screen
        self.initialize()

    def initialize(self):
        self.level = 1
        self.lines = 0
        self.score = 0

    def draw(self):
        score_area_y = SCORE_AREA_Y
        for text, num in zip(['LEVEL', 'LINES', 'SCORE'], [f'{self.level}', f'{self.lines}', f'{self.score}']):
            line_1 = self.sysfont.render(text, True, COLOR_WHITE)
            line_2 = self.sysfont.render(num, True, (250, 102, 14))
            self.screen.blit(line_1, (SCORE_AREA_X, score_area_y))
            score_area_y += 20
            self.screen.blit(line_2, (SCORE_AREA_X, score_area_y))
            score_area_y += 40

    def add(self, deleted_rows):
        """Compute lines, level and score.
           Args:
                deleted_rows: int, the number of deleted lines of blocks.

           Clearing 10 lines brings the level up. The level starts with 1.
           Scoring:
                1 line   40 * level
                2 lines  100 * level
                3 lines  300 * level
                4 lines  400 * level
        """
        self.lines += deleted_rows
        self.level = self.lines // 10 + 1

        if deleted_rows == 1:
            self.score += 40 * self.level
        elif deleted_rows == 2:
            self.score += 100 * self.level
        elif deleted_rows == 3:
            self.score += 300 * self.level
        else:
            self.score += 1200 * self.level


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    play = pygame.sprite.RenderUpdates()
    pause = pygame.sprite.RenderUpdates()
    start = pygame.sprite.RenderUpdates()
    gameover = pygame.sprite.RenderUpdates()
    repeat = pygame.sprite.RenderUpdates()
    Block.containers = play
    Plate.containers = play
    NextBlockDisplay.containers = play
    StopButton.containers = play
    Pause.containers = pause
    RestartButton.containers = pause
    Start.containers = start
    StartButton.containers = start
    GameOver.containers = gameover
    RepeatButton.containers = repeat

    tetris = PyTetris(screen)
    clock = pygame.time.Clock()
    pygame.key.set_repeat(500, 100)

    while True:
        clock.tick(60)
        screen.fill(COLOR_GREEN)

        if tetris.status == Status.PLAY:
            tetris.update()
            play.update()
            play.draw(screen)
            tetris.score.draw()
        elif tetris.status == Status.PAUSE:
            pause.update()
            pause.draw(screen)
        elif tetris.status == Status.START:
            start.update()
            start.draw(screen)
        elif tetris.status == Status.GAMEOVER:
            play.update()
            tetris.score.draw()
            play.draw(screen)
            gameover.update()
            gameover.draw(screen)
        elif tetris.status == Status.REPEAT:
            gameover.update()
            gameover.draw(screen)
            repeat.update
            repeat.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                tetris.click(*event.pos)
            if tetris.status == Status.PLAY and tetris.block_status == Status.DROPPING:
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


if __name__ == '__main__':
    main()
