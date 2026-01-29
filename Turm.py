import pygame
from sys import exit
from FigurDisplay import FigurDisplay

class Turm(FigurDisplay):
    def __init__(self, image:str, size:int, field_length:int, teamID:int):
        super().__init__(image, size, field_length, teamID, False)



    def getRelativeMaybePossibleTurns(self, FieldLabel):
        possibleZuege = []
        
        for i in range(1, 8):
            possibleZuege.append((i, 0))
            possibleZuege.append((-i, 0))
            possibleZuege.append((0, i))
            possibleZuege.append((0, -i))
        return possibleZuege
    

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Turm Test')
    clock = pygame.time.Clock()


    TestTurmGroup = pygame.sprite.GroupSingle()
    TestTurm = Turm("assets/graphics/s_turm.png", 80, 400, 1)
    TestTurmGroup.add(TestTurm)
    print(TestTurm.gibRelativePossibleTurns())
    while True:
        screen.fill("white")
        for event in pygame.event.get():
	        if event.type == pygame.QUIT:
                  pygame.quit()
                  exit()
        TestTurmGroup.draw(screen)
        TestTurmGroup.update()
        pygame.display.update()
        clock.tick(60)
