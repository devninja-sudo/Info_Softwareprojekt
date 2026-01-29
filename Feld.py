import pygame
from sys import exit

class Feld(pygame.sprite.Sprite):
    def __init__(self, size:tuple[int, int], topLeftCorner:tuple[int, int], color:str, label:str="undefined"):
        super().__init__()

        self.color = color
        self.__figure = None
        self.__size = size
        self.__label = label

        self.image = pygame.surface.Surface(self.__size)
        self.rect = self.image.get_rect(topleft = topLeftCorner)

        self.__effects = []
        self.__effectKeyHighlight = "Highlight"
        self.__FigurGroup = pygame.sprite.GroupSingle()

        self.update()

    def getLabel(self):
        return self.__label

    def setFieldPosition(self, topLeftCorner:tuple[int, int]):
        self.rect.topleft = topLeftCorner

    def update(self):
        self.__generateFieldSurface()
        self.__FigurGroup.draw(self.image)
        

    def __generateFieldSurface(self):
        self.image.fill(self.color)
        for effect in self.__effects:
            if effect[0] == self.__effectKeyHighlight:
                HighlightDescription = effect[1]
                imageRect = self.image.get_rect()
                if HighlightDescription == "SmallGreenMiddleCircle":
                    pygame.draw.circle(surface=self.image, color="green", center=imageRect.center, radius=self.__size[0]*0.3)
                elif HighlightDescription == "GreenOutlineBox":
                    pygame.draw.rect(self.image, "green", imageRect, self.__size[0]//15)

        

    def getRect(self)->pygame.rect.Rect:
        return self.rect
    
    def __getFigureGroup(self)->pygame.sprite.GroupSingle:
        return self.__FigurGroup


    def setFigure(self, Figure):
        self.__FigurGroup.empty()
        self.__figure = Figure
        if Figure is not None:
            self.__FigurGroup.add(self.__figure)
        self.update()

    def getFigure(self):
        return self.__figure

    def addFieldHighlight(self, HighlightType:str):
        self.__effects.append([self.__effectKeyHighlight, HighlightType])
        self.update()
    
    def clearFieldHighlights(self):
        for effect in self.__effects:
            if effect[0] == self.__effectKeyHighlight:
                self.__effects.remove(effect)
        self.update()
            

    def removeFieldHighlight(self, HighlightType:str):
        self.__effects.remove([self.__effectKeyHighlight, HighlightType])
        self.update()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Feld Test')
    clock = pygame.time.Clock()


    TestFeldGroup = pygame.sprite.GroupSingle()
    TestFeld = Feld((50, 50), (10, 10), "yellow")
    TestFeldGroup.add(TestFeld)
    TestFeld.addFieldHighlight("SmallGreenMiddleCircle")
    while True:
        for event in pygame.event.get():
	        if event.type == pygame.QUIT:
                  pygame.quit()
                  exit()
        TestFeldGroup.draw(screen)
        TestFeldGroup.update()
        pygame.display.update()
        clock.tick(60)
