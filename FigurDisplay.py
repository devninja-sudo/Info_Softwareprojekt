import pygame
from sys import exit


class FigurDisplay(pygame.sprite.Sprite):
    def __init__(self, image:str, size:int, field_length:int, teamID:int, canJump:bool):
        super().__init__()

        self.__imagePath = image
        self.__field_length = field_length
        self.__centerPos = (self.__field_length/2, self.__field_length/2)
        self.__team = teamID


        self.image = pygame.image.load(self.__imagePath).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))

        self.rect = self.image.get_rect(center = self.__centerPos)

        self.__canJump = canJump

    def getTeam(self)->int:
        return self.__team

    
    def getCanJump(self):
        return self.__canJump


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Figur Test')
    clock = pygame.time.Clock()


    TestSpringerGroup = pygame.sprite.GroupSingle()
    TestSpringerGroup.add(FigurDisplay("assets/graphics/s_springer.png", 80, 200, 1))
    
    while True:
        screen.fill("white")
        for event in pygame.event.get():
	        if event.type == pygame.QUIT:
                  pygame.quit()
                  exit()
        TestSpringerGroup.draw(screen)
        TestSpringerGroup.update()
        pygame.display.update()
        clock.tick(60)