import pygame
from sys import exit

class Feld(pygame.sprite.Sprite):
    def __init__(self, size:tuple[int, int], topLeftCorner:tuple[int, int], color:str):
        super().__init__()

        self.color = color
        self.image = pygame.surface.Surface((size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft = topLeftCorner)
        self.effects = []
        self.figure = None

    def setFieldPosition(self, topLeftCorner:tuple[int, int]):
        self.rect.topleft = topLeftCorner

    def update(self):
        pass

    def getRect(self)->pygame.rect.Rect:
        return self.rect
        

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Feld Test')
    clock = pygame.time.Clock()


    TestFeldGroup = pygame.sprite.GroupSingle()
    TestFeldGroup.add(Feld((50, 50), (10, 10), "yellow"))
    
    while True:
        for event in pygame.event.get():
	        if event.type == pygame.QUIT:
                  pygame.quit()
                  exit()
        TestFeldGroup.draw(screen)
        TestFeldGroup.update()
        pygame.display.update()
        clock.tick(60)
