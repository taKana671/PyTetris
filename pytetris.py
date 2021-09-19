import pygame
import sys
from pygame.locals import *


SCREEN = Rect(0, 0, 700, 500)


class Block(pygame.sprite.Sprite):

    SPEED = 1

    def __init__(self, filename, x, y):
        super().__init__(self.containers)
        self.image = pygame.image.load(filename).convert()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y  
        # self.rect.left = x
        # self.rect.top = y

    def update(self):
        self.y += self.SPEED
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def move_right(self):
        if self.rect.right > SCREEN.right:
            self.x = SCREEN.right
        else:
            self.x += 25


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    group = pygame.sprite.RenderUpdates()
    blocks = pygame.sprite.Group()
    Block.containers = group, blocks
    clock = pygame.time.Clock()

    is_wait= True

    block = Block('images/red25.png', 300, 0)


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
                    pygame.display.update()





if __name__ == '__main__':
    main()