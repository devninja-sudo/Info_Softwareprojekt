import pygame
from sys import exit
from FigurBuilder import FigurBuilder

class Koenig(FigurBuilder):
    def __init__(self, image:str, size:int, field_length:int, field_count:int, fieldLabelStartLetter:str, teamID:int, mustKill:bool=False):
        super().__init__(image, size, field_length, field_count, fieldLabelStartLetter, teamID, True)

        self.__mustKill:bool = mustKill
        self.__canKill:bool = True


        self.__hasAnxiety:bool = True
        self.setKingRole(True)
        self.__hasMoved:bool = False
        


    def getMaybePossibleTurns(self, originFieldLabel:str)->list[dict]:
        possibleTurns = []
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if i == 0 and j == 0:
                    continue
                possibleTurns = self.getNewZugListWithAddingRelative(originFieldLabel, possibleTurns, (i, j), self.__mustKill, self.__canKill, self.__hasAnxiety)
        return possibleTurns
    
    def Moved(self):
        self.__hasMoved = True


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Koenig Test')
    clock = pygame.time.Clock()


    TestKoenigGroup = pygame.sprite.GroupSingle()
    TestKoenig = Koenig("assets/graphics/s_koenig.png", 80, 400, 8, "a", 1)
    TestKoenigGroup.add(TestKoenig)
    print(TestKoenig.getMaybePossibleTurns("a1"))
    while True:
        screen.fill("white")
        for event in pygame.event.get():
	        if event.type == pygame.QUIT:
                  pygame.quit()
                  exit()
        TestKoenigGroup.draw(screen)
        TestKoenigGroup.update()
        pygame.display.update()
        clock.tick(60)
