import pygame
from sys import exit
from FigurDisplay import FigurDisplay

class Laeufer(FigurDisplay):
    def __init__(self, image:str, size:int, field_length:int, teamID:int, mustKill:bool=False):
        super().__init__(image, size, field_length, teamID, False)
        self.__mustKill = mustKill



    def getRelativeMaybePossibleTurns(self, FieldLabel):
        possibleZuege = []
        
        for i in range(1, 8):
            for directionPoint in [(i, i), (-i, i), (-i, -i), (i, -i)]:
                    possibleZuege = self.getNewZugListWithAdd(possibleZuege, directionPoint, self.__mustKill)
        return possibleZuege
    

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Laeufer Test')
    clock = pygame.time.Clock()


    TestLaeuferGroup = pygame.sprite.GroupSingle()
    TestLaeufer = Laeufer("assets/graphics/s_turm.png", 80, 400, 1)
    TestLaeuferGroup.add(TestLaeufer)
    print(TestLaeufer.getRelativeMaybePossibleTurns("a1"))
    while True:
        screen.fill("white")
        for event in pygame.event.get():
	        if event.type == pygame.QUIT:
                  pygame.quit()
                  exit()
        TestLaeuferGroup.draw(screen)
        TestLaeuferGroup.update()
        pygame.display.update()
        clock.tick(60)
