import pygame
from sys import exit
from typing import Callable
from resource_path import resource_path

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

        self.image:pygame.surface.Surface = pygame.image.load(resource_path(self.__imagePath)).convert_alpha()
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
        '''
        Vor.: -originFieldLabel- ist eine gueltige Schachfeldbezeichnung, mit einer Laenge von 2. Das erste Zeichen ist ein Buchstabe im Berreich des im Anfangsbeschriftungsbuchstaben und dem Anfangsbeschriftungsbuchstaben um der Feldanzahl weiter versetzten Buchstaben.
              -RelativePoint- ist ein Tuple und beschreibt ein Feld relativ zu dem originFieldLabel,
                            mit 2 Integern. Der erste Integer ist die Anzahl der Felder, 
                            welche der Zug in Richtung der aufsteigenden Buchstaben geht und 
                            Der zweite ist die Anzahl der Felder, welche der Zug in Richtung der aufsteigenden Zahlen geht. Negative Integer sind in beiden faelllen zulaessig, indem Fall gehen sie in die andere Richtung.
        Eff.: -
        Erg.: Ist in -RelativePoint- ein Feld beschrieben, welches außerhalb des bereits angegebenden Schachbrettes führt ist None geliefert.
              Ist in -RelativePoint- ein gueltiges Feld beschrieben, so ist die Feldbezeichnung des relativ beschriebendes Feldes geliefert als String.  
        '''        
        targetFieldLabel:str = ""
        originLetterID:int = ord(originFieldLabel[0])
        originNumberID:int = int(originFieldLabel[1:])

        targetFieldLetterID:int = originLetterID + RelativePoint[0]
        targetFieldNumberID:int = originNumberID + RelativePoint[1]

        targetFieldLabel = chr(targetFieldLetterID) + str(targetFieldNumberID)

        if not(self.__getIsFieldLabelValid(targetFieldLabel)):
            return None
        return targetFieldLabel
    
    def getNewTurnsListWithAddingRelative(self, originFieldLabel:str, oldZugList:list, RelativePoint:tuple[int, int], onlyOnKill:bool, canKill:bool=True, hasAnxiety:bool=False, specialMoveLabel:str|None = None, needFigureOnField:str|None = None, needFigureType:type|None = None,  allowNeededFigureHasTurned:bool|None = None, endPointNeededFigure:str|None = None, onDoneTurnCall:Callable|None=None, killMaybeFigureType:type|None=None, killMaybeFigureField:str|None=None, killMaybeFigureMustHadDoubleWalkLastTurn:bool=False)->list[dict]:
        '''
        Vor.: -originFieldLabel- ist eine gueltige Schachfeldbezeichnung, mit einer Laenge von 2. Das erste Zeichen ist ein Buchstabe im Berreich des im Anfangsbeschriftungsbuchstaben und dem Anfangsbeschriftungsbuchstaben um der Feldanzahl weiter versetzten Buchstaben.
              -oldZugList- ist eine leere Liste oder eine Liste mit Elementen, welche Eintraege enthaelt, welche durch die korrekte Nutzung der MethodegetNewZugListWithAddingRelative an eine Liste hätte angehangen sein können oder angehangen wurde. 
              -RelativePoint- ist ein Tuple und beschreibt ein Feld relativ zu dem originFieldLabel, 
                            mit 2 Integern. Der erste Integer ist die Anzahl der Felder, 
                            welche der Zug in Richtung der aufsteigenden Buchstaben geht und 
                            der zweite ist die Anzahl der Felder, welche der Zug in Richtung der aufsteigenden Zahlen geht. 
                            Negative Integer sind in beiden faelllen zulaessig, indem Fall gehen sie in die andere Richtung.
              -onlyOnKill- ist ein Boolean und beschreibt, ob die Figur nur zu dem mit -RelativePoint- beschriebenden Feld gehen kann, 
                            wenn sie auf diesen Feld eine Figur schlagen wuerden.
              -canKill- ist ein Boolean, welches ohne Angabe auf True gesetzt wird. Dieses Argument beschreibt, 
                        ob die Figur beim gehen zu dem mit -RelativePoint- beschriebenden Feld gehen kann, 
                        wenn dabei eine Figur geschlagen werden wuerde.
              -hasAnxiety- ist ein Boolean, welches ohne Angabe auf False gesetzt wurde, ausser wenn die Figur die Koenigrolle traegt ist es auf True gesetzt. 
                        Dieses Argument beschreibt, ob die Figur sich nicht zu dem mit -RelativePoint- beschriebenden Feld gehen kann,
                        wenn sie auf dem Feld im naechsten Zug geschlagen werden koennte. 
                        False steht dafuer, dass sie zu dem Feld trotzdem gehen wuerde und
                        True steht dafuer, dass sie es nicht tuen wurde.
              -specialMoveLabel- muss nicht angegeben sein, 
                                wenn -needFigureOnField- und -needFigureType- und -allowNeededFigureHasTurned- auch None entspricht. 
                                Es beschreibt eine spezielle Zug Bezeichnung als String, welche eventuell für späteres umsetzen der Zuege wichtig sein kann.
              -needFigureOnField- muss nicht angegeben sein. 
                                Es entspricht einer Feldbezeichnung. 
                                Nur wenn auf diesem Feld eine Figur steht soll der angegebende Zug umgesetzt werden und ein Feld angegeben wurde. 
              -needFigureType- muss nicht angegeben sein. 
                                Bei Angabe beschreibt es als Typ welcher Typ von Figur auf bei -needFigureOnField- angesprochendem Feld zu stehen hat nur wenn dieser Typ von Figur auf diesem Feld steht soll der Zug gesetzt werden.
              -allowNeededFigureHasTurned- muss nicht angeben sein. 
                                Es beschreibt bei Angabe, inform eines Boolean, ob die benoetigte Figur auf dem Feld -needFigureOnField- sich bereits bewegt haben darf.
              -endPointNeededFigure- muss nicht angeben sein. 
                                Es beschreibt bei Angabe, inform eines Strings, auf welchem Feld die Figur auf dem mit -needFigureOnField- gemeinten Feld nach dem Zug stehen soll.
                                Ohne Angabe bleibt die Figur auf dem mit -needFigureOnField- gemeinten Feld auf dem Feld stehen.
              -onDoneTurnCall- muss nicht angegeben sein.
                                Bei Angabe entspricht -onDoneTurnCall- eine existierende Methode/Funktion.
                                Bei Angabe beschreibt -onDoneTurnCall-, welche Methode/Funktion nach durchführen des Zuges aufgerufen werden soll.
              -killMaybeFigureField- muss nicht angegeben sein, wenn -killMaybeFigureType-, -killMaybeFigureField- und -killMaybeFigureMustHadDoubleWalkLastTurn- auch nicht angegeben ist oder None entspricht.
                                Bei Angabe beschreibt es ein Feld, inform einer Feldbezeichnung als String, auf welchem eine Figur auf dem beschriebendem Feld zusaetzlich geschlagen werden soll.
              -killMaybeFigureType- muss nicht immer angegeben sein, nur wenn -killMaybeFigureMustHadDoubleWalkLastTurn- mit True angegeben wurde muss es mit einer Figurenklasse definiert sein, welche ueber eine Methode hasDidDoubleWalkInTurn(self, TurnNumber:int)->bool: verfuegt, wie bei der Klasse vom 'Bauer'.
                                Bei Angabe entspricht es einem Figuren Typ.
                                Bei Angabe legt es fest, welchen Figurentyp auf dem -killMaybeFigureField- zusaetzlich definierten Feld zum schlagen einer Figur geschlagen werden koennen soll, andere Figurentypen sollen nicht mehr geschlagen werden sollen durch die zusaetzliche Methode.
              -killMaybeFigureMustHadDoubleWalkLastTurn- muss nicht angegeben sein.
                                                        Bei Angabe legt es fest, dass der Zug nur durchgeführt werden soll, wenn die Figur auf dem mit -killMaybeFigureField- gemeinten Feld ein Doppelschritt gemacht haben soll in dem letztem Zug.     
        Eff.: -
        Erg.: 
            Wenn -RelativePoint- ein Feld beschreibt, welches nicht auf dem definierten Schachbrett existiert ist nur die -oldZugList- geliefert, 
            sonst ist eine Liste, welche aus -oldZugList- besteht und eine Tabelle angehangen wurde, welche beschreibt welche genau beschreibt unter welchen Bedingungen ein bestimmter Zug durchgefuehrt werden kann geliefert. 
            Die ggf. der Liste -oldZugList- Angehangende Tabelle besteht in diesem Fall aus ("" sind die Keys und das hinter dem = die Werte):
                "point" = -RelativePoint-
                "fieldLabel" eine gueltige Feldbezeichnung zu dem sich die Figur bewegen soll.
                "onlyOnKill" = -onlyOnKill-
                "canKill" = -canKill-
                "killMaybeFigureType" = -killMaybeFigureType-
                "killMaybeFigureField" = -killMaybeFigureField-
                "killMaybeFigureMustHadDoubleWalkLastTurn" = -killMaybeFigureMustHadDoubleWalkLastTurn-
                "hasAnxiety" = -hasAnxiety- oder immer True, wenn es die Figur die Koenigsrolletraegt
                "specialTurnType" = -specialMoveLabel-
                "needFigureOnField" = -needFigureOnField-
                "neededFigureType" = -needFigureType-
                "allowNeededFigureHasTurned" = allowNeededFigureHasTurned
                "endPointNeededFigure" = endPointNeededFigure
                "onDoneTurnCall" = onDoneTurnCall
        '''        
        newTurn = {}
        newTurn["point"] = RelativePoint
        fieldLabel:str|None = self.convertRelativePointToFieldLabel(originFieldLabel, RelativePoint)
        if fieldLabel == None:
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