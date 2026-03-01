import pygame
from sys import exit
from FigurBuilder import FigurBuilder

class Turm(FigurBuilder):
    '''
    Vor.: -image- ist vom Typstring, welcher den Pfad beschreibt, welche Textur der Turm besitzt. Die Textur ist im PNG Format an dem angegebenden Pfad gespeichert.
          -size- ist vom Typ Integer und beschreibt wie viele Pixel groß der Turm dargestellt werden soll. Die Textur wird immer Quadratisch geladen.
          -field_lenght- ist vom Typ Integer und beschreibt, wie viele Pixel ein Feld lang und ist groesser als 0. 
          -field_count- ist vom Typ Integer und beschreibt, wie viele Felder lang das Schachbrett ist und ist groesser als 0.
          -fieldLabelStartLetter- ist vom Typ String und beschreibt mit welchem Buchstabe, dass Brett beginnt beschriftet zu werden. Ein Beispiel wäre "a". -fieldLabelStartLetter- besitzt nur ein Zeichen, welches im lateinischen Alphabet ist und der Anzahl des -field_lenght- nächste Buchstabe noch in dem Alphabet existiert.
          -teamID- ist vom Typ Integer, auch wenn es geht ist für spätere Fälle empfohlen, dass -teamID nicht -1 entspricht.
          -mustKill- ist vom Typ Boolean und ohne Angabe entspricht er False. -mustKill- beschreibt, ob die Figur einen Zug nur machen kann, wenn er eine Figur mit dem Zug schlagen würde. 
                     Dabei steht -False- für muss nicht unbedingt schlagen und -True- für muss unbedingt Schlagen.
    Eff.: -
    Erg.: Eine Turminstanz ist geliefert, welche -FigurBuilder- geerbt hat.
    '''
    def __init__(self, image:str, size:int, field_length:int, field_count:int, fieldLabelStartLetter:str, teamID:int, mustKill:bool=False):
        super().__init__(image, size, field_length, field_count, fieldLabelStartLetter, teamID, False)
        self.__mustKill = mustKill



    def getMaybePossibleTurns(self, originFieldLabel:str)->list[dict]:
        possibleZuege = []
        
        for i in range(1, 8):
                for directionPoint in [(i, 0), (-i, 0), (0, i), (0, -i)]:
                    possibleZuege = self.getNewZugListWithAddingRelative(originFieldLabel, possibleZuege, directionPoint, self.__mustKill)
        return possibleZuege

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Turm Test')
    clock = pygame.time.Clock()


    TestTurmGroup = pygame.sprite.GroupSingle()
    TestTurm = Turm("assets/graphics/s_turm.png", 80, 400, 1)
    TestTurmGroup.add(TestTurm)
    print(TestTurm.getMaybePossibleTurns("a1"))
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
