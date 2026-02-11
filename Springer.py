import pygame
from sys import exit
from FigurBuilder import FigurBuilder

class Springer(FigurBuilder):
    def __init__(self, image:str, size:int, field_length:int, field_count:int, fieldLabelStartLetter:str, teamID:int, mustKill:bool=False):
        super().__init__(image, size, field_length, field_count, fieldLabelStartLetter, teamID, True)

        self.__SchrittLaenge = 1
        self.__SchrittBreite = 2

        self.__mustKill = mustKill
        



    def getMaybePossibleTurns(self, originFieldLabel:str)->list[dict]:
        possibleZuege = []
        
        for i in [-1, 1]:
            for j in [-1, 1]:
                possibleZuege = self.gebeNeueZuglisteMitNeuemZug(originFieldLabel, possibleZuege, (self.__SchrittLaenge*i, self.__SchrittBreite*j), self.__mustKill)
                possibleZuege = self.gebeNeueZuglisteMitNeuemZug(originFieldLabel, possibleZuege, (self.__SchrittBreite*i, self.__SchrittLaenge*j), self.__mustKill)
        return possibleZuege
    


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Springer Test')
    clock = pygame.time.Clock()


    TestSpringerGroup = pygame.sprite.GroupSingle()
    TestSpringer = Springer("assets/graphics/s_springer.png", 80, 400, 1)
    TestSpringerGroup.add(TestSpringer)
    print(TestSpringer.getMaybePossibleTurns("a1"))
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
