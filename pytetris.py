import logging

import pygame
import sys
from collections import namedtuple
from pygame.locals import *

SCREEN = Rect(0, 0, 700, 600)
BLOCK_AREA_LEFT = 100
BLOCK_AREA_RIGHT = 300
BLOCK_AREA_BOTTOM = 430
BLOCK_AREA_TOP = 20

COLS = 10   # the number of columns
ROWS = 20  # the number of rows
BLOCK_SIZE = 20


Shaped = namedtuple('Shaped', 'filename coordinates')
BLUE = Shaped('images/red25.png', [[0, 4], [1, 4], [2, 4], [3, 4]])


logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='test.log')
logger.addHandler(handler)


class LineShaped:

    def __init__(self):
        # super().__init__(self.containers)
        # self.block_group = block_group
        self.blocks = pygame.sprite.Group()
        self.initialize()
        # self.blocks = [block for block in self.initialize()]

    def initialize(self):
        for row, col in BLUE.coordinates:
            block = Block(BLUE.filename, row, col)
            self.blocks.add(block)
            # yield block
            # yield Block(BLUE.filename, x, y)

    def update(self):
        if any(block.col >= COLS for block in self.blocks.sprites()):
            self.move_left()
        if any(block.col < 0 for block in self.blocks.sprites()):
            self.move_right()
        if any(block.row > ROWS for block in self.blocks.sprites()):
            self.move_up()
        for block in self.blocks.sprites():
            block.rect.centerx = BLOCK_AREA_LEFT + block.col * BLOCK_SIZE
            block.rect.centery = BLOCK_AREA_TOP + block.row * BLOCK_SIZE
       
        if all(block.row <= ROWS for block in self.blocks.sprites()):
            self.move_down()

    def move_right(self):
        for block in self.blocks.sprites():
            block.col += 1
 
    def move_left(self):
        for block in self.blocks.sprites():
            block.col -= 1

    def move_down(self):
        for block in self.blocks.sprites():
            block.row += 1

    def move_up(self):
        for block in self.blocks.sprites():
            block.row -= 1

    def rotate(self):
        pass


class Block(pygame.sprite.Sprite):

    def __init__(self, filename, row, col):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.row = row
        self.col = col
        self.stop = False


    # def update(self):
    #     self.rect.centerx = BLOCK_AREA_LEFT + self.col * BLOCK_SIZE
    #     self.rect.centery = BLOCK_AREA_TOP + self.row * BLOCK_SIZE



class Plate(pygame.sprite.Sprite):

    def __init__(self, filename):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, (250, 5))
        self.rect = self.image.get_rect()
        self.rect.left = BLOCK_AREA_LEFT
        self.rect.top = BLOCK_AREA_BOTTOM


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    group = pygame.sprite.RenderUpdates()
    # blocks = pygame.sprite.Group()


    matrix = [[None for _ in range(COLS)] for _ in range(ROWS)]

    # Block.containers = group, blocks
    Block.containers = group
    Plate.containers = group
    # LineShaped.containers = group

    plate = Plate('images/plate.png')
    # block_group = pygame.sprite.Group()

    # for row, col in BLUE.coordinates:
    #     block = Block(BLUE.filename, row, col)
    #     block_group.add(block)

    # for s in block_group.sprites():
    #     logger.info(f'{s.__dict__}')

    tetris = LineShaped()

    clock = pygame.time.Clock()
    

    while True:
        clock.tick(5)
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
                    # tetris.rorate()
                    pass

     


if __name__ == '__main__':
    main()
