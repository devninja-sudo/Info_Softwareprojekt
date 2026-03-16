import pygame
from typing import Callable


class Dialog(pygame.sprite.Sprite):
    '''
    Vor.: -DialogWidth- beschreibt eine Breite und ist nicht Negativ.
        -DialogHeight- beschreibt eine Hoehe und ist nicht Negativ.
        -centerPosition- ist vom Typ Tuple und besitzt 2 Integer die den Mittelpunkt des Dialogfensters Beschreiben, wobei der erste für die X-Position steht und der zweite Integer die Y-Achsen Position beschreibt.
        -headline- ist vom Typ String und beschreibt die Überschrift des Dialogfensters.
        -headlineSize- ist ein nicht negativer Integer und beschreibt die Schriftgroesse der Ueberschrift.
        -answers- ist eine Liste, welche weitere Listen als Elemente hat, welche aus einem String bestehen, welcher den Text fuer die Antwortmoeglichkeit beschreibt, und desweiterin eine Funktion oder Methode enthält, welche aufgerufen wird beim klicken auf die Antwortmoeglichkeit, die Methode/Funktion benötigt kein Argument/Parameter.
        -answerSize- ist ein positiver Integer, welcher die Schriftgroesse der Antwortmoeglichkeiten beschreibt.
        -answerDistanceSize- ist ein positiver Integer, welcher den zusaetzlichen Y-Achsen Abstand von den Antwortmoeglichkeiten zu einander beschreibt.
        -closeable- ist bei angabe True oder False und beschreibt, ob beim verarbeiten eines Klickes außerhalb des Feldes das Dialogfenster unsichtbar werden soll, dabei wird das Dialogfenster im geschlossenden Zustand Weiß.
        -onVoidClick- ist bei Angabe eine Methode/Funktion die kein Argument/Parameter benoetigt, diese wird Aufgerufen, wenn ein linker Mausklick verarbeitet wird, jedoch dieser nicht auf einer Antwortmoeglichkeit ausgefuert wurde.
        -posOffset- ist eine Punktangabe als Tuple durch zwei Integer und beschreibt eine zusetzliche Verschiebung des Mittelpunktes.
        -onSurfaceChange- ist bei Angabe eine Methode/Funktion die kein Argument/Parameter benoetigt, diese wird Aufgerufen, wenn die Flaeche von dem Dialogfenster aktualliesiert wurde.
    Eff.: self.image ist eine Surface von einer weißen Box, mit der Breite von -DialogWidth-  und der Hoehe von -DialogHeight- und die Ueberschrift -headline- oben mit der -headlineSize- beschriebenden Groesse mittig traegt.
            Mit Text des ersten Elements aus den Listen, welche in der Liste -answers- stehnen ist die self.image ebenfalls versehen und der Abstand der Antwort moeglichkeiten von den Textelementkanten Unten zu Oben ist durch -answerDistanceSize- beschreibbar.
        self.rect ist ein Rect, welches die gleiche Groesse wie self.image besitzt und die Position der Mitte mit -centerPosition- und bedenken von -posOffset- festgelegt ist.


        Die private Variable:
        -self.__answersDataWithSurface- ist nun zu einer Liste gesetzt,
            welche Tabellen enthaelt mit den Schluesseln "text", welchen den Text von einer angegebenden Antwortmoeglichkeit enthaelt,
            "callable" der angegebenden Funktion/Methode entspricht oder bei keiner Angabe None,
            "surface" einer pygame.Surface, wie die Flaeche fuer die Antwortmoeglichkeiten auszusehen hat beschreibt und
            dem Schluessel "rect", welcher zu der Flaeche gehoert und beschreibt an welcher Stelle sie abgebildet werden soll.
            
    Erg.: Eine Dialoginstanz ist geliefert.
    '''
    def __init__(self, DialogWidth:int, DialogHeight:int, centerPosition:tuple[int, int], headline:str, headlineSize:int, answers:list[list[str, Callable]], answerSize:int, answerDistanceSize:int, closeable:bool, onVoidClick:Callable|None=None, posOffset:tuple[int, int]=(0,0), onSurfaceChange:Callable=None):
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
        '''
        Vor.: - 
        Eff.: Wenn -onSurfaceChange- bei der Initiierung festgelegt wurde und dies Korrekt ausgefuert wurde ist die angegebene Funktion aufgerufen.
        Erg.: -
        '''
        if self.__onSurfaceChange == None:
            return
        self.__onSurfaceChange()

    def createSelfAnswersSurfaceData(self):
        '''
        Vor.: -
        Eff:. -self.__answersDataWithSurface- ist nun zu einer Liste gesetzt,
            welche Tabellen enthaelt mit den Schluesseln "text", welchen den Text von einer angegebenden Antwortmoeglichkeit enthaelt,
            "callable" der angegebenden Funktion/Methode entspricht oder bei keiner Angabe None,
            "surface" einer pygame.Surface, wie die Flaeche fuer die Antwortmoeglichkeiten auszusehen hat beschreibt und
            dem Schluessel "rect", welcher zu der Flaeche gehoert und beschreibt an welcher Stelle sie abgebildet werden soll.
        Erg.: -         
        '''
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
        '''
        Vor.: - 
        Eff.: self.image ist eine Surface von einer weißen Box, mit der Breite von -DialogWidth-  und der Hoehe von -DialogHeight- und die Ueberschrift -headline- oben mit der -headlineSize- beschriebenden Groesse mittig traegt.
            Mit Text des ersten Elements aus den Listen, welche in der Liste -answers- stehnen ist die self.image ebenfalls versehen und der Abstand der Antwort moeglichkeiten von den Textelementkanten Unten zu Oben ist durch -answerDistanceSize- beschreibbar.
            self.rect ist ein Rect, welches die gleiche Groesse wie self.image besitzt und die Position der Mitte mit -centerPosition- und bedenken von -posOffset- festgelegt ist.
        Erg.: -
        '''
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
        '''
        Vor.: -
        Eff.: -self.image- ist nun vollstaendig weiss eingefaerbt.
        Erg.: - 
        '''
        self.__isShown = False
        self.image.fill("white")
        if not(self.__initPhase):
            self.__CallOnSurfaceChange()

    def getIfShown(self)->bool:
        '''
        Vor.: -
        Eff.: -
        Er.: Es ist geliefert, ob -self.image- weiss eingefaerbt ist, weil von den Methoden -hideSurface- und -showSurface- zuletzt -hideSurface- ausgefuert wurde.
        '''
        return self.__isShown

    def showSurface(self):
        '''
        Vor.: -
        Eff.: self.image ist eine Surface von einer weißen Box, mit der Breite von -DialogWidth-  und der Hoehe von -DialogHeight- und die Ueberschrift -headline- oben mit der -headlineSize- beschriebenden Groesse mittig traegt.
            Mit Text des ersten Elements aus den Listen, welche in der Liste -answers- stehnen ist die self.image ebenfalls versehen und der Abstand der Antwort moeglichkeiten von den Textelementkanten Unten zu Oben ist durch -answerDistanceSize- beschreibbar.
        self.rect ist ein Rect, welches die gleiche Groesse wie self.image besitzt und die Position der Mitte mit -centerPosition- und bedenken von -posOffset- festgelegt ist.
        Erg.: - 
        '''
        self.__isShown = True
        self.makeSurface()

    def handleLeftClick(self, pos:tuple[int, int]):
        '''
        Vor.: -pos- ist ein Tuple mit zwei Integern. Er beschreibt die Position der Maus bei einem Mausklick.
        Eff.: Wenn -pos- in dem Berreich einer Antwortmoeglichkeit ist, dann ist sofern angegeben, die fuer die Antwort definierte Methode oder Funktion ausgefuert.
            Wenn -pos- in keinem Berreich einer Antwortmoeglichkeit liegt, dann ist die Methode/Funktion ausgefuert, welche bei der Initiierung mit -onVoidClick- evtl. angegeben wurde ausgefuert und 
            wenn das Dialogfenster schliessbar ist, dann ist es nun weiss eingefaerbt und -self.hideSurface- ist ausgefuert.
        Erg.: - 
        '''
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
                
