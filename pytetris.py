import pygame
import sys
from collections import namedtuple
from pygame.locals import *

SCREEN = Rect(0, 0, 700, 500)
BLOCK_AREA_LEFT = 100
BLOCK_AREA_RIGHT = 350
BLOCK_AREA_BOTTOM = 470


Shaped = namedtuple('Shaped', 'filename coordinates')
BLUE = Shaped('images/red25.png', [[225, 100], [225, 125], [225, 150], [225, 175]])


class LineShaped:

    def __init__(self):
        self.blocks = [block for block in self.initialize()]
        self.sort_blocks()

    def initialize(self):
        for x, y in BLUE.coordinates:
            yield Block(BLUE.filename, x, y)

    def sort_blocks(self):
        self.blocks.sort(key=lambda block: block.y, reverse=True)
        max_y = self.blocks[0].y
        self.bottoms = [block for block in self.blocks if block.y == max_y]
        self.tops = [block for block in self.blocks if block.y != max_y]

    def move_right(self):
        for block in self.blocks:
            block.move_right()

    def move_left(self):
        for block in self.blocks:
            block.move_left()

    def move_down(self):
        for bottom_block in self.bottoms:
            bottom_block.move_down()
        for top_block in self.tops:
            if bottom_block.stop:
                top_block.stop = True
            else:
                top_block.move_down()


class Block(pygame.sprite.Sprite):

    SPEED = 1

    def __init__(self, filename, x, y):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.stop = False
        # self.rect.left = x
        # self.rect.top = y

    def update(self):
        if self.rect.bottom <= BLOCK_AREA_BOTTOM and not self.stop:
            self.y += self.SPEED
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def move_right(self):
        if self.rect.right > BLOCK_AREA_RIGHT:
            self.x = BLOCK_AREA_RIGHT
        else:
            self.x += 25

    def move_left(self):
        if self.rect.left < BLOCK_AREA_LEFT:
            self.x = BLOCK_AREA_LEFT
        else:
            self.x -= 25

    def move_down(self):
        if self.rect.bottom > BLOCK_AREA_BOTTOM:
            self.y = BLOCK_AREA_BOTTOM
            self.stop = True
        else:
            self.y += 25



def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    group = pygame.sprite.RenderUpdates()
    blocks = pygame.sprite.Group()
    # LineShaped.containers = group, blocks
    Block.containers = group, blocks
    clock = pygame.time.Clock()
    # block = Block('images/red25.png', 300, 0)
    block = LineShaped()

    while True:
        clock.tick(60)
        # pygame.key.set_repeat(10)
        screen.fill((0, 100, 0))
        group.update()
        group.draw(screen)

        pygame.display.update() 
  

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    block.move_right()
                if event.key == K_LEFT:
                    block.move_left()
                if event.key == K_DOWN:
                    block.move_down()



if __name__ == '__main__':
    main()