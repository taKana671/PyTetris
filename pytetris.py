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
BLOCK_AREA_BOTTOM = 495
BLOCK_AREA_TOP = 100

COLS = 10   # the number of columns
ROWS = 20  # the number of rows
BLOCK_SIZE = 20


BlockSet = namedtuple('BlockSet', 'filename coordinates')

BLUE = BlockSet('images/blue25.png', [[[-1, 4], [0, 4], [1, 4], [2, 4]], [[-1, 4], [-1, 5], [-1, 6], [-1, 7]], [[-1, 4], [0, 4], [1, 4], [2, 4]], [[-1, 4], [-1, 5], [-1, 6], [-1, 7]]])
DARK = BlockSet('images/dark25.png', [[[-1, 3], [0, 3], [0, 4], [0, 5]], [[-1, 4], [-1, 5], [0, 4], [1, 4]], [[-1, 3], [-1, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [1, 4], [1, 3]]])
GREEN = BlockSet('images/green25.png', [[[-1, 4], [-1, 5], [0, 3], [0, 4]], [[-1, 3], [0, 3], [0, 4], [1, 4]], [[-1, 4], [-1, 5], [0, 3], [0, 4]], [[-1, 3], [0, 3], [0, 4], [1, 4]]])
ORANGE = BlockSet('images/orange25.png', [[[-1, 5], [0, 3], [0, 4], [0, 5]], [[-1, 4], [0, 4], [1, 4], [1, 5]], [[-1, 3], [-1, 4], [-1, 5], [0, 3]], [[-1, 3], [-1, 4], [0, 4], [1, 4]]])
PURPLE = BlockSet('images/purple25.png', [[[-1, 4], [0, 3], [0, 4], [0, 5]], [[-1, 4], [0, 4], [0, 5], [1, 4]], [[-1, 3], [-1, 4], [-1, 5], [0, 4]], [[-1, 4], [0, 3], [0, 4], [1, 4]]])
RED = BlockSet('images/red25.png', [[[-1, 3], [-1, 4], [0, 4], [0, 5]], [[-1, 4], [0, 3], [0, 4], [1, 3]], [[-1, 3], [-1, 4], [0, 4], [0, 5]], [[-1, 4], [0, 3], [0, 4], [1, 3]]])
YELLOW = BlockSet('images/yellow25.png', [[[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]]])
BLOCKSETS = [BLUE, DARK, GREEN, ORANGE, PURPLE, RED, YELLOW]
# BLOCKSETS = [BLUE]


logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='test.log')
logger.addHandler(handler)


class PyTetris:

    def __init__(self, screen):

        self.matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.screen = screen
        self.index = 0
        self.timer = 20
        self.start()
        self.update = self.move

    def start(self):
        index = random.randint(0, len(BLOCKSETS) - 1)
        block_set = BLOCKSETS[index]
        self.blocks = []
        for row, col in block_set.coordinates[0]:
            block = Block(block_set.filename, row, col)
            self.blocks.append(block)
        self.block_set = copy.deepcopy(block_set.coordinates)

    def move(self):
        self.timer -= 1
        if self.timer == 0:
            self.move_down()
            self.timer = 20

        for block in self.blocks:
            block.rect.centerx = BLOCK_AREA_LEFT + block.col * BLOCK_SIZE
            block.rect.centery = BLOCK_AREA_TOP + block.row * BLOCK_SIZE

        if any(self.judge_ground(block) for block in self.blocks):
            self.update_matrix()

            # if any(all(row) for row in self.matrix):
            #     self.update = self.delete_blocks
            # Game over
            if any(block for block in self.matrix[0]):
                self.update = self.game_over
            else:
                self.start()
                self.move_down()
                self.timer = 1
                # for block in self.blocks:
                #     block.rect.centerx = BLOCK_AREA_LEFT + block.col * BLOCK_SIZE
                #     block.rect.centery = BLOCK_AREA_TOP + block.row * BLOCK_SIZE

    def check_matrix(self, block, new_row, new_col):
        # Check whether the block is not contained in self.blocks.
        if (new_row, new_col) not in self.block_set[self.index]:
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

    def delete_blocks(self):
        for row in self.matrix:
            if all(row):
                for i, block in enumerate(row):
                    row[i] = block.kill()

        if remainings := [row for row in self.matrix if any(row)]:
            self.matrix = [[None for _ in range(COLS)] for _ in range(ROWS - len(remainings))] + remainings
            for i, row in enumerate(self.matrix):
                for block in row:
                    if block:
                        block.row = i - 1
                        block.rect.centerx = BLOCK_AREA_LEFT + block.col * BLOCK_SIZE
                        block.rect.centery = BLOCK_AREA_TOP + block.row * BLOCK_SIZE
        self.update = self.move

    def update_matrix(self):
        for block in self.blocks:
            self.matrix[block.row][block.col] = block

    def update_matrix_row(self, step):
        for block in self.block_set:
            for row_col in block:
                row_col[0] += step

    def update_matrix_col(self, step):
        for block in self.block_set:
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

    def rotate(self):
        self.index += 1
        if self.index > 3:
            self.index = 0
        position = self.block_set[self.index]
        for block, (row, col) in zip(self.blocks, position):
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
        self.image = pygame.transform.scale(self.image, (200, 5))
        self.rect = self.image.get_rect()
        self.rect.left = BLOCK_AREA_LEFT - 10
        self.rect.bottom = BLOCK_AREA_BOTTOM


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    group = pygame.sprite.RenderUpdates()
    Block.containers = group
    Plate.containers = group

    plate = Plate('images/plate.png')

    tetris = PyTetris(screen)

    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
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
