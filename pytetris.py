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

SCORE_AREA_X = 390
SCORE_AREA_Y = 350

NEXT_BLOCK_AREA_LEFT = 410
NEXT_BLOCK_AREA_BOTTOM = 200
DISPLAY_X = 410
DISPLAY_Y = 100
NEXT_TEXT_X = 440
NEXT_TEXT_Y = 80


COLS = 10   # the number of columns
ROWS = 20  # the number of rows
BLOCK_SIZE = 20


BlockSet = namedtuple('BlockSet', 'filename next coordinates')

BLUE = BlockSet('images/blue25.png', [[1, 2.5], [2, 2.5], [3, 2.5], [4, 2.5]],
                [[[-1, 4], [0, 4], [1, 4], [2, 4]], [[-1, 4], [-1, 5], [-1, 6], [-1, 7]], [[-1, 4], [0, 4], [1, 4], [2, 4]], [[-1, 4], [-1, 5], [-1, 6], [-1, 7]]])
DARK = BlockSet('images/dark25.png', [[2, 1.5], [3, 1.5], [3, 2.5], [3, 3.5]],
                [[[-1, 3], [0, 3], [0, 4], [0, 5]], [[-1, 4], [0, 4], [1, 4], [1, 3]], [[-1, 3], [-1, 4], [-1, 5], [0, 5]], [[-1, 4], [-1, 5], [0, 4], [1, 4]]])
GREEN = BlockSet('images/green25.png', [[2, 1.5], [2, 2.5], [3, 2.5], [3, 3.5]],
                 [[[-1, 4], [-1, 5], [0, 3], [0, 4]], [[-1, 3], [0, 3], [0, 4], [1, 4]], [[-1, 4], [-1, 5], [0, 3], [0, 4]], [[-1, 3], [0, 3], [0, 4], [1, 4]]])
ORANGE = BlockSet('images/orange25.png', [[2, 3.5], [3, 1.5], [3, 2.5], [3, 3.5]],
                  [[[-1, 5], [0, 3], [0, 4], [0, 5]], [[-1, 3], [-1, 4], [0, 4], [1, 4]], [[-1, 3], [-1, 4], [-1, 5], [0, 3]], [[-1, 4], [0, 4], [1, 4], [1, 5]]])
PURPLE = BlockSet('images/purple25.png', [[2, 2.5], [3, 1.5], [3, 2.5], [3, 3.5]],
                  [[[-1, 4], [0, 3], [0, 4], [0, 5]], [[-1, 4], [0, 4], [1, 4], [0, 3]], [[-1, 3], [-1, 4], [-1, 5], [0, 4]], [[-1, 4], [0, 4], [1, 4], [0, 5]]])
RED = BlockSet('images/red25.png', [[2, 2.5], [2, 3.5], [3, 1.5], [3, 2.5]],
               [[[-1, 3], [-1, 4], [0, 4], [0, 5]], [[-1, 4], [0, 3], [0, 4], [1, 3]], [[-1, 3], [-1, 4], [0, 4], [0, 5]], [[-1, 4], [0, 3], [0, 4], [1, 3]]])
YELLOW = BlockSet('images/yellow25.png', [[2, 2], [2, 3], [3, 2], [3, 3]],
                  [[[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]], [[-1, 4], [0, 4], [-1, 5], [0, 5]]])

BLOCKSETS = [BLUE, DARK, GREEN, ORANGE, PURPLE, RED, YELLOW]


logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='test.log')
logger.addHandler(handler)


class PyTetris:

    def __init__(self, screen, score, next_block_display):
        self.screen = screen
        self.score = score
        self.next_block_display = next_block_display
        self.matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.index = 0
        self.drop_timer = 20
        self.ground_timer = 60
        self.judge_timer = 20
        self.next_bockset = None
        self.start()
        self.update = self.update_moving_block

    def get_blockset(self):
        index = random.randint(0, len(BLOCKSETS) - 1)
        blockset = BLOCKSETS[index]
        return blockset

    def start(self):
        if self.next_bockset is None:
            blockset = self.get_blockset()
        else:
            blockset = self.next_bockset
        self.next_bockset = self.get_blockset()
        self.next_block_display.show_next(self.next_bockset)
        self.blocks = [Block(blockset.filename, row, col) for row, col in blockset.coordinates[0]]
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
                    self.update = self.game_over
                else:
                    self.start()
                    self.drop_timer = 1

    def update_ground_blocks(self):
        self.ground_timer -= 1
        if self.ground_timer == 40:
            if deleted_rows := self.delete_blocks():
                self.score.add_score(self.calculate_score(deleted_rows))
        if self.ground_timer == 20:
            self.move_ground_blocks()
        if self.ground_timer == 0:
            self.start()
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


class NextBlockDisplay(pygame.sprite.Sprite):

    def __init__(self, filename, screen):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, (100, 5))
        self.rect = self.image.get_rect()
        self.rect.left = NEXT_BLOCK_AREA_LEFT
        self.rect.bottom = NEXT_BLOCK_AREA_BOTTOM
        self.sysfont = pygame.font.SysFont(None, 30)
        self.screen = screen
        self.next_blocks = None

    def draw(self):
        text = self.sysfont.render(
            'next', True, (255, 255, 250))
        self.screen.blit(text, (NEXT_TEXT_X, NEXT_TEXT_Y))

    def show_next(self, block_set):
        self.delete_blocks()
        self.next_blocks = [Block(block_set.filename, row, col) for row, col in block_set.next]
        for block in self.next_blocks:
            block.rect.centerx = DISPLAY_X + block.col * BLOCK_SIZE
            block.rect.centery = DISPLAY_Y + block.row * BLOCK_SIZE

    def delete_blocks(self):
        if self.next_blocks:
            for block in self.next_blocks:
                block.kill()


class Score(pygame.sprite.Sprite):

    def __init__(self, screen):
        self.sysfont = pygame.font.SysFont(None, 40)
        self.screen = screen
        self.score = 0

    def draw(self):
        text = self.sysfont.render(
            f'SCORE {self.score}', True, (255, 255, 250))
        self.screen.blit(text, (SCORE_AREA_X, SCORE_AREA_Y))

    def add_score(self, score):
        self.score += score


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    group = pygame.sprite.RenderUpdates()
    Block.containers = group
    Plate.containers = group
    NextBlockDisplay.containers = group

    # plate = Plate('images/plate.png')
    Plate('images/plate.png')

    score = Score(screen)
    next_display = NextBlockDisplay('images/plate.png', screen)
    tetris = PyTetris(screen, score, next_display)

    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        screen.fill((0, 100, 0))

        tetris.update()
        group.update()
        group.draw(screen)
        score.draw()
        next_display.draw()

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
