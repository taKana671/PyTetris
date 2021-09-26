import logging
import copy
import pygame
import random
import sys
from collections import namedtuple
from pygame.locals import *

SCREEN = Rect(0, 0, 700, 600)
BLOCK_AREA_LEFT = 100
BLOCK_AREA_RIGHT = 300
BLOCK_AREA_BOTTOM = 475
BLOCK_AREA_TOP = 100

COLS = 10   # the number of columns
ROWS = 20  # the number of rows
BLOCK_SIZE = 20


BlockSet = namedtuple('BlockSet', 'filename coordinates')


BLUE = BlockSet('images/blue25.png',
                [[[-1, 4], [0, 4], [1, 4], [2, 4]], [[0, 4], [0, 5], [0, 6], [0, 7]], [[-1, 4], [0, 4], [1, 4], [2, 4]], [[0, 4], [0, 5], [0, 6], [0, 7]]])
DARK = BlockSet('images/dark25.png', [[-1, 4], [0, 4], [1, 4], [1, 5]])
GREEN = BlockSet('images/green25.png', [[-1, 4], [-1, 5], [0, 3], [0, 4]])
ORANGE = BlockSet('images/orange25.png', [[-1, 4], [-1, 5], [0, 5], [1, 5]])
PURPLE = BlockSet('images/purple25.png', [[-1, 4], [0, 3], [0, 4], [0, 5]])
RED = BlockSet('images/red25.png', [[-1, 3], [-1, 4], [0, 4], [0, 5]])
YELLOW = BlockSet('images/yellow25.png', [[-1, 4], [-1, 5], [0, 4], [0, 5]])
# SHAPED_LIST = [BLUE, DARK, GREEN, ORANGE, PURPLE, RED, YELLOW]
BLOCKSETS = [BLUE]

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='test.log')
logger.addHandler(handler)


class PyTetris:

    def __init__(self, matrix, screen):
        self.matrix = matrix
        self.screen = screen
        self.stop = False
        self.toggle = 0
        self.timer = 20
        self.start()

    def start(self):
        index = random.randint(0, len(BLOCKSETS) - 1)
        block_set = BLOCKSETS[index]
        self.blocks = pygame.sprite.Group()
        for row, col in block_set.coordinates[0]:
            block = Block(block_set.filename, row, col)
            self.blocks.add(block)
        self.block_set = copy.deepcopy(block_set.coordinates)

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            if not self.stop:
                self.move_down()
                self.timer = 20
        if any(self.judge_right(block) for block in self.blocks.sprites()):
            self.move_left()
        if any(self.judge_left(block) for block in self.blocks.sprites()):
            self.move_right()
        if any(self.judge_down(block) for block in self.blocks.sprites()):
            self.move_up()
        if any(self.judge_ground(block) for block in self.blocks.sprites()):
            self.update_matrix()
            # Game over
            if any(block for block in self.matrix[0]):
                self.stop = True
                self.game_over()
            else:
                self.start()
        if not self.stop:
            for block in self.blocks.sprites():
                block.rect.centerx = BLOCK_AREA_LEFT + block.col * BLOCK_SIZE
                block.rect.centery = BLOCK_AREA_TOP + block.row * BLOCK_SIZE

    def judge_left(self, block):
        return block.col < 0 or self.matrix[block.row][block.col]

    def judge_right(self, block):
        return block.col >= COLS or self.matrix[block.row][block.col]

    def judge_down(self, block):
        return block.row >= ROWS or self.matrix[block.row][block.col]

    def judge_up(self, block):
        return block.row < 0

    def judge_ground(self, block):
        return block.row == ROWS - 1 or self.matrix[block.row + 1][block.col]

    def update_matrix(self):
        for block in self.blocks.sprites():
            self.matrix[block.row][block.col] = block

    def update_row(self, step):
        for block in self.block_set:
            for row_col in block:
                row_col[0] += step

    def update_col(self, step):
        for block in self.block_set:
            for row_col in block:
                row_col[1] += step

    def move_right(self):
        self.update_col(1)
        for block in self.blocks.sprites():
            block.col += 1

    def move_left(self):
        self.update_col(-1)
        for block in self.blocks.sprites():
            block.col -= 1

    def move_down(self, step=1):
        self.update_row(step)
        for block in self.blocks.sprites():
            block.row += step

    def move_up(self):
        self.update_row(-1)
        for block in self.blocks.sprites():
            block.row -= 1

    def rotate(self):
        self.toggle += 1
        if self.toggle > 3:
            self.toggle = 0
        position = self.block_set[self.toggle]
        for block, (row, col) in zip(self.blocks.sprites(), position):
            block.row = row
            block.col = col

    def game_over(self):
        self.sysfont = pygame.font.SysFont(None, 20)
        img = self.sysfont.render('Game over', True, (255, 255, 250))
        self.screen.blit(img, (400, 300))


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
        self.image = pygame.transform.scale(self.image, (250, 5))
        self.rect = self.image.get_rect()
        self.rect.left = BLOCK_AREA_LEFT
        self.rect.bottom = BLOCK_AREA_BOTTOM


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    group = pygame.sprite.RenderUpdates()

    matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]
    Block.containers = group
    Plate.containers = group

    plate = Plate('images/plate.png')

    tetris = PyTetris(matrix, screen)

    clock = pygame.time.Clock()

    while True:
        # clock.tick(5)
        clock.tick(60)
        # pygame.key.set_repeat(10)
        screen.fill((0, 100, 0))

        tetris.update()
        group.update()
        group.draw(screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    tetris.move_right()
                if event.key == K_LEFT:
                    tetris.move_left()
                if event.key == K_DOWN:
                    tetris.move_down()
                if event.key == K_UP:
                    tetris.rotate()

        # pygame.event.pump()
        # pressed = pygame.key.get_pressed()
        # if pressed[K_ESCAPE]:
        #     pygame.quit()
        #     sys.exit()
        # if pressed[K_RIGHT]:
        #     tetris.move_right()
        # if pressed[K_LEFT]:
        #     tetris.move_left()
        # if pressed[K_DOWN]:
        #     tetris.move_down()
        # if pressed[K_UP]:
        #     tetris.rotate()


if __name__ == '__main__':
    main()
