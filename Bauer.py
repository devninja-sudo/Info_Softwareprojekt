import pygame
from sys import exit
from FigurBuilder import FigurBuilder

class Bauer(FigurBuilder):
    '''
    Vor.: -image- ist vom Typ String, welcher den Pfad der Textur beschreibt, die der Bauer besitzt. Die Textur ist dort im PNG Format gespeichert.
          -size- ist vom Typ Integer und beschreibt wie viele Pixel gross der Bauer dargestellt werden soll. Die Textur wird immer Quadratisch geladen.
          -field_lenght- ist vom Typ Integer und beschreibt, wie viele Pixel ein Feld lang ist. Es muss groesser als 0 sein. 
          -field_count- ist vom Typ Integer und beschreibt, wie viele Felder lang das Schachbrett ist. Es muss groesser als 0 sein.
          -fieldLabelStartLetter- ist vom Typ String und beschreibt mit welchem Buchstabe die Beschriftung des Feldes beginnt. Ein Beispiel waere "a". -fieldLabelStartLetter- besitzt nur ein Zeichen, welches im lateinischen Alphabet ist. Dabei muss der Buchstabe, der -field_lenght- Stellen weiter ist, noch im lateinischen Alphabet liegen.
          -teamID- ist vom Typ Integer, auch wenn es geht ist fuer spaetere Faelle empfohlen, dass -teamID nicht -1 entspricht.
          -mustKill- ist vom Typ Boolean und ohne Angabe entspricht er False. -mustKill- beschreibt, ob die Figur nur einen Zug machen darf, wenn sie dabei eine andere Figur schlaegt. Dabei steht -False- fuer muss nicht unbedingt schlagen und -True- fuer muss unbedingt Schlagen.
    Eff.: -
    Erg.: Eine Bauerinstanz ist geliefert, welche -FigurBuilder- geerbt hat.
    '''
    def __init__(self, image:str, size:int, field_length:int, field_count:int, fieldLabelStartLetter:str, teamID:int, mustKill:bool=False):
        super().__init__(image, size, field_length, field_count, fieldLabelStartLetter, teamID, False)
        self.__mustKill = mustKill
        self.__didDoubleWalkInTurns = []

    def didDoubleWalk(self, TurnNumber:int)->None:
        '''
        Vor.: -TurnNumber- ist vom Typ Integer und beschreibt in welchem Zug der Bauer einen Doppelzug macht.
        Eff.: -TurnNumber- ist der Liste -didDoubleWalkInTurns- angehaengt.
        Erg.: -
        '''
        self.__didDoubleWalkInTurns.append(TurnNumber)

    def hasDidDoubleWalkInTurn(self, testTurnNumber:int)->bool:
        '''
        Vor.: -testTurnNumber- ist vom Typ Integer und beschreibt einen bestimmten Zug des Spiels.
        Eff.: -
        Erg.: -True- ist geliefert, wenn zu diesem Zug ein Doppelzug statt findet.
              -False- ist geliefert, wenn dies nicht der Fall ist.
        '''
        return testTurnNumber in self.__didDoubleWalkInTurns

    def getMaybePossibleTurns(self, originFieldLabel:str)->list[dict]:
        '''
        Vor.: -originFieldLabel- ist eine gueltige Schachfeldbezeichnung, mit einer Laenge von 2. Das erste Zeichen ist ein Buchstabe im Berreich des Buchstaben der Anfangsbeschriftungs und dem Buchstaben der Anfangsbeschriftungs versetzt um die Feldanzahl. Das zweite Zeichen ist eine Zahl im Berreich der Zahl der Anfangsbeschriftungs und der Zahl der Anfangsbeschriftungs versetzt um die Feldanzahl.
        Eff.: -
        Erg.: 
              Eine Liste ggf. aus Tabellen ist geliefert. Sie beschreibt unter welchen Bedingungen ein bestimmter Zug durchgefuehrt werden kann. 
              Die ggf. in Liste vorkommenden Tabellen bestehen in diesem Fall aus ("" sind die Keys und das hinter dem = die Werte):
                "point" = :tuple[int, int] (gueltige Feldbezeichnung, die relativ zu -originFieldLabel- die Anzahl der Felder angibt, die fuer einen Zug in Buchstaben und Zahlen Richtung noetig sind)
                "fieldLabel" = :str eine gueltige Feldbezeichnung (das erste Zeichen ist ein Buchstabe im Berreich des Buchstaben der Anfangsbeschriftungs und dem Buchstaben der Anfangsbeschriftungs versetzt um die Feldanzahl / das zweite Zeichen ist eine Zahl im Berreich der Zahl der Anfangsbeschriftungs und der Zahl der Anfangsbeschriftungs versetzt um die Feldanzahl) zu dem sich die Figur bewegen soll.
                "onlyOnKill" = :bool (-True-, wenn die Figur nur den Zug machen kann, wenn sie dabei eine andere Figur schlagen wuerde)
                "canKill" = :bool (-True-, wenn die Figur beim Zug auf das Zielfeld eine andere Figur schlagen koennte)
                "killMaybeFigureType" =  (Klasse der Figur, die geschlagen werden kann)
                "killMaybeFigureField" = :str (Feldbezeichnung des Feldes, auf dem eine Figur geschlagen werden kann)
                "killMaybeFigureMustHadDoubleWalkLastTurn" = :bool (beschreibt, ob die Figur, die geschlagen werden kann, im letzten Zug einen Doppelzug gemacht hat)
                "hasAnxiety" = :boool oder immer True, wenn die Figur die Koenigsrolle traegt (beschreibt, ob die Figur auf dem Zeilfeld des Zuges geschlagen werden koennte)
                "specialTurnType" = :str (spezielle Zugbezeichnung)
                "needFigureOnField" = :str (Zug ist nur moeglich, wenn auf dem Feld eine Figur steht und ein anderes Feld angegeben ist)
                "neededFigureType" =  (ueberprueft, ob der Zug einer bestimmten hier angegebender Figur als Figurklasse mit der Figur auf dem Feld uebereinstimmt)
                "allowNeededFigureHasTurned" = :bool (beschreibt, ob sie die Figur auf dem Feld -needFigureOnField- schon bewegt hat)
                "endPointNeededFigure" = :str (Feldbezeichnung, auf dem die Firgur nach dem Zug steht)
                "onDoneTurnCall" = :Callable (beschreibt die Methode/Funktion, die nach dem Zug ausgefuerht wird)
        '''
        possibleZuege = []
        if self.getTeam() == 0:
            direction = 1
        else:
            direction = -1
        possibleZuege = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleZuege, (0, 1*direction), self.__mustKill, False)
        if int(originFieldLabel[1]) == 2 and direction == 1:
            possibleZuege = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleZuege, (0, 2*direction), self.__mustKill, False, onDoneTurnCall=self.didDoubleWalk)
        elif int(originFieldLabel[1]) == 7 and direction == -1:
            possibleZuege = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleZuege, (0, 2*direction), self.__mustKill, False, onDoneTurnCall=self.didDoubleWalk)

        possibleZuege = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleZuege, (1, 1*direction), True, True, killMaybeFigureField=self.convertRelativePointToFieldLabel(originFieldLabel, (1, 0)), killMaybeFigureType=Bauer, killMaybeFigureMustHadDoubleWalkLastTurn=True)
        possibleZuege = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleZuege, (-1, 1*direction), True, True, killMaybeFigureField=self.convertRelativePointToFieldLabel(originFieldLabel, (-1, 0)), killMaybeFigureType=Bauer, killMaybeFigureMustHadDoubleWalkLastTurn=True)
        
        return possibleZuege

    

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Laeufer Test')
    clock = pygame.time.Clock()


    TestBauerGroup = pygame.sprite.GroupSingle()
    BauerDame = Bauer("assets/graphics/s_bauer.png", 80, 400, 1, "a", 0, False)
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
