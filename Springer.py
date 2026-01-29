import pygame
from sys import exit
from FigurDisplay import FigurDisplay

class Springer(FigurDisplay):
    def __init__(self, image:str, size:int, field_length:int, teamID:int):
        super().__init__(image, size, field_length, teamID, True)

        self.__SchrittLaenge = 1
        self.__SchrittBreite = 2
        



    def getRelativeMaybePossibleTurns(self, FieldLabel):
        possibleZuege = []
        
        for i in [-1, 1]:
            for j in [-1, 1]:
                possibleZuege.append((self.__SchrittLaenge*i, self.__SchrittBreite*j))
                possibleZuege.append((self.__SchrittBreite*i, self.__SchrittLaenge*j))
        return possibleZuege
    


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Springer Test')
    clock = pygame.time.Clock()


    TestSpringerGroup = pygame.sprite.GroupSingle()
    TestSpringer = Springer("assets/graphics/s_springer.png", 80, 400, 1)
    TestSpringerGroup.add(TestSpringer)
    print(TestSpringer.gibRelativePossibleTurns())
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
