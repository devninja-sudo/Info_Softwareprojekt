import pygame
from sys import exit
from Dame import Dame
from Bauer import Bauer
from Laeufer import Laeufer
from Springer import Springer
from Turm import Turm
from Koenig import Koenig


class Feld(pygame.sprite.Sprite):
    '''
    Vor.: -size- ist ein Tuple mit 2 positiven Integern, 
        der erste beschreibt die Feldbreite und der zweite beschreibt die Feldhoehe. 
        -topLeftCorner- ist ein Tuple mit 2 positiven Integern, 
        der erste beschreibt die X-Position des Feldes und die zweite beschreibt die Y-Position des Feldes.
        -color- ist ein String, welcher eine gueltige Farbe von Pygame beschreibt.
        -label- ist ein String, welcher die Bezeichnung des Feldes beschreibt, 
                wenn dieser nicht definiert ist entspricht dieser "undefined".
    Eff.: -
    Erg.: Ein Feld ist geliefert, welcher pygame.sprite.Sprite geerbt hat.
    '''
    def __init__(self, size:tuple[int, int], topLeftCorner:tuple[int, int], color:str, label:str="undefined"):
        super().__init__()

        self.color:str = color
        self.__figure:None|Springer|Turm|Bauer|Laeufer|Dame|Koenig = None
        self.__size:tuple[int, int] = size
        self.__label:str = label

        self.image:pygame.Surface = pygame.surface.Surface(self.__size)
        self.rect:pygame.Rect = self.image.get_rect(topleft = topLeftCorner)

        self.__effects:list = []
        self.__effectKeyHighlight:str = "Highlight"
        self.__FigureGroup:pygame.sprite.Group = pygame.sprite.GroupSingle()

        self.update()

    def getLabel(self)->str:
        '''
        Vor.: - 
        Eff.: -
        Erg.: Die Bezeichnung des Feldes ist als String geliefert.
        '''
        return self.__label

    def setFieldPosition(self, topLeftCorner:tuple[int, int])->None:
        self.rect.topleft = topLeftCorner

    def update(self)->None:
        '''
        Vor.: -
        Eff.: Die Flaeche -self.image- ist mit Feld und Flaechengrafik aktualiesiert und bereit um ggf. auf den Bildschirm gezeichnet zu werden.
        Erg.: -        
        '''
        self.__drawFieldSurface()
        self.__FigureGroup.draw(self.image)
        

    def __drawFieldSurface(self)->None:
        '''
        Vor.: -
        Eff.: Die Flaeche -self.image- ist mit dem Feld und Effekten ueberschrieben.
        Erg.: -        
        '''
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
        '''
        Vor.: -
        Eff.: - 
        Erg.: Das Rechteck (Pygame Rect - beschreibt den Ort und der Groesse der Flaeche) von 
              der Oberflaeche (Pygame Surface - vereinfacht ein Grafikpapier fuer Python) vom Feld ist geliefert.
        '''
        return self.rect
    
    def __getFigureGroup(self)->pygame.sprite.GroupSingle:
        '''
        Vor.: -
        Eff.: -
        Erg.: Die Pygame Gruppe mit der Figur (Ist eine Pygame Sprite) auf dem Feld ist geliefert. 
        '''
        return self.__FigureGroup


    def setFigure(self, Figure:None|Springer|Turm|Bauer|Laeufer|Dame|Koenig):
        '''
        Vor.: -Figure- ist vom Typ: None, Springer, Turm, Bauer, Laeufer, Dame oder Koenig
        Eff.: Die Figur auf dem Feld ist zu der angegebenden -Figure- gesetzt, wenn -Figure- mit None angegeben wurde ist die Figur auf dem Feld entfernt.
        Erg.: -
        '''
        self.__FigureGroup.empty()
        self.__figure = Figure
        if Figure is not None:
            self.__FigureGroup.add(self.__figure)
        self.update()

    def getFigure(self) -> None|Springer|Turm|Bauer|Laeufer|Dame|Koenig:
        '''
        Vor.: -
        Eff.: -
        Erg.: Die Figur, welche auf dem Feld steht ist geliefert, wenn keine auf dem Feld steht ist None geliefert.'''
        return self.__figure

    def addFieldHighlight(self, HighlightType:str) -> None:
        '''
        Vor.: -HighlightType- ist vom Typ String und entspricht "SmallGreenMiddleCircle" oder "GreenOutlineBox".
        Eff.: Wenn -HighlightType- "SmallGreenMiddleCircle" entspricht ist in der Mitte des Feldes auf der Feldflaeche ein Efffekt mit gruenem Kreis abgebildet.
            Wenn -HighlightType- "GreenOutlineBox" entspricht ist auf der Feldflaeche ein Efffekt mit einer gruenen Aussenline abgebildet.
        Erg.: -
        '''
        self.__effects.append([self.__effectKeyHighlight, HighlightType])
        self.update()
    
    def clearFieldHighlights(self) -> None:
        '''
        Vor.: -
        Eff.: Die Feldflaeche ist nun frei von Effekten, welche mit addFieldHighlight hinzugefuegt wurden. 
        Erg.: -
        '''
        for effect in self.__effects:
            if effect[0] == self.__effectKeyHighlight:
                self.__effects.remove(effect)
        self.update()
            

    def removeFieldHighlight(self, HighlightType:str) -> None:
        '''
        Vor.: -HighlightType- ist vom Typ String und entspricht "SmallGreenMiddleCircle" oder "GreenOutlineBox".
        Eff.: Die Feldflaeche ist nun frei von dem Effekt mit der Bezeichnung -HighlightType-, welcher mit der Methode addFieldHighlight ggf. auf dem Feld abgebildet wurde. 
        Erg.: -
        '''
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
