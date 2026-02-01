import pygame
from sys import exit
from Feld import Feld
from Springer import Springer
from Turm import Turm
from Laeufer import Laeufer
from FigurBuilder import FigurBuilder
from Dame import Dame
from Bauer import Bauer

class Brett(pygame.sprite.Sprite):
    def __init__(self, edge_length:int, topLeftCorner:tuple[int, int], field_color1:str="yellow", field_color2:str="red", rotation:int=0):
        super().__init__()

        self.__onTurnTeam:int = 0 # Später natürlich 0
        self.__cursor = None
        self.__eventMode:str = None 
        self.__running:bool = False

        self.__rotation:int = rotation
        self.__edge_length:int = edge_length
        self.__fields_count:int = 8
        self.__field_length:int = edge_length//self.__fields_count
        

        self.__field_color_1:str = field_color1
        self.__field_color_2:str = field_color2

        self.__field_label_start_letter:str = "a"

        #die Variablen müssen so heißen und public sein wegen Pygame
        self.image:pygame.Surface = pygame.surface.Surface((edge_length, edge_length))
        self.rect:pygame.Rect = self.image.get_rect(topleft = topLeftCorner)

        self.__fields:dict = self.__createFields()
        self.__fieldsGroup:pygame.sprite.Group = self.__createFieldsGroup()
        self.__setupBrett()
        self.update()



    def start(self)->None:
        if self.__running:
            raise "Bereits gestartet!"
        self.__running = True
        self.__eventMode = "chooseFigure"

    def __setupBrett(self)->None:
        #Wird später sauberer geschrieben !!!
        scale:float = 0.9
        self.__fields["a8"].setFigure(Turm("assets/graphics/s_turm.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1))
        self.__fields["h8"].setFigure(Turm("assets/graphics/s_turm.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1))

        self.__fields["b8"].setFigure(Springer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1))
        self.__fields["g8"].setFigure(Springer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1))
        
        self.__fields["c8"].setFigure(Laeufer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1))
        self.__fields["f8"].setFigure(Laeufer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1))

        self.__fields["d8"].setFigure(Dame("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1))

        self.__buildPawnRow(7, scale, "assets/graphics/s_bauer.png", 1)
        self.__buildPawnRow(2, scale, "assets/graphics/s_bauer.png", 0)

        self.__fields["a1"].setFigure(Turm("assets/graphics/s_turm.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0))
        self.__fields["h1"].setFigure(Turm("assets/graphics/s_turm.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0))

        self.__fields["b1"].setFigure(Springer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0))
        self.__fields["g1"].setFigure(Springer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0))
        
        self.__fields["c1"].setFigure(Laeufer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0))
        self.__fields["f1"].setFigure(Laeufer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0))

        self.__fields["d1"].setFigure(Dame("assets/graphics/s_springer.png",self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0))

    def __buildPawnRow(self, RowNumber:int, scale:float, texturePath:str, teamID:int) -> None:
        for i in range(self.__fields_count):
            fieldLabelLetter:str = chr(ord(self.__field_label_start_letter)+i)
            fieldLabel:str = fieldLabelLetter + str(RowNumber)
            targetField:Feld = self.__fields[fieldLabel]
            targetField.setFigure(Bauer(texturePath, self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, teamID))

    def setRotation(self, rotation:int)->None:
        if rotation % 90 != 0:
            raise "Rotation not available!"
        self.__rotation:int = rotation
        self.__correctFieldPositions()

    def getRotation(self)->int:
        return self.__rotation
    
    def __correctFieldPositions(self)->None:
        for key in self.__fields.keys():
            currentField:Feld = self.__fields[key]
            currentField.setFieldPosition(self.__getFieldPositionByName(key))
        self.__generateImage()

    def __createFields(self)->dict:
        fields:dict = {}
        for spread in range(ord(self.__field_label_start_letter), ord(self.__field_label_start_letter)+self.__fields_count):
            for lengths in range(1, 1+self.__fields_count):
                if (spread+lengths)%2 == 1:
                    color = self.__field_color_1
                else:
                    color = self.__field_color_2 
                field_label:str = chr(spread) + str(lengths)
                field_current:Feld = Feld((self.__field_length, self.__field_length), self.__getFieldPositionByName(field_label), color, field_label)
                fields[field_label] = field_current
        return fields
    

    def __getFieldPositionByName(self, field_name:str)->tuple[int, int]:
        lengthID = int(ord(field_name[0])-ord(self.__field_label_start_letter))
        spreadID = int(field_name[1])

        x = self.__field_length*lengthID
        y = self.__field_length*(self.__fields_count-spreadID)

        self.__rotation = self.__rotation%360
        if self.__rotation == 0:
            return (x, y)
        if self.__rotation % 90 != 0:
            raise "Rotation not available!"
        for i in range(self.__rotation//90):
            x, y = self.__rotatePoint90degree((x, y))
        return x, y
    
    def __rotatePoint90degree(self, point:tuple[int, int])->tuple[int, int]:
        return (self.__edge_length-point[1]-self.__field_length, point[0])
    
    def __getFieldsGroup(self)->pygame.sprite.Group:
        return self.__fieldsGroup
    
    def __createFieldsGroup(self)->pygame.sprite.Group:
        fieldsGroup = pygame.sprite.Group()
        
        for key in self.__fields.keys():
            field = self.__fields[key]
            fieldsGroup.add(field)

        return fieldsGroup

    def __generateImage(self) -> None:
        self.image.fill("black")
        fieldsGroup = self.__getFieldsGroup()
        fieldsGroup.draw(self.image)
        
    def update(self) -> None:
        self.__generateImage()

    def __CheckIfIsNotAFeldInstance(self, testObject:object) ->bool:
        return type(testObject) != Feld
    
    def handleClickEvent(self, pos:tuple[int, int])->None:
        if not(self.__running):
            return
        
        clickedField = self.getFieldByCords(pos)
        if self.__CheckIfIsNotAFeldInstance(clickedField):
            return
        clickedFieldLabel = clickedField.getLabel()

        if self.__eventMode == "chooseFigure":
            self.__chooseFigureEvent(clickedField)
        elif self.__eventMode == "setFigure":
            self.__setFigureEvent(clickedField)

    def __resetCursorAndSetEventMode(self, eventMode:str):
        self.__cursor = None
        self.__eventMode = eventMode
        
    def __setFigureEvent(self, clickedField:Feld)->None:
        self.__clearAllFieldHighlights()
        if self.__chooseFigureEvent(clickedField):
            return
        if self.__CheckIfIsNotAFeldInstance(self.__cursor):
            raise "Cursor muss ein Feld sein"
        
        clickedFigure = clickedField.getFigure()
        clickedFieldLabel = clickedField.getLabel()   

        if not(clickedField in self.getPossibleTurnFields(self.__cursor)):
            self.__resetCursorAndSetEventMode("chooseFigure")
            self.__clearAllFieldHighlights()
            return
        
        beforeClickedFieldFigure = clickedField.getFigure()
        beforeCursorFigur = self.__cursor.getFigure()

        clickedField.setFigure(self.__cursor.getFigure())
        self.__cursor.setFigure(None)

        if self.__getCheckedTeam() == self.__onTurnTeam:
            print("Zug nicht möglich (achte auf Schach)")
            clickedField.setFigure(beforeClickedFieldFigure)
            self.__cursor.setFigure(beforeCursorFigur)

            self.__resetCursorAndSetEventMode("chooseFigure")
            self.__clearAllFieldHighlights()
            return
        
        if clickedFigure != None:
            if clickedFigure.getTeam() == self.__onTurnTeam:
                self.__eventMode = "chooseFigure"
                self.__chooseFigureEvent(clickedField)
                return
            else:
                print("Es wird eine Figur geschlagen!")

        self.__switchToOtherPlayer()
        self.__eventMode = "chooseFigure"
        self.__clearAllFieldHighlights()
        
    def __getCheckedTeam(self)->int|None:
        return None # muss noch ordentlich werden

    def __switchToOtherPlayer(self)->None:
        self.__onTurnTeam = (self.__onTurnTeam+1)%2

    def __chooseFigureEvent(self, clickedField:Feld)->bool:
        clickedFigure:None|Springer|Turm|Bauer|Laeufer|Dame = clickedField.getFigure()
        clickedFieldLabel:str = clickedField.getLabel()
        if clickedFigure == None:
            self.__clearAllFieldHighlights() 
            return False
        # clickedFigure ist ab jetzt Aufjedenfall eine Figur

        if clickedFigure.getTeam() != self.__onTurnTeam:
            return False
        # Es ist sichergestellt, dass mann nicht eine Figur vom Gegner verschieben wollte
        self.__markAllPosibleFields(clickedFieldLabel)
        clickedField.addFieldHighlight("GreenOutlineBox")
        self.__eventMode:str = "setFigure"
        self.__cursor = clickedField
        return True

    def __clearAllFieldHighlights(self)->None:
        for key in self.__fields.keys():
            field = self.__fields[key]
            if type(field) != Feld:
                continue
            field.clearFieldHighlights()

    def getPossibleTurnFields(self, Field:Feld)->list[Feld]:        # Geht sicher, dass nicht doch irgendwie Ein Feld außerhalb des Brettes ist arbeitet noch Relative
        PossibleTurnFields = []
        relativePossibleTurnFields = self.__getPossibleRelativeFieldsFromFigurOnField(Field)
        for relativeField in relativePossibleTurnFields:
            field = self.getRelativeField(Field.getLabel(), relativeField)
            if type(field) != Feld:
                continue
            PossibleTurnFields.append(field)
        return PossibleTurnFields



    def __markAllPosibleFields(self, FigureFieldLabel:str)->None:
        for field in self.getPossibleTurnFields(self.__fields[FigureFieldLabel]):
            if type(field) == Feld:
                field.addFieldHighlight("SmallGreenMiddleCircle")
            
    def __getOnlyPointsList(self,TurnsDatas:list[dict])->list[tuple]:
        PointsList:list = []                           #
        for TurnData in TurnsDatas:               #
            PointsList.append(TurnData["point"])  # Zur Weiterverarbeitung sind nur noch die Relativen Punkte notwending 
        return PointsList
    
    def __getOnlyTurnDataWithValidFields(self, turnsData:list[dict])->list[dict]:
        turnDataValidFields = []
        for turnData in turnsData:
            turnTargetFieldLabel = turnData["fieldLabel"]
            if not(turnTargetFieldLabel in self.__fields.keys()):
                continue

            targetField = self.__fields[turnTargetFieldLabel]
            if type(targetField) != Feld:
                continue
            turnDataValidFields.append(turnData)
        return turnDataValidFields

    def __getTurnsNotKillingMatesFromTurnData(self, turnsData:list[dict], TeamID:int)->list[dict]:
        turnDataNotKillingMates = []
        for turnData in turnsData:
            turnTargetFieldLabel = turnData["fieldLabel"]
            if not(turnTargetFieldLabel in self.__fields.keys()):       # Auf Nummer sicher gehen eig. nicht Notwendig! Kein Feld -> Kein Zug
                continue                                                # Auf Nummer sicher gehen eig. nicht Notwendig! Kein Feld -> Kein Zug
            targetField = self.__fields[turnTargetFieldLabel]           # Auf Nummer sicher gehen eig. nicht Notwendig! Kein Feld -> Kein Zug
            if type(targetField) != Feld:                               # Auf Nummer sicher gehen eig. nicht Notwendig! Kein Feld -> Kein Zug
                continue                                                # Auf Nummer sicher gehen eig. nicht Notwendig! Kein Feld -> Kein Zug
            fieldFigure = targetField.getFigure()
            if fieldFigure == None:                                     # Wenn keine Figur auf dem ZielFeld steht kann auch keine Rausgworfen werden, also ist das ok
                turnDataNotKillingMates.append(turnData)                # Wenn keine Figur auf dem ZielFeld steht kann auch keine Rausgworfen werden, also ist das ok
                continue                                                # Wenn keine Figur auf dem ZielFeld steht kann auch keine Rausgworfen werden, also ist das ok
            if fieldFigure.getTeam() == TeamID:
                continue
            turnDataNotKillingMates.append(turnData)
        return turnDataNotKillingMates

    def __getPossibleRelativeFieldsFromFigurOnField(self, startingPointField:Feld)->list[tuple]:
        figure:None|Springer|Turm|Bauer|Laeufer|Dame = startingPointField.getFigure()
        if figure == None:
            return []       # Ein Feld ohne Figur kann seine Figur nirgendwo hinsetzen
        
        startFieldLabel:str = startingPointField.getLabel()

        canJump:bool = figure.getCanJump()
        canKillMates:bool = figure.getCanKillMates()
        relativeMaybePossibleTurnsData:list[dict] = figure.getMaybePossibleTurns(startFieldLabel)                           # Diese sollten eig. nicht Links zu nicht existenten Feldern haben
        relativeMaybePossibleTurnsData:list[dict] = self.__getOnlyTurnDataWithValidFields(relativeMaybePossibleTurnsData)   # Das ist jetzt trotzdem nochmal Sichergestellt, wer weiß oder so...

        if not(canJump):
            relativeMaybePossibleTurnsData:list[dict] = self.__getTurnDataWithoutWalkThroughFigures(relativeMaybePossibleTurnsData, startingPointField)
        if not(canKillMates):
            relativeMaybePossibleTurnsData:list[dict] = self.__getTurnsNotKillingMatesFromTurnData(relativeMaybePossibleTurnsData, figure.getTeam())


        possibleRelativeFields = []                                                                                             
        for relativeMaybePossibleTurnData in relativeMaybePossibleTurnsData:                                                                        # Für jeden Punkt prüfen, welche der zusätzlichen Eigenschaften den Zuges erfüllt sein müssen um den Zug auszuführen und wenn diese nicht erfüllt ist ihn aussortieren
            if type(relativeMaybePossibleTurnData) != dict:
                raise "Unexpectet Type error in Brett: Line 309"
            if relativeMaybePossibleTurnData["onlyOnKill"] or not(relativeMaybePossibleTurnData["canKill"]):
                inspectIfKillField = self.__fields[relativeMaybePossibleTurnData["fieldLabel"]]
                if self.__CheckIfIsNotAFeldInstance(inspectIfKillField):
                    continue
                if inspectIfKillField.getFigure() == None and relativeMaybePossibleTurnData["onlyOnKill"]:
                    continue
                if inspectIfKillField.getFigure() != None and not(relativeMaybePossibleTurnData["canKill"]):
                    continue
            possibleRelativeFields.append(relativeMaybePossibleTurnData["point"])  
        return possibleRelativeFields
    
    def __getBackTurnsDataByRelativeTurns(self, relativePossibleTurnsDatas:list[dict], points:list[tuple[int, int]])->list[dict]|list:
        result:list = []
        for point in points:
            backTurnData = self.__getBackTurnDataByRalativeTurn(relativePossibleTurnsDatas, point)
            if backTurnData == None:
                raise "Could not find Turndata Back"
            result.append(backTurnData)
        return result

    def __getBackTurnDataByRalativeTurn(self, relativePossibleTurnsDatas:list[dict], point:tuple[int, int])->dict|None:
        for relativePossibleTurnData in relativePossibleTurnsDatas:
            controlPoint:tuple[int, int] = relativePossibleTurnData["point"]
            if controlPoint == point:
                return relativePossibleTurnData
       
    def __getTurnDataWithoutWalkThroughFigures(self, relativeMaybePossibleTurnsData:list[dict], startField:Feld)->list|list[dict]:
        possibleRelativeFields:list[tuple] = self.__getOnlyPointsList(relativeMaybePossibleTurnsData)   
        xLine:list = []
        yLine:list = []
        DiagonalXandY:list = []
        DiagonalXdiffY:list = []
        
        unsortet:list[tuple] = possibleRelativeFields.copy()
        for RelativeField in possibleRelativeFields:
            # Vertikal -> (nur X ändert sich, Y = 0)
            if RelativeField[1] == 0:
                xLine.append(RelativeField)
                unsortet.remove(RelativeField)
                continue
            # Horizontal -> (nur Y ändert sich, X = 0)
            if RelativeField[0] == 0:
                yLine.append(RelativeField)
                unsortet.remove(RelativeField)
                continue
            # Diagonale -> (X und Y gleich)
            if RelativeField[1] == RelativeField[0]:
                DiagonalXandY.append(RelativeField)
                unsortet.remove(RelativeField)
                continue
            # Diagonale -> (X und Y entgegengesetzt)
            if RelativeField[1] == -RelativeField[0]:
                DiagonalXdiffY.append(RelativeField)
                unsortet.remove(RelativeField)
                continue
        
        if unsortet != []:
            raise "Nicht unterstütztes Bewegungsraster!"
        
        xLines:list[tuple]|list = self.__sortToDestination(xLine, 0)
        yLines:list[tuple]|list = self.__sortToDestination(yLine, 1)
        DiagonalXandY:list[tuple]|list = self.__sortToDestination(DiagonalXandY, 0)
        DiagonalXdiffY:list[tuple]|list = self.__sortToDestination(DiagonalXdiffY, 0)
        # Jetzt sind alle Listen nach Richtungen Sortiert und in der richtigen reinfolge um jetzt von Vorne bis nach hinten zu prüfen, ob was im Weg steht um dahin zu laufen 
        resultFields = []
        for lines in [xLines, yLines, DiagonalXandY, DiagonalXdiffY]:
            for line in lines:
                for resultRelative in self.__cutLineAtWalkingThroughFigures(line, startField):
                    resultFields.append(resultRelative)

        resultFields:list[dict]|list = self.__getBackTurnsDataByRelativeTurns(relativeMaybePossibleTurnsData, resultFields)
        return resultFields
    
    def __cutLineAtWalkingThroughFigures(self, Line:list[tuple], startField:Feld)->list[tuple]|list:
        '''
        Vor.: 'Line' ist nach zunehmenden Abstand sortiert und geht entweder Wagerecht oder Horizontal
        Eff.: -
        Erg.: Eine Liste die nur noch die relativen beinhaltet die von dem startFeld aus, wenn man die Linie von links nach rechts durchläuft nicht durch eine andere Figur läuft, sondern diese schlagen würde.
        '''
        resultLine = []
        for relative in Line: # Für jedes Feld in der Liste in der bereits richtigen Reignfolge durchgehen und zum ergebniss hinzufügen, wenn etwas im Weg stegt, dann stoppen
            inspectField:Feld|None = self.getRelativeField(startField.getLabel(), relative)
            if type(inspectField) != Feld:
                continue
            if inspectField.getFigure() != None:
                resultLine.append(relative)
                break
            resultLine.append(relative)
        return resultLine
    
    def __sortToDestination(self, Line:list, sortIndex:int)->list:
        Line.sort()
        Line = self.__SpitNegatives(Line, sortIndex)
        return self.__reverseFirstPart(Line)
    
    def __reverseFirstPart(self, Line:list[list[tuple], list[tuple]])->list:
        firstPartLine = Line[0]
        if type(firstPartLine) == list:
            firstPartLine.reverse()
        return firstPartLine, Line[1]
    
    def __SpitNegatives(self, Line:list[tuple], SplitNumberIndex:int)->list[list[tuple], list[tuple]]:
        LinePositives = []
        LineNegatives = []

        for Element in Line:
            if Element[SplitNumberIndex] < 0:
                LineNegatives.append(Element)
                continue
            LinePositives.append(Element)
        return LineNegatives, LinePositives

    def getRelativeField(self, fieldLabel:str, relativeField:tuple[int, int])->Feld|None:
        startFieldX:int = ord(fieldLabel[0])
        startFieldY:int = int(fieldLabel[1])
        try:
            targetFieldLabel:str = chr(startFieldX+relativeField[0])+str(startFieldY+relativeField[1])
            targetField:Feld|None = self.__fields[targetFieldLabel]
            if type(targetField) != Feld:
                return None
            return targetField
        except:
            return None



    def getFieldByCords(self, pos:tuple[int, int])->Feld|None:
        x:int = pos[0]-self.rect.topleft[0]
        y:int = pos[1]-self.rect.topleft[1]
        if not(self.rect.collidepoint(pos)):
            return 
        
        for key in self.__fields.keys():
            field = self.__fields[key]
            if type(field) != Feld:
                continue 

            field_rect:pygame.rect.Rect = field.getRect()
            
            if field_rect.collidepoint(x, y):
                return field

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption('Brett Test')
    clock = pygame.time.Clock()


    TestBrettGroup = pygame.sprite.GroupSingle()
    Spielbrett = Brett(800, (1920/2-400, 1080/2-400), "white", "black")
    Spielbrett.start()
    TestBrettGroup.add(Spielbrett)
    print(Spielbrett.getRelativeField("d4", (1, 1)))
    
    
    while True:
        screen.fill("grey")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                continue
            if event.type == pygame.MOUSEBUTTONUP:
                Spielbrett.handleClickEvent(pygame.mouse.get_pos())
        TestBrettGroup.draw(screen)
        TestBrettGroup.update()
        pygame.display.update()
        clock.tick(60)
        #Spielbrett.setRotation(int(input()))