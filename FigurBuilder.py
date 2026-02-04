import pygame
from sys import exit


class FigurBuilder(pygame.sprite.Sprite):
    def __init__(self, image:str, size:int, field_length:int, field_count:int, fieldLabelStartLetter:str, teamID:int, canJump:bool, KillMates:bool=False):
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

        self.__hasKingRole:bool = False


        self.__movedAmount:int = 0

    def setKingRole(self, kingRole:bool)->None:
        self.__hasKingRole = kingRole

    def getKingRole(self)->bool:
        return self.__hasKingRole
    
    def getTeam(self)->int:
        return self.__team
    
    def moved(self):
        self.__movedAmount +=1
    
    def undoMovedCounterbyOne(self):
        self.__movedAmount -=1

    def getHasMoved(self)->bool:
        return self.__movedAmount != 0
    
    def getMovedAmount(self)->int:
        return self.__movedAmount
    
    def getCanJump(self)->bool:
        return self.__canJump
    
    def getCanKillMates(self)->bool:
        return self.__KillMates
    
    def setFieldCount(self, field_count:int)->None:
        self.__field_count = field_count

    def setFieldLabelStartLetter(self, Letter:str)->None:
        self.__fieldLabelStartLetter = Letter

    def __getIsFieldLabelValid(self, testFieldlabel:str):
        lowestLetterID:int = ord(self.__fieldLabelStartLetter)
        maxLetterID:int = lowestLetterID+self.__field_count
        lowestNumber:int = 1
        testFieldlabelLetterID:int = ord(testFieldlabel[0])
        testFieldlabelNumberID:int = int(testFieldlabel[1:])

        return lowestLetterID <= testFieldlabelLetterID <= maxLetterID and lowestNumber <= testFieldlabelNumberID <= self.__field_count


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
    
    def getNewZugListWithAddingRelative(self, originFieldLabel:str, oldZugList:list, RelativePoint:tuple[int, int], onlyOnKill:bool, canKill:bool=True, hasAnxiety:bool=False, specialMoveLabel:str|None = None, needFigureOnField:str|None = None, needFigureType:type|None = None,  allowNeededFigureHasTurned:bool|None = None, endPointNeededFigure:str|None = None)->list[dict]:
        newTurn = {}
        newTurn["point"] = RelativePoint
        fieldLabel:str|None = self.convertRelativePointToFieldLabel(originFieldLabel, RelativePoint)
        if fieldLabel == None:                          # Wenn der Zug außerhalb des Brettes gehen würde -> wird fieldLabel == None zu True
            return oldZugList
        newTurn["fieldLabel"] = fieldLabel
        newTurn["onlyOnKill"] = onlyOnKill
        newTurn["canKill"] = canKill
        
        if self.__hasKingRole:
            newTurn["hasAnxiety"] = True
        else:
            newTurn["hasAnxiety"] = hasAnxiety

        newTurn["specialTurnType"] = specialMoveLabel
        newTurn["needFigureOnField"] = needFigureOnField
        newTurn["neededFigureType"] = needFigureType
        newTurn["allowNeededFigureHasTurned"] = allowNeededFigureHasTurned
        newTurn["endPointNeededFigure"] = endPointNeededFigure
        
        

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