class TextInputDialog(pygame.sprite.Sprite):
    '''
    Vor.: -DialogWidth- und -DialogHeight- sind nicht negativ.
        -centerPosition- ist ein Tuple mit genau zwei Integern fuer die Mittelpunktposition.
        -headline- und -buttonText- sind Strings.
        -headlineSize-, -inputSize-, -buttonSize- und -maxInputLength- sind positive Integer.
        -closeable- ist ein Bool.
        -onSubmit-, -onVoidClick-, -onSurfaceChange- und -wennZweiterButton- sind entweder None oder aufrufbare Objekte.
        -zweiterKnopfText- ist None oder ein String.
    Eff.: Initialisiert ein Dialog-Sprite mit Eingabefeld, Hauptbutton und evtl Zweitbutton.
        Der aktuelle Eingabewert ist leer, der Dialog ist sichtbar und eone Surface ist erstellt.
    Erg.: Eine TextInputDialog-Instanz ist geliefert.
    '''
    def __init__(self, DialogWidth:int, DialogHeight:int, centerPosition:tuple[int], headline:str, headlineSize:int, inputSize:int, buttonText:str, buttonSize:int, closeable:bool, onSubmit:Callable|None=None, onVoidClick:Callable|None=None, posOffset:tuple[int, int]=(0,0), onSurfaceChange:Callable=None, maxInputLength:int=24, zweiterKnopfText:str|None=None, wennZweiterButton:Callable|None=None):
        super().__init__()
        self.__initPhase = True
        self.__width:int = DialogWidth
        self.__height:int = DialogHeight
        self.__centerPosition:tuple[int] = centerPosition
        self.__headline:str = headline
        self.__headlineSize:int = headlineSize
        self.__inputSize:int = inputSize
        self.__buttonText:str = buttonText
        self.__buttonSize:int = buttonSize
        self.__closeable:bool = closeable
        self.__onSubmit:Callable|None = onSubmit
        self.__onVoidClick:Callable|None = onVoidClick
        self.__posOffset = posOffset
        self.__onSurfaceChange = onSurfaceChange
        self.__maxInputLength:int = maxInputLength
        self.__secondaryButtonText:str|None = zweiterKnopfText
        self.__wennZweiterButton:Callable|None = wennZweiterButton
        self.__isShown = True
        self.__eingabeWert:str = ""
        self.__cursorSichtbar:bool = True
        self.__letzterCursorBlink = pygame.time.get_ticks()
        self.makeSurface()
        self.__initPhase = False

    def __CallOnSurfaceChange(self):
        '''
        Vor.: -
        Eff.: Wenn -onSurfaceChange- gesetzt ist, wird die Funktion exakt genau einmal aufgerufen.
        Erg.: -
        '''
        if self.__onSurfaceChange == None:
            return
        self.__onSurfaceChange()

    def setHeadline(self, headline:str):
        '''
        Vor.: -headline- ist ein String.
        Eff.: Setzt die Überschrift und erstellt die Dialog-Surface neu.
        Erg.: -
        '''
        self.__headline = headline
        self.makeSurface()

    def getValue(self)->str:
        '''
        Vor.: -
        Eff.: -
        Erg.: Der aktuelle Eingabetext ist geliefert.
        '''
        return self.__eingabeWert

    def clearValue(self):
        '''
        Vor.: -
        Eff.: Der gespeicherte Eingabetext wird auf den leeren String gesetzt und die Surface neu erstellt.
        Erg.: -
        '''
        self.__eingabeWert = ""
        self.makeSurface()

    def showSurface(self):
        '''
        Vor.: -
        Eff.: Der Dialog wird als sichtbar markiert und komplett neu gezeichnet.
        Erg.: -
        '''
        self.__isShown = True
        self.makeSurface()

    def hideSurface(self):
        '''
        Vor.: -
        Eff.: Der Dialog wird als unsichtbar markiert, -self.image- weiss gefuellt und ggf. -onSurfaceChange- ausgelöst.
        Erg.: -
        '''
        self.__isShown = False
        self.image.fill("white")
        if not(self.__initPhase):
            self.__CallOnSurfaceChange()

    def getIfShown(self):
        '''
        Vor.: -
        Eff.: -
        Erg.: Es ist geliefert, ob der Dialog aktuell als sichtbar markiert ist.
        '''
        return self.__isShown

    def makeSurface(self):
        '''
        Vor.: -
        Eff.: Erstellt -self.image- und -self.rect-, zeichnet Rahmen, Ueberschrift, Eingabefeld,
            Buttons.
            Wenn nicht in der init, wird -onSurfaceChange- aufgerufen.
        Erg.: -
        '''
        self.image:pygame.surface.Surface = pygame.surface.Surface((self.__width, self.__height))
        self.image.fill("white")
        self.rect:pygame.rect.Rect = self.image.get_rect(center = self.__centerPosition)
        pygame.draw.rect(self.image, "Red", self.image.get_rect(), 4)

        titelFont = pygame.font.Font(None, self.__headlineSize)
        titelSurface = titelFont.render(self.__headline, False, "black").convert()
        self.image.blit(titelSurface, titelSurface.get_rect(centerx = self.__width//2, top = self.__height*0.08))

        eingabeRect = pygame.Rect(self.__width*0.1, self.__height*0.35, self.__width*0.8, self.__height*0.22)
        pygame.draw.rect(self.image, "black", eingabeRect, 2)

        eingabeFont = pygame.font.Font(None, self.__inputSize)
        textZumRendern = self.__eingabeWert
        if self.__cursorSichtbar and self.__isShown:
            textZumRendern += "|"
        eingabeSurface = eingabeFont.render(textZumRendern, False, "black").convert()
        self.image.blit(eingabeSurface, eingabeSurface.get_rect(midleft=(eingabeRect.left + 8, eingabeRect.centery)))

        buttonFont = pygame.font.Font(None, self.__buttonSize)
        self.__buttonSurface = buttonFont.render(self.__buttonText, False, "black").convert()
        buttonCenterY = int(self.__height*0.78)
        if self.__secondaryButtonText == None:
            self.__buttonRect = self.__buttonSurface.get_rect(center=(self.__width//2, buttonCenterY))
        else:
            self.__buttonRect = self.__buttonSurface.get_rect(center=(int(self.__width*0.68), buttonCenterY))
        self.image.blit(self.__buttonSurface, self.__buttonRect)

        self.__secondaryButtonRect = None
        if self.__secondaryButtonText != None:
            self.__secondaryButtonSurface = buttonFont.render(self.__secondaryButtonText, False, "black").convert()
            self.__secondaryButtonRect = self.__secondaryButtonSurface.get_rect(center=(int(self.__width*0.32), buttonCenterY))
            self.image.blit(self.__secondaryButtonSurface, self.__secondaryButtonRect)

        if not(self.__initPhase):
            self.__CallOnSurfaceChange()

    def update(self):
        '''
        Vor.: -
        Eff.: Solange der Dialog sichtbar ist, blinkt der Cursor im Eingabefeld. Da keine Animation wird für jedes Blinken die Surface neu gezeichnet.
        Erg.: -
        '''
        if not(self.__isShown):
            return
        jetzt = pygame.time.get_ticks()
        if jetzt - self.__letzterCursorBlink >= 450:
            self.__cursorSichtbar = not(self.__cursorSichtbar)
            self.__letzterCursorBlink = jetzt
            self.makeSurface()

    def handleLeftClick(self, pos:tuple[int, int]):
        '''
        Vor.: -pos- ist ein Tuple aus zwei Integern (Mausposition im Fenster).
        Eff.: Verarbeitet einen Linksklick relativ zum Dialog:
            Klick auf Zweitbutton ruft -wennZweiterButton- auf,
            Klick auf Hauptbutton ruft -onSubmit- mit aktuellem Eingabetext auf,
            ansonsten wird ggf. -onVoidClick- ausgefuehrt und bei -closeable=True- der Dialog versteckt.
        Erg.: -
        '''
        if not(self.__isShown):
            return
        localPos = (pos[0] - self.rect.x - self.__posOffset[0], pos[1] - self.rect.y - self.__posOffset[1])
        didNoAction = True
        if self.__secondaryButtonRect != None and self.__secondaryButtonRect.collidepoint(localPos):
            if self.__wennZweiterButton != None:
                self.__wennZweiterButton()
            didNoAction = False
        if self.__buttonRect.collidepoint(localPos):
            if self.__onSubmit != None:
                self.__onSubmit(self.__eingabeWert)
            didNoAction = False
        if didNoAction:
            if self.__onVoidClick != None:
                self.__onVoidClick()
            if self.__closeable:
                self.hideSurface()

    def handleKeyDown(self, event:pygame.event.Event):
        '''
        Vor.: -event- ist ein pygame.KEYDOWN-Event mit gueltigen Attributen -key- und -unicode-.
        Eff.: Verarbeitet Tastatureingaben fuer den Dialog:
            ENTER ruft -onSubmit- mit aktuellem Eingabetext auf,
            BACKSPACE entfernt das letzte Zeichen,
            sonst wird ein druckbares Einzelzeichen (bis -maxInputLength-) angehaengt.
            Bei Textaenderung wird die Surface neu erstellt.
        Erg.: -
        '''
        if not(self.__isShown):
            return
        if event.key == pygame.K_RETURN:
            if self.__onSubmit != None:
                self.__onSubmit(self.__eingabeWert)
            return
        if event.key == pygame.K_BACKSPACE:
            if len(self.__eingabeWert) != 0:
                self.__eingabeWert = self.__eingabeWert[:-1]
                self.makeSurface()
            return
        if len(self.__eingabeWert) >= self.__maxInputLength:
            return
        text = event.unicode
        if len(text) != 1:
            return
        if not(text.isprintable()):
            return
        if text in ["\t", "\n", "\r"]:
            return
        self.__eingabeWert += text
        self.makeSurface()

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
        

