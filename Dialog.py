import pygame
from typing import Callable


class Dialog(pygame.sprite.Sprite):
    def __init__(self, DialogWidth:int, DialogHeight:int, centerPosition:tuple[int], headline:str, headlineSize:int, answers:list[list[str, Callable]], answerSize:int, answerDistanceSize:float, closeable:bool, onVoidClick:Callable|None=None, posOffset:tuple[int, int]=(0,0), onSurfaceChange:Callable=None):
        super().__init__()
        self.__initPhase = True
        self.__width:int = DialogWidth
        self.__height:int = DialogHeight
        self.__centerPosition:tuple[int] = centerPosition
        self.__headline:str = headline
        self.__headlineSize:int = headlineSize
        self.__answerSize:int = answerSize
        self.__answerDistanceSize:int = answerDistanceSize
        self.__answers:list[list[str, Callable]] = answers
        self.__closeable:bool = closeable
        self.__onVoidClick:Callable|None = onVoidClick
        self.__posOffset = posOffset
        self.__onSurfaceChange = onSurfaceChange
        self.createSelfAnswersSurfaceData()
        self.makeSurface()
        self.__isShown = True
        
        self.__initPhase = False
        pass

    def __CallOnSurfaceChange(self):
        if self.__onSurfaceChange == None:
            return
        self.__onSurfaceChange()

    def createSelfAnswersSurfaceData(self):
        dialogAnswerFont = pygame.font.Font(None, self.__answerSize)
        self.__answersDataWithSurface:list[dict] = []
        for answer in self.__answers:
            i = self.__answers.index(answer)
            answerData = {}
            answerData["text"] = answer[0]
            answerData["callable"] = answer[1]
            answerData["surface"] = dialogAnswerFont.render(answer[0], False, 'black').convert()
            if i == 0:
                answerData["rect"] = answerData["surface"].get_rect(topleft = (self.__width*0.05, self.__height*self.__answerDistanceSize))
            else:
                answerBefore = self.__answersDataWithSurface[i-1]
                answerBeforeRect:pygame.rect.Rect = answerBefore["rect"]
                answerData["rect"] = answerData["surface"].get_rect(topleft = (self.__width*0.05, self.__height*self.__answerDistanceSize+answerBeforeRect.height*i))
            self.__answersDataWithSurface.append(answerData)

    def makeSurface(self):
        self.image:pygame.surface.Surface = pygame.surface.Surface((self.__width, self.__height))
        self.image.fill("white")
        self.rect:pygame.rect.Rect = self.image.get_rect(center = self.__centerPosition)
        pygame.draw.rect(self.image, "Red", self.image.get_rect(), 4)


        dialogHeadlineFont = pygame.font.Font(None, self.__headlineSize)
        self.questionTextSurface = dialogHeadlineFont.render(self.__headline, False, 'black').convert()
        self.image.blit(self.questionTextSurface, self.questionTextSurface.get_rect(centerx = self.__width//2, top = self.__height*0.05))
        for answerData in self.__answersDataWithSurface:
            self.image.blit(answerData["surface"], answerData["rect"])
        if not(self.__initPhase):
            self.__CallOnSurfaceChange()

    def hideSurface(self):
        self.__isShown = False
        self.image.fill("white")
        if not(self.__initPhase):
            self.__CallOnSurfaceChange()

    def getIfShown(self):
        return self.__isShown

    def showSurface(self):
        self.__isShown = True
        self.makeSurface()

    def handleLeftClick(self, pos:tuple[int, int]):
        didNoAction = True
        if not(self.__isShown):
            return
        for answer in self.__answersDataWithSurface:
            AnswerRect:pygame.rect.Rect = answer["rect"]
            if AnswerRect.collidepoint(pos[0] - self.rect.x - self.__posOffset[0], pos[1] - self.rect.y - self.__posOffset[1]):
                if answer["callable"] != None:
                    answer["callable"]()
                    didNoAction = False
                    break
        if didNoAction:
            if self.__onVoidClick != None:
                self.__onVoidClick()
            if self.__closeable:
                self.hideSurface()

def click():
    #TestDialog.hideSurface()
    print("weg")
    

def Dame():
    print("Dame")

def Bauer():
    print("Bauer")


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Dialog Test')
    clock = pygame.time.Clock()


    TestDialogGroup = pygame.sprite.GroupSingle()
    TestDialog = Dialog(300, 200, (600, 300), "Geht es?", 60, [["Dame", Dame], ["Bauer", Bauer]], 40, 0.3, closeable=True, onVoidClick=click)
    TestDialogGroup.add(TestDialog)
    
    while True:
        screen.fill("white")
        
        
        if TestDialogGroup != None:
            TestDialogGroup.draw(screen)
            TestDialogGroup.update()
        pygame.display.update()
        

