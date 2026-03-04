import pygame
from sys import exit
from FigurBuilder import FigurBuilder

class Springer(FigurBuilder):
    '''
    Vor.: -image- ist vom Typ String, welcher den Pfad der Textur beschreibt, die der Springer besitzt. Die Textur ist dort im PNG Format gespeichert.
          -size- ist vom Typ Integer und beschreibt wie viele Pixel gross der Springer dargestellt werden soll. Die Textur wird immer Quadratisch geladen.
          -field_lenght- ist vom Typ Integer und beschreibt, wie viele Pixel ein Feld lang ist. Es muss groesser als 0 sein. 
          -field_count- ist vom Typ Integer und beschreibt, wie viele Felder lang das Schachbrett ist. Es muss groesser als 0 sein.
          -fieldLabelStartLetter- ist vom Typ String und beschreibt mit welchem Buchstabe die Beschriftung des Feldes beginnt. Ein Beispiel waere "a". -fieldLabelStartLetter- besitzt nur ein Zeichen, welches im lateinischen Alphabet ist. Dabei muss der Buchstabe, der -field_lenght- Stellen weiter ist, noch im lateinischen Alphabet liegen.
          -teamID- ist vom Typ Integer, auch wenn es geht ist fuer spaetere Faelle empfohlen, dass -teamID nicht -1 entspricht.
          -mustKill- ist vom Typ Boolean und ohne Angabe entspricht er False. -mustKill- beschreibt, ob die Figur nur einen Zug machen darf, wenn sie dabei eine andere Figur schlaegt. Dabei steht -False- fuer muss nicht unbedingt schlagen und -True- fuer muss unbedingt Schlagen.
    Eff.: -
    Erg.: Eine Springerinstanz ist geliefert, welche -FigurBuilder- geerbt hat.
    '''
    def __init__(self, image:str, size:int, field_length:int, field_count:int, fieldLabelStartLetter:str, teamID:int, mustKill:bool=False):
        super().__init__(image, size, field_length, field_count, fieldLabelStartLetter, teamID, True)

        self.__SchrittLaenge = 1
        self.__SchrittBreite = 2

        self.__mustKill = mustKill
        



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
        
        for i in [-1, 1]:
            for j in [-1, 1]:
                possibleZuege = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleZuege, (self.__SchrittLaenge*i, self.__SchrittBreite*j), self.__mustKill)
                possibleZuege = self.getNewTurnsListWithAddingRelative(originFieldLabel, possibleZuege, (self.__SchrittBreite*i, self.__SchrittLaenge*j), self.__mustKill)
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
