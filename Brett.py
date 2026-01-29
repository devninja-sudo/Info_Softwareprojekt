import pygame
from sys import exit
from Feld import Feld
from Springer import Springer
from Turm import Turm
from Laeufer import Laeufer
from FigurDisplay import FigurDisplay

class Brett(pygame.sprite.Sprite):
    def __init__(self, edge_length:int, topLeftCorner:tuple[int, int], field_color1:str="yellow", field_color2:str="red", rotation:int=0):
        super().__init__()

        self.__onTurnTeam = 1 # Später natürlich 0
        self.__cursor = None
        self.__eventMode = None 
        self.__running = False

        self.__rotation = rotation
        self.__edge_length = edge_length
        self.__fields_count = 8
        self.__field_length = edge_length//self.__fields_count
        

        self.__field_color_1 = field_color1
        self.__field_color_2 = field_color2

        self.__field_label_start_letter = "a"

        #die Variablen müssen so heißen und public sein wegen Pygame
        self.image = pygame.surface.Surface((edge_length, edge_length))
        self.rect = self.image.get_rect(topleft = topLeftCorner)

        self.__fields = self.__createFields()
        self.__fieldsGroup = self.__createFieldsGroup()
        self.__setupBrett()
        self.update()



    def start(self):
        if self.__running:
            raise "Bereits gestartet!"
        self.__running = True
        self.__eventMode = "chooseFigure"

    def __setupBrett(self):
        #Wird später sauberer geschrieben !!!
        scale = 0.9
        self.__fields["a8"].setFigure(Turm("assets/graphics/s_turm.png", self.__field_length*scale, self.__field_length, 1))
        self.__fields["h8"].setFigure(Turm("assets/graphics/s_turm.png", self.__field_length*scale, self.__field_length, 1))

        self.__fields["b8"].setFigure(Springer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, 1))
        self.__fields["g8"].setFigure(Springer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, 1))
        
        #
        self.__fields["c8"].setFigure(Laeufer("assets/graphics/s_springer.png", self.__field_length*scale, self.__field_length, 1))

    def setRotation(self, rotation:int):
        if rotation % 90 != 0:
            raise "Rotation not available!"
        self.__rotation = rotation
        self.__correctFieldPositions()

    def getRotation(self)->int:
        return self.__rotation
    
    def __correctFieldPositions(self):
        for key in self.__fields.keys():
            currentField = self.__fields[key]
            if type(currentField) != Feld:
                continue
            currentField.setFieldPosition(self.__getFieldPositionByName(key))
        self.__generateImage()

    def __createFields(self)->dict:
        fields = {}
        for spread in range(ord(self.__field_label_start_letter), ord(self.__field_label_start_letter)+self.__fields_count):
            for lengths in range(1, 1+self.__fields_count):
                if (spread+lengths)%2 == 1:
                    color = self.__field_color_1
                else:
                    color = self.__field_color_2 
                field_label = chr(spread) + str(lengths)
                field_current = Feld((self.__field_length, self.__field_length), self.__getFieldPositionByName(chr(spread)+str(lengths)), color, field_label)
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
    

    def __rotatePoint90degree(self, point:tuple[int, int]):
        return (self.__edge_length-point[1]-self.__field_length, point[0])
    
    def __getFieldsGroup(self)->pygame.sprite.Group:
        return self.__fieldsGroup
    
    def __createFieldsGroup(self)->pygame.sprite.Group:
        fieldsGroup = pygame.sprite.Group()
        if type(self.__fields) != dict:
            raise "Error: self.__fields should be a dict!"
        
        for key in self.__fields.keys():
            field = self.__fields[key]
            fieldsGroup.add(field)

        return fieldsGroup

    def __generateImage(self):
        self.image.fill("black")

        fieldsGroup = self.__getFieldsGroup()
        fieldsGroup.draw(self.image)
        
    def update(self):
        self.__generateImage()
    
    def handleClickEvent(self, pos:tuple[int, int]):
        if not(self.__running):
            return
        
        clickedField = self.getFieldByCords(pos)
        if type(clickedField) != Feld:
            return
        clickedFieldLabel = clickedField.getLabel()

        if self.__eventMode == "chooseFigure":
            self.__chooseFigureEvent(clickedField)
        elif self.__eventMode == "setFigure":
            self.__setFigureEvent(clickedField)
        
    def __setFigureEvent(self, clickedField:Feld):
        self.__clearAllFieldHighlights()
        if self.__chooseFigureEvent(clickedField):
            return
        if type(self.__cursor) != Feld:
            raise "Benötigt ein Cursor Feld"
        
        clickedFigure = clickedField.getFigure()
        clickedFieldLabel = clickedField.getLabel()       
        if clickedFigure !=None:
            if clickedFigure.getTeam() == self.__onTurnTeam:
                self.__eventMode = "chooseFigure"
                self.__chooseFigureEvent(clickedField)
                return
            else:
                print("Es wird wohl eine Figur geschlagen!")
        
        if not(clickedField in self.getPossibleTurnFields(self.__cursor)):
            self.__cursor = None
            self.__eventMode = "chooseFigure"
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

            self.__cursor = None
            self.__eventMode = "chooseFigure"
            self.__clearAllFieldHighlights()
            return
        self.__switchToOtherPlayer()
        self.__eventMode = "chooseFigure"
        self.__clearAllFieldHighlights()
        
        


    def __getCheckedTeam(self):
        return None # muss noch ordentlich werden

    def __switchToOtherPlayer(self):
        pass
        #self.__onTurnTeam = (self.__onTurnTeam+1)%2

    def __chooseFigureEvent(self, clickedField:Feld):
        clickedFigure = clickedField.getFigure()
        clickedFieldLabel = clickedField.getLabel()
        if clickedFigure == None:
            self.__clearAllFieldHighlights() # Sollte also eine Figur sein
            return False
        
        if clickedFigure.getTeam() != self.__onTurnTeam:
            return False
        
        self.__markAllPosibleFields(clickedFigure, clickedFieldLabel)
        clickedField.addFieldHighlight("GreenOutlineBox")
        self.__eventMode = "setFigure"
        self.__cursor = clickedField
        return True

    def __clearAllFieldHighlights(self):
        for key in self.__fields.keys():
            field = self.__fields[key]
            if type(field) != Feld:
                continue
            field.clearFieldHighlights()

    def getPossibleTurnFields(self, Field:Feld)->list[tuple]:
        PossibleTurnFields = []
        relativePossibleTurnFields = self.__getPossibleRelativeFields(Field)
        for relativeField in relativePossibleTurnFields:
            field = self.getRelativeField(Field.getLabel(), relativeField)
            if type(field) != Feld:
                continue
            PossibleTurnFields.append(field)
        return PossibleTurnFields



    def __markAllPosibleFields(self, Figure, FigureFieldLabel):
        for field in self.getPossibleTurnFields(self.__fields[FigureFieldLabel]):
            if type(field) != Feld:
                continue
            field.addFieldHighlight("SmallGreenMiddleCircle")

    def __getPossibleRelativeFields(self, Field:Feld):
        Figure = Field.getFigure()
        if Figure == None:
            return []
        canJump = Figure.getCanJump()
        relativeMaybePossibleTurnFields = Figure.getRelativeMaybePossibleTurns(Field.getLabel())
        possibleRelativeFields = []
        for MaybeRelativeField in relativeMaybePossibleTurnFields:
            inspectionField = self.getRelativeField(Field.getLabel(), MaybeRelativeField)
            if inspectionField == None:
                continue           
            possibleRelativeFields.append(MaybeRelativeField)
        if canJump:
            return self.__removeKillOwnFiguresInRelatives(possibleRelativeFields, Field)
        possibleRelativeFields = self.__doNotWalkThroughFigures(possibleRelativeFields, Field)
        return self.__removeKillOwnFiguresInRelatives(possibleRelativeFields, Field)
    
    def __removeKillOwnFiguresInRelatives(self, RelativeFields:list[tuple], StartField:Feld)->list:
        result = []
        for RelativeField in RelativeFields:
            inspectField = self.getRelativeField(StartField.getLabel(), RelativeField)
            if type(inspectField) != Feld:
                continue
            if StartField.getFigure() == None or inspectField.getFigure() == None:
                result.append(RelativeField)
                continue
            if StartField.getFigure().getTeam() == inspectField.getFigure().getTeam():
                continue
            result.append(RelativeField)
        return result
        

    def __doNotWalkThroughFigures(self, possibleRelativeFields:list[tuple], startField:Feld):
        xLine = []
        yLine = []
        DiagonalXandY = []
        DiagonalXdiffY = []
        
        unsortet = possibleRelativeFields.copy()
        for RelativeField in possibleRelativeFields:
            # Vertikal (nur X ändert sich, Y = 0)
            if RelativeField[1] == 0:
                xLine.append(RelativeField)
                unsortet.remove(RelativeField)
                continue
            # Horizontal (nur Y ändert sich, X = 0)
            if RelativeField[0] == 0:
                yLine.append(RelativeField)
                unsortet.remove(RelativeField)
                continue
            # Diagonale: X und Y gleich
            if RelativeField[1] == RelativeField[0]:
                DiagonalXandY.append(RelativeField)
                unsortet.remove(RelativeField)
                continue
            # Diagonale: X und Y entgegengesetzt
            if RelativeField[1] == -RelativeField[0]:
                DiagonalXdiffY.append(RelativeField)
                unsortet.remove(RelativeField)
                continue
        
        if unsortet != []:
            raise "Nicht unterstütztes Bewegungsraster!"
        
        xLines = self.__sortToDestination(xLine, 0)
        yLines = self.__sortToDestination(yLine, 1)
        DiagonalXandY = self.__sortToDestination(DiagonalXandY, 0)
        DiagonalXdiffY = self.__sortToDestination(DiagonalXdiffY, 0)

        resultFields = []
        for lines in [xLines, yLines, DiagonalXandY, DiagonalXdiffY]:
            for line in lines:
                for resultRelative in self.__cutLineAtWalkingThroughFigures(line, startField):
                    resultFields.append(resultRelative)
        return resultFields
    
    def __cutLineAtWalkingThroughFigures(self, Line:list, startField:Feld):
        '''
        Vor.: 'Line' ist nach zunehmenden Abstand sortiert und geht entweder Wagerecht oder Horizontal
        Eff.: -
        Erg.: Eine Liste die nur noch die relativen beinhaltet die von dem startFeld aus, wenn man die Linie von links nach rechts durchläuft nicht durch eine andere Figur läuft, sondern diese schlagen würde.
        '''
        resultLine = []
        for relative in Line:
            inspectField = self.getRelativeField(startField.getLabel(), relative)
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
    
    def __reverseFirstPart(self, Line:list)->list:
        firstPartLine = Line[0]
        if type(firstPartLine) == list:
            firstPartLine.reverse()
        return firstPartLine, Line[1]
    
    def __SpitNegatives(self, Line:list[tuple], SplitNumberIndex)->list:
        LinePositives = []
        LineNegatives = []

        for Element in Line:
            if Element[SplitNumberIndex] < 0:
                LineNegatives.append(Element)
                continue
            LinePositives.append(Element)
        return LineNegatives, LinePositives

    def getRelativeField(self, fieldLabel:str, relativeField:tuple[int, int])->Feld:
        startFieldX = ord(fieldLabel[0])
        startFieldY = int(fieldLabel[1])
        try:
            targetFieldLabel = chr(startFieldX+relativeField[0])+str(startFieldY+relativeField[1])
            targetField = self.__fields[targetFieldLabel]
            
            if type(targetField) != Feld:
                return None
            return targetField
        except:
            return None



    def getFieldByCords(self, pos:tuple[int, int])->Feld:
        x = pos[0]-self.rect.topleft[0]
        y = pos[1]-self.rect.topleft[1]
        if not(self.rect.collidepoint(pos)):
            return 
        
        for key in self.__fields.keys():
            field = self.__fields[key]
            if type(field) != Feld:
                continue 

            field_rect = field.getRect()
            if type(field_rect) != pygame.rect.Rect:
                continue

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
