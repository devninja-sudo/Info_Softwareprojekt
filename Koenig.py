import pygame
from sys import exit
from FigurBuilder import FigurBuilder
from Turm import Turm
class Koenig(FigurBuilder):
    '''
    Vor.: -image- ist vom Typ String, welcher den Pfad der Textur beschreibt, die der Koenig besitzt. Die Textur ist dort im PNG Format gespeichert.
          -size- ist vom Typ Integer und beschreibt wie viele Pixel gross der Koenig dargestellt werden soll. Die Textur wird immer Quadratisch geladen.
          -field_lenght- ist vom Typ Integer und beschreibt, wie viele Pixel ein Feld lang ist. Es muss groesser als 0 sein. 
          -field_count- ist vom Typ Integer und beschreibt, wie viele Felder lang das Schachbrett ist. Es muss groesser als 0 sein.
          -fieldLabelStartLetter- ist vom Typ String und beschreibt mit welchem Buchstabe die Beschriftung des Feldes beginnt. Ein Beispiel waere "a". -fieldLabelStartLetter- besitzt nur ein Zeichen, welches im lateinischen Alphabet ist. Dabei muss der Buchstabe, der -field_lenght- Stellen weiter ist, noch im lateinischen Alphabet liegen.
          -teamID- ist vom Typ Integer, auch wenn es geht ist fuer spaetere Faelle empfohlen, dass -teamID nicht -1 entspricht.
          -mustKill- ist vom Typ Boolean und ohne Angabe entspricht er False. -mustKill- beschreibt, ob die Figur nur einen Zug machen darf, wenn sie dabei eine andere Figur schlaegt. Dabei steht -False- fuer muss nicht unbedingt schlagen und -True- fuer muss unbedingt Schlagen.
    Eff.: -
    Erg.: Eine Koeniginstanz ist geliefert, welche -FigurBuilder- geerbt hat.
    '''
    def __init__(self, image:str, size:int, field_length:int, field_count:int, fieldLabelStartLetter:str, teamID:int, mustKill:bool=False):
        super().__init__(image, size, field_length, field_count, fieldLabelStartLetter, teamID, False, None, True)

        self.__mustKill:bool = mustKill
        self.__canKill:bool = True


        self.__hasAnxiety:bool = True
        
        


    def getMaybePossibleTurns(self, originFieldLabel:str)->list[dict]:
        '''
        Vor.: -originFieldLabel- ist eine gueltige Schachfeldbezeichnung, mit einer Laenge von 2. Das erste Zeichen ist ein Buchstabe im Berreich des Buchstaben der Anfangsbeschriftungs und dem Buchstaben der Anfangsbeschriftungs versetzt um die Feldanzahl. Das zweite Zeichen ist eine Zahl im Berreich der Zahl der Anfangsbeschriftungs und der Zahl der Anfangsbeschriftungs versetzt um die Feldanzahl.
        Eff.: -
        Erg.: Ein Dictionary mit folgenden Daten ist geliefert. Den Koordinaten des Punktes, auf der die Figur steht. Den Angaben, ob das Schlagen einer anderen Figur moeglich ist (mit Angabe der anderen Figur, des Feldes und ob ein Doppelzug geschehen ist). Ob die Figur von einer anderen Figur bedroht wird. Ob die Figur besondere Zuege hat und ob der Zug erlaubt ist.
              Eine Liste ggf. aus Tabellen ist geliefert. Sie beschreibt unter welchen Bedingungen ein bestimmter Zug durchgefuehrt werden kann. 
              Die ggf. in Liste vorkommenden Tabellen bestehen in diesem Fall aus ("" sind die Keys und das hinter dem = die Werte):
                "point" = -RelativePoint- (gueltige Feldbezeichnung, die relativ zu -originFieldLabel- die Anzahl der Felder angibt, die fuer einen Zug in Buchstaben und Zahlen Richtung noetig sind)
                "fieldLabel" eine gueltige Feldbezeichnung (das erste Zeichen ist ein Buchstabe im Berreich des Buchstaben der Anfangsbeschriftungs und dem Buchstaben der Anfangsbeschriftungs versetzt um die Feldanzahl / das zweite Zeichen ist eine Zahl im Berreich der Zahl der Anfangsbeschriftungs und der Zahl der Anfangsbeschriftungs versetzt um die Feldanzahl) zu dem sich die Figur bewegen soll.
                "onlyOnKill" = -onlyOnKill- (-True-, wenn die Figur nur den Zug machen kann, wenn sie dabei eine andere Figur schlagen wuerde)
                "canKill" = -canKill- (-True-, wenn die Figur beim Zug auf das Zielfeld eine andere Figur schlagen koennte)
                "killMaybeFigureType" = -killMaybeFigureType- (Typ der Figur, die geschlagen werden kann)
                "killMaybeFigureField" = -killMaybeFigureField- (Feldbezeichnung des Feldes, auf dem eine Figur geschlagen werden kann)
                "killMaybeFigureMustHadDoubleWalkLastTurn" = -killMaybeFigureMustHadDoubleWalkLastTurn- (beschreibt, ob die Figur, die geschlagen werden kann, im letzten Zug einen Doppelzug gemacht hat)
                "hasAnxiety" = -hasAnxiety- oder immer True, wenn die Figur die Koenigsrolle traegt (beschreibt, ob die Figur auf dem Zeilfeld des Zuges geschlagen werden koennte)
                "specialTurnType" = -specialMoveLabel- (spezielle Zugbezeichnung)
                "needFigureOnField" = -needFigureOnField- (Zug ist nur moeglich, wenn auf dem Feld eine Figur steht und ein anderes Feld angegeben ist)
                "neededFigureType" = -needFigureType- (ueberprueft, ob der Zug einer bestimmten Figur mit der Figur auf dem Feld uebereinstimmt)
                "allowNeededFigureHasTurned" = allowNeededFigureHasTurned (beschreibt, ob sie die Figur auf dem Feld -needFigureOnField- schon bewegt hat)
                "endPointNeededFigure" = endPointNeededFigure (Feld, auf dem die Firgur nach dem Zug steht)
                "onDoneTurnCall" = onDoneTurnCall (beschreibt die Methode/Funktion, die nach dem Zug ausgefuerht wird)        
        '''
        possibleTurns = []
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if i == 0 and j == 0:
                    continue
                possibleTurns = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleTurns, (i, j), self.__mustKill, self.__canKill, self.__hasAnxiety)
        if not(self.getHasMoved()):
            possibleTurns = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleTurns, (2, 0), False, False, True, "castling", self.convertRelativePointToFieldLabel(originFieldLabel, (3, 0)), Turm, False, self.convertRelativePointToFieldLabel(originFieldLabel, (1, 0)))
            possibleTurns = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleTurns, (-2, 0), False, False, True, "castling", self.convertRelativePointToFieldLabel(originFieldLabel, (-4, 0)), Turm, False, self.convertRelativePointToFieldLabel(originFieldLabel, (-2, 0)))
        return possibleTurns

    


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
