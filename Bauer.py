import pygame
from sys import exit
from FigurBuilder import FigurBuilder

class Bauer(FigurBuilder):
    def __init__(self, image:str, size:int, field_length:int, field_count:int, fieldLabelStartLetter:str, teamID:int, mustKill:bool=False):
        super().__init__(image, size, field_length, field_count, fieldLabelStartLetter, teamID, False)
        self.__mustKill = mustKill



    def getMaybePossibleTurns(self, originFieldLabel:str)->list[dict]:
        possibleZuege = []
        if self.getTeam() == 0:
            direction = 1
        else:
            direction = -1
        possibleZuege = self.getNewZugListWithAddingRelative(originFieldLabel, possibleZuege, (0, 1*direction), self.__mustKill, False)
        if int(originFieldLabel[1]) == 2 and direction == 1:
            possibleZuege = self.getNewZugListWithAddingRelative(originFieldLabel, possibleZuege, (0, 2*direction), self.__mustKill, False)
        elif int(originFieldLabel[1]) == 7 and direction == -1:
            possibleZuege = self.getNewZugListWithAddingRelative(originFieldLabel, possibleZuege, (0, 2*direction), self.__mustKill, False)

        possibleZuege = self.getNewZugListWithAddingRelative(originFieldLabel, possibleZuege, (1, 1*direction), True, True)
        possibleZuege = self.getNewZugListWithAddingRelative(originFieldLabel, possibleZuege, (-1, 1*direction), True, True)
        
        return possibleZuege

    

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Laeufer Test')
    clock = pygame.time.Clock()


    TestBauerGroup = pygame.sprite.GroupSingle()
    BauerDame = Bauer("assets/graphics/s_bauer.png", 80, 400, 1)
    TestBauerGroup.add(BauerDame)
    print(BauerDame.getMaybePossibleTurns("a1"))
    while True:
        screen.fill("white")
        for event in pygame.event.get():
	        if event.type == pygame.QUIT:
                  pygame.quit()
                  exit()
        TestBauerGroup.draw(screen)
        TestBauerGroup.update()
        pygame.display.update()
        clock.tick(60)
