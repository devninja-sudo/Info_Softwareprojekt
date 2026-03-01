import pygame
from sys import exit
from typing import Callable

class FigurBuilder(pygame.sprite.Sprite):
    '''
    Vor.: -image- ist vom Typstring, welcher den Pfad beschreibt, welche Textur der Turm besitzt. Die Textur ist im PNG Format an dem angegebenden Pfad gespeichert.
          -size- ist vom Typ Integer und beschreibt wie viele Pixel groß der Turm dargestellt werden soll. Die Textur wird immer Quadratisch geladen.
          -field_length- ist vom Typ Integer und beschreibt, wie viele Pixel ein Feld lang und ist groesser als 0. 
          -field_count- ist vom Typ Integer und beschreibt, wie viele Felder lang das Schachbrett ist und ist groesser als 0. Diese Angabe wird benutzt um die Zugmoeglichkeiten zu berechnen. 
          -fieldLabelStartLetter- ist vom Typ String und beschreibt mit welchem Buchstabe, dass Brett beginnt beschriftet zu werden. Ein Beispiel wäre "a". -fieldLabelStartLetter- besitzt nur ein Zeichen, welches im lateinischen Alphabet ist und der Anzahl des -field_lenght- nächste Buchstabe noch in dem Alphabet existiert. Die Nummerierung des Schachbrettes beginnt immer bei 1.
          -teamID- ist vom Typ Integer, auch wenn es geht ist für spätere Fälle empfohlen, dass -teamID nicht -1 entspricht.
          -canJump- ist vom Typ Boolean und beschreibt, ob die Figur ueber andere Figuren springen kann. Ist diese Variable True wird in den Datensaetzen der Figur beschrieben, dass sie es kann. Ist diese False wird in den Datensaetzen der Figur beschrieben, dass sie es nicht kann.
          -KillMates- ist vom Typ Boolean und beschreibt, ob die Figur andere Figuren aus dem gleichen Team schlagen kann. Ist diese Variable True wird in den Datensaetzen der Figur beschrieben, dass sie es kann. Ist diese False wird in den Datensaetzen der Figur beschrieben, dass sie es nicht kann.
          -KillMates- ist ohne Angabe mit False definiert. 
          -hasKingRole- ist vom Typ Boolean und beschreibt, ob die Figur die Koenigsrole traegt. True steht dafuer, dass die Figur die Koenigsrolle hat und False steht dafuer, dass sie keine Koenigsrolle hat.
    Eff.: - 
    Erg.: Ein -FigurBuilder- ist geliefert, welcher pygame.sprite.Sprite geerbt hat.
    '''
    def __init__(self, image:str, size:int, field_length:int, field_count:int, fieldLabelStartLetter:str, teamID:int, canJump:bool, KillMates:bool=False, hasKingRole:bool=False):
        super().__init__()

        self.__imagePath:str = image
        self.__field_length:int = field_length
        self.__centerPos:tuple[int, int] = (self.__field_length/2, self.__field_length/2)
        self.__team:int = teamID
        self.__KillMates:bool = KillMates
        self.__field_count:int = field_count
        self.__fieldLabelStartLetter:str = fieldLabelStartLetter

        self.image:pygame.surface.Surface = pygame.image.load(self.__imagePath).convert_alpha()
        self.image:pygame.surface.Surface = pygame.transform.scale(self.image, (size, size))

        self.rect:pygame.rect.Rect = self.image.get_rect(center = self.__centerPos)

        self.__canJump:bool = canJump

        self.__hasKingRole:bool = hasKingRole

        self.__movedAmount:int = 0

    def setKingRole(self, kingRole:bool)->None:
        '''
        Vor.: -kingRole- ist vom Typ Boolean und beschreibt, ob die Figur die Koenigsrole traegt. True steht dafuer, dass die Figur die Koenigsrolle hat und False steht dafuer, dass sie keine Koenigsrolle hat.
        Eff.: Die Koenigsrole ist zu den uebermittelten Wert angepasst.
        Erg.: - 
        '''
        self.__hasKingRole = kingRole

    def getKingRole(self)->bool:
        '''
        Vor.: -
        Eff.: -
        Erg.: Die aktuelle Koenigsrolle ist geliefert. True steht dafuer, dass die Figur die Koenigsrolle hat und False steht dafuer, dass sie keine Koenigsrolle hat.
        '''
        return self.__hasKingRole
    
    def getTeam(self)->int:
        '''
        Vor.: -
        Eff.: -
        Erg.: Die aktuelle TeamID ist geliefert.
        '''
        return self.__team
    
    def moved(self):
        '''
        Vor.: -
        Eff.: Die Anzahl, wie oft die Figur bewegt wurde ist um eins erhoeht.
        Erg.: -
        '''
        self.__movedAmount +=1
    
    def undoMovedCounterByOne(self):
        '''
        Vor.: -
        Eff.: Die Anzahl, wie oft die Figur bewegt wurde ist um eins vermindert.
        Erg.: -
        '''
        self.__movedAmount -=1

    def getHasMoved(self)->bool:
        '''
        Vor.: -
        Eff.: -
        Erg.: Es ist ein Boolean geliefert, welcher beschreibt, ob die Anzahl der uebermittelten Figur bewegungen 0 entspricht.
        '''
        return self.__movedAmount != 0 
    
    def getMovedAmount(self)->int:
        '''
        Vor.: -
        Eff.: -
        Erg.: Die Anzahl der uebermittelten Figur bewegungen ist als Integer ueberliefert.
        '''
        return self.__movedAmount
    
    def getCanJump(self)->bool:
        '''
        Vor.: -
        Eff.: -
        Erg.: Es ist geliefert als Boolean, ob die Figur springen kann.
        '''
        return self.__canJump
    
    def getCanKillMates(self)->bool:
        '''
        Vor.: -
        Eff.: -
        Erg.: Es ist geliefert als Boolean, ob die Figur Figuren aus dem gleichen Team schlagen kann.
        '''
        return self.__KillMates
    
    def setFieldCount(self, field_count:int)->None:
        '''
        Vor.: -field_count- ist vom Typ Integer und ist groesser als 0. 
        Eff.: Die Feldanzahl des Brettes mit welchem die Figur ihre zugmöglichkeiten berechnet ist auf -field_count- angepasst.
        Erg.: -
        '''
        self.__field_count = field_count

    def setFieldLabelStartLetter(self, Letter:str)->None:
        '''
        Vor.: -Letter- ist vom Typ String und beschreibt mit welchem Buchstabe, dass Brett beginnt beschriftet zu werden. Ein Beispiel wäre "a". -fieldLabelStartLetter- besitzt nur ein Zeichen, welches im lateinischen Alphabet ist und der Anzahl der angegebenden Feldlaenge nächste Buchstabe noch in dem Alphabet existiert.
        Eff.: Das Zeichen mit dem das Brett seine Beschriftung beginnt ist auf -Letter- angepasst.
        Erg.: -
        '''
        self.__fieldLabelStartLetter = Letter

    def __getIsFieldLabelValid(self, testFieldlabel:str):
        '''
        Vor.: -testFieldlabel- ist ein String mit einer Laenge von mindestens 2. Sie ist eventuell eine gueltige Schachfeldbezeichnung.
        Eff.: -
        Erg.: Es ist als Boolean geliefert, ob -testFieldlabel- eine gueltige Schachfeldbezeichnung fuer das bereits beschriebende Schachbrettes ist.
        '''
        lowestLetterID:int = ord(self.__fieldLabelStartLetter)
        maxLetterID:int = lowestLetterID+self.__field_count
        lowestNumber:int = 1
        testFieldLabelLetterID:int = ord(testFieldlabel[0])
        testFieldLabelNumberID:int = int(testFieldlabel[1:])

        return lowestLetterID <= testFieldLabelLetterID <= maxLetterID and lowestNumber <= testFieldLabelNumberID <= self.__field_count


    def convertRelativePointToFieldLabel(self, originFieldLabel:str, RelativePoint:tuple[int, int])->str|None:
        
        
        
        targetFieldLabel:str = ""
        originLetterID:int = ord(originFieldLabel[0])
        originNumberID:int = int(originFieldLabel[1:])

        targetFieldLetterID:int = originLetterID + RelativePoint[0]
        targetFieldNumberID:int = originNumberID + RelativePoint[1]

        targetFieldLabel = chr(targetFieldLetterID) + str(targetFieldNumberID)

        if not(self.__getIsFieldLabelValid(targetFieldLabel)):
            return None
        return targetFieldLabel
    
    def getNewZugListWithAddingRelative(self, originFieldLabel:str, oldZugList:list, RelativePoint:tuple[int, int], onlyOnKill:bool, canKill:bool=True, hasAnxiety:bool=False, specialMoveLabel:str|None = None, needFigureOnField:str|None = None, needFigureType:type|None = None,  allowNeededFigureHasTurned:bool|None = None, endPointNeededFigure:str|None = None, onDoneTurnCall:Callable|None=None, killMaybeFigureType:type|None=None, killMaybeFigureField:str|None=None, killMaybeFigureMustHadDoubleWalkLastTurn:bool=False)->list[dict]:
        newTurn = {}
        newTurn["point"] = RelativePoint
        fieldLabel:str|None = self.convertRelativePointToFieldLabel(originFieldLabel, RelativePoint)
        if fieldLabel == None:                          # Wenn der Zug außerhalb des Brettes gehen würde -> wird fieldLabel == None zu True
            return oldZugList
        newTurn["fieldLabel"] = fieldLabel
        newTurn["onlyOnKill"] = onlyOnKill
        newTurn["canKill"] = canKill
        newTurn["killMaybeFigureType"] = killMaybeFigureType
        newTurn["killMaybeFigureField"] = killMaybeFigureField
        newTurn["killMaybeFigureMustHadDoubleWalkLastTurn"] = killMaybeFigureMustHadDoubleWalkLastTurn

        if self.__hasKingRole:
            newTurn["hasAnxiety"] = True
        else:
            newTurn["hasAnxiety"] = hasAnxiety

        newTurn["specialTurnType"] = specialMoveLabel
        newTurn["needFigureOnField"] = needFigureOnField
        
        newTurn["neededFigureType"] = needFigureType
        newTurn["allowNeededFigureHasTurned"] = allowNeededFigureHasTurned
        newTurn["endPointNeededFigure"] = endPointNeededFigure
        
        newTurn["onDoneTurnCall"] = onDoneTurnCall

        oldZugList.append(newTurn)
        return oldZugList

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption('Figur Test')
    clock = pygame.time.Clock()


    TestSpringerGroup = pygame.sprite.GroupSingle()
    TestSpringerGroup.add(FigurBuilder("assets/graphics/s_springer.png", 80, 200, 1))
    
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