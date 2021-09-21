import pygame
import sys
from collections import namedtuple
from pygame.locals import *

SCREEN = Rect(0, 0, 700, 600)
BLOCK_AREA_LEFT = 100
BLOCK_AREA_RIGHT = 300
BLOCK_AREA_BOTTOM = 430


Shaped = namedtuple('Shaped', 'filename coordinates')
BLUE = Shaped('images/red25.png', [[200, 20], [200, 40], [200, 60], [200, 80]])


class LineShaped:

    def __init__(self, blocks, plate):
        self.group = blocks
        self.plate = plate
        self.blocks = [block for block in self.initialize()]

    def initialize(self):
        for x, y in BLUE.coordinates:
            block = Block(BLUE.filename, x, y)
            self.group.add(block)
            yield block
            # yield Block(BLUE.filename, x, y)

    def move_right(self):
        for block in self.blocks:
            block.move_right()

    def move_left(self):
        for block in self.blocks:
            block.move_left()

    def move_down(self):
        is_collide = pygame.sprite.spritecollideany(self.plate, self.group)
        coords = [340, 360, 380, 400]
        for i, block in enumerate(self.blocks):
            block.move_down(is_collide, coords[i])

    def stop(self):
        if pygame.sprite.spritecollideany(self.plate, self.blocks):
            for block in self.blocks:
                block.stop()


    def rotate(self):
        pass


class Block(pygame.sprite.Sprite):

    SPEED = 1

    def __init__(self, filename, x, y):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.stop = False

        # self.rect.left = x
        # self.rect.top = y

    def update(self):
        # if self.rect.bottom < BLOCK_AREA_BOTTOM and not self.stop:
        if not self.stop and self.rect.bottom < BLOCK_AREA_BOTTOM:
            self.y += self.SPEED
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def move_right(self):
        if self.rect.right > BLOCK_AREA_RIGHT:
            self.x = BLOCK_AREA_RIGHT
        elif not self.stop:
            self.x += 20

    def move_left(self):
        if self.rect.left < BLOCK_AREA_LEFT:
            self.x = BLOCK_AREA_LEFT
        elif not self.stop:
            self.x -= 20

    def move_down(self, is_collide, y):
        if is_collide:
            self.stop = True
            self.y = y
            # self.y = self.rect.centery
        elif not self.stop:
            self.y += 20
        # if self.rect.bottom >= BLOCK_AREA_BOTTOM:
        #     self.y = BLOCK_AREA_BOTTOM
        #     self.stop = True
        # elif not self.stop:
        #     self.y += 25

    def stop(self):
        self.stop = True
        self.y = self.rect.centery

    def rotate(self):
        pass


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
    blocks = pygame.sprite.Group()
    # Block.containers = group, blocks
    Block.containers = group
    Plate.containers = group
    clock = pygame.time.Clock()
    # block = Block('images/red25.png', 300, 0)
    plate = Plate('images/plate.png')
    block = LineShaped(blocks, plate)
    # block = LineShaped()

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
                if event.key == K_UP:
                    # block.rorate()
                    pass

        if pygame.sprite.spritecollideany(plate, blocks):
            for b in block.blocks:
                b.stop = True

        


if __name__ == '__main__':
    main()
