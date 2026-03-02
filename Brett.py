import pygame
from sys import exit
import socket
import threading
from Feld import Feld
from Springer import Springer
from Turm import Turm
from Laeufer import Laeufer
from Dame import Dame
from Bauer import Bauer
from Koenig import Koenig
from Dialog import Dialog, TextInputDialog
from time import time

class Brett(pygame.sprite.Sprite):
    def __init__(self, edge_length:int, topLeftCorner:tuple[int, int], field_color1:str="yellow", field_color2:str="red", rotation:int=0):
        super().__init__()

        self.SetupTurnVars()
        self.__setupNetzwerkVars()

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

        self.__DialogGroup = pygame.sprite.Group()
        self.setupDialogGroup()

        self.__fields:dict[str:Feld] = self.__createFields()
        self.__fieldsGroup:pygame.sprite.Group = self.__createFieldsGroup()
        self.__setupBrett()
        self.__generateImage()
        self.__resignDialog.hideSurface()
        self.__setupStartDialogs()

    def SetupTurnVars(self):
        self.__onTurnTeam:int = 0 
        self.__cursor = None
        self.__eventMode:str = None 
        self.__running:bool = False
        self.__turnNumber:int = 0
        self.__PawnPromotes:list = []

    def __setupNetzwerkVars(self):
        self.__startKlar:bool = False
        self.__netzAktiv:bool = False
        self.__netzPort:int = 55555
        self.__netzSock:socket.socket|None = None
        self.__netzBuffer:str = ""
        self.__netzVerbundenEvent = threading.Event()
        self.__netzEmpfangThread:threading.Thread|None = None
        self.__netzListenerThread:threading.Thread|None = None
        self.__netzSucheThread:threading.Thread|None = None
        self.__spielerName:str = ""
        self.__meinTeam:int = 0
        self.__wendeRemoteZugAn:bool = False
        self.__modusDialog:Dialog|None = None
        self.__nameDialog:TextInputDialog|None = None
        self.__netzStatusDialog:Dialog|None = None
        self.__startDialogGruppe = pygame.sprite.Group()

    def __setupStartDialogs(self):
        self.__startDialogGruppe.empty()
        self.__modusDialog = Dialog(
            self.rect.width, self.rect.height,
            (self.rect.width//2, self.rect.height//2),
            "Spielmodus wählen", self.rect.height//10,
            [
                ["Singleplayer", self.__waehleSingleplayer],
                ["Multiplayer (LAN)", self.__zeigeNameDialog]
            ],
            self.rect.height//8, 0.42, False,
            onVoidClick=self.__generateImage,
            posOffset=self.rect.topleft,
            onSurfaceChange=self.__generateImage
        )
        self.__startDialogGruppe.add(self.__modusDialog)
        self.__generateImage()

    def __zeigeNameDialog(self):
        self.__nameDialog = TextInputDialog(
            self.rect.width, self.rect.height,
            (self.rect.width//2, self.rect.height//2),
            "Name eingeben", self.rect.height//10,
            self.rect.height//10,
            "Weiter", self.rect.height//10,
            False,
            onSubmit=self.__uebernehmeSpielerName,
            onVoidClick=self.__generateImage,
            posOffset=self.rect.topleft,
            onSurfaceChange=self.__generateImage,
            maxInputLength=24
        )
        self.__startDialogGruppe.empty()
        self.__startDialogGruppe.add(self.__nameDialog)
        self.__generateImage()

    def __zeigeNetzStatusDialog(self, headline:str):
        self.__netzStatusDialog = Dialog(
            self.rect.width, self.rect.height,
            (self.rect.width//2, self.rect.height//2),
            headline, self.rect.height//14,
            [["Erneut suchen", self.__starteNetzSuche]],
            self.rect.height//10, 0.7, False,
            onVoidClick=self.__generateImage,
            posOffset=self.rect.topleft,
            onSurfaceChange=self.__generateImage
        )
        self.__startDialogGruppe.empty()
        self.__startDialogGruppe.add(self.__netzStatusDialog)
        self.__generateImage()

    def __waehleSingleplayer(self):
        self.__netzAktiv = False
        self.__startDialogGruppe.empty()
        self.__startKlar = True
        self.start()
        self.__generateImage()

    def __uebernehmeSpielerName(self, playerName:str):
        playerName = playerName.strip()
        if playerName == "":
            if self.__nameDialog != None:
                self.__nameDialog.setHeadline("Name darf nicht leer sein")
            return
        self.__spielerName = playerName
        self.__starteMultiplayer()

    def __starteMultiplayer(self):
        self.__netzAktiv = True
        self.__zeigeNetzStatusDialog("Suche im LAN nach Schachpartie")
        if self.__netzListenerThread == None or not(self.__netzListenerThread.is_alive()):
            self.__netzListenerThread = threading.Thread(target=self.__listenerWorker, daemon=True)
            self.__netzListenerThread.start()
        self.__starteNetzSuche()

    def __starteNetzSuche(self):
        if self.__netzVerbundenEvent.is_set():
            return
        if self.__netzSucheThread != None and self.__netzSucheThread.is_alive():
            return
        self.__netzSucheThread = threading.Thread(target=self.__discoveryWorker, daemon=True)
        self.__netzSucheThread.start()

    def __holeLokaleIp(self)->str:
        return socket.gethostbyname(socket.gethostname())

    def __listenerWorker(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("0.0.0.0", self.__netzPort))
        listener.listen(3)
        while self.__netzAktiv and not(self.__netzVerbundenEvent.is_set()):
            conn, _addr = listener.accept()
            raw = conn.recv(2048)
            if len(raw) == 0:
                conn.close()
                continue
            msgText = raw.decode("utf-8").strip()
            msgParts = msgText.split(";")
            if len(msgParts) < 2 or msgParts[0] != "ASK":
                conn.close()
                continue
            if self.__netzVerbundenEvent.is_set():
                conn.sendall("BUSY\n".encode("utf-8"))
                conn.close()
                continue
            conn.sendall(("OK;" + self.__spielerName + "\n").encode("utf-8"))
            self.__setzeNetzSocket(conn, 1)
            return

    def __discoveryWorker(self):
        localIp = self.__holeLokaleIp()
        chunks = localIp.split(".")
        if len(chunks) != 4:
            self.__zeigeNetzStatusDialog("LAN-Suche fehlgeschlagen")
            return
        prefix = f"{chunks[0]}.{chunks[1]}.{chunks[2]}"
        own = int(chunks[3])
        for host in range(1, 41):
            if not(self.__netzAktiv) or self.__netzVerbundenEvent.is_set():
                return
            if host == own:
                continue
            target = f"{prefix}.{host}"
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if sock.connect_ex((target, self.__netzPort)) != 0:
                sock.close()
                continue
            sock.sendall(("ASK;" + self.__spielerName + "\n").encode("utf-8"))
            raw = sock.recv(2048)
            if len(raw) == 0:
                sock.close()
                continue
            responseText = raw.decode("utf-8").strip()
            if responseText.startswith("OK;"):
                self.__setzeNetzSocket(sock, 0)
                return
            sock.close()
        if not(self.__netzVerbundenEvent.is_set()):
            self.__zeigeNetzStatusDialog("Kein Spiel gefunden, warte auf Anfrage")

    def __setzeNetzSocket(self, sock:socket.socket, localTeam:int):
        if self.__netzVerbundenEvent.is_set():
            sock.close()
            return
        self.__netzSock = sock
        self.__meinTeam = localTeam
        self.__netzVerbundenEvent.set()
        self.__startDialogGruppe.empty()
        self.__startKlar = True
        self.start()
        self.__starteNetzEmpfang()
        self.__generateImage()

    def __starteNetzEmpfang(self):
        if self.__netzEmpfangThread != None and self.__netzEmpfangThread.is_alive():
            return
        self.__netzEmpfangThread = threading.Thread(target=self.__receiverWorker, daemon=True)
        self.__netzEmpfangThread.start()

    def __receiverWorker(self):
        while self.__netzAktiv and self.__netzVerbundenEvent.is_set():
            if self.__netzSock == None:
                return
            raw = self.__netzSock.recv(4096)
            if len(raw) == 0:
                return
            self.__netzBuffer += raw.decode("utf-8")
            while "\n" in self.__netzBuffer:
                line, self.__netzBuffer = self.__netzBuffer.split("\n", 1)
                line = line.strip()
                if line == "":
                    continue
                parts = line.split(";")
                if len(parts) >= 3 and parts[0] == "MOVE":
                    self.__setzeRemoteZug(parts[1], parts[2])
                    continue
                if len(parts) >= 3 and parts[0] == "PROMO":
                    self.__setzeRemotePromo(parts[1], parts[2])

    def __sendeNetzMessage(self, text:str):
        if not(self.__netzAktiv) or not(self.__netzVerbundenEvent.is_set()):
            return
        if self.__netzSock == None:
            return
        self.__netzSock.sendall((text + "\n").encode("utf-8"))

    def __setzeRemoteZug(self, startLabel:str, targetLabel:str):
        startField = self.__fields.get(startLabel)
        targetField = self.__fields.get(targetLabel)
        if type(startField) != Feld or type(targetField) != Feld:
            return
        self.__wendeRemoteZugAn = True
        self.__eventMode = "chooseFigure"
        self.__chooseFigureEvent(startField)
        self.__setFigureEvent(targetField)
        self.__wendeRemoteZugAn = False
        self.__generateImage()

    def __setzeRemotePromo(self, fieldLabel:str, pieceName:str):
        field = self.__fields.get(fieldLabel)
        if type(field) != Feld:
            return
        figure = field.getFigure()
        if type(figure) != Bauer:
            return
        if pieceName == "TURM":
            if figure.getTeam() == 0:
                field.setFigure(self.__whiteTower)
            else:
                field.setFigure(self.__blackTower)
        elif pieceName == "LAEUFER":
            if figure.getTeam() == 0:
                field.setFigure(self.__whiteBishop)
            else:
                field.setFigure(self.__blackBishop)
        elif pieceName == "SPRINGER":
            if figure.getTeam() == 0:
                field.setFigure(self.__whiteKnight)
            else:
                field.setFigure(self.__blackKnight)
        elif pieceName == "DAME":
            if figure.getTeam() == 0:
                field.setFigure(self.__whiteQueen)
            else:
                field.setFigure(self.__blackQueen)
        else:
            return
        self.__generateImage()


    
    def restartGame(self):
        self.__reset_game_state()
        if self.__netzAktiv:
            self.__startKlar = True
        self.start()
    
    def getFieldRow(self, RowNumber:int)->list[Feld]:
        RowFields = []
        for i in range(self.__fields_count):
            letter = chr(ord(self.__field_label_start_letter)+i)
            RowFields.append(self.__fields[letter+str(RowNumber)])
        return RowFields
    
    def setupDialogGroup(self):
        self.__DialogGroup.empty()
        self.__resignDialog = Dialog(
            self.rect.width, self.rect.height, 
            (self.rect.width//2, self.rect.height//2), 
            "Was möchtest du tun?", self.rect.height//8, 
            [["Neues Spiel!", self.restartGame]], 
            self.rect.height//5, 0.4, True, 
            onVoidClick=self.__generateImage, 
            posOffset=self.rect.topleft, 
            onSurfaceChange=self.__generateImage
        )
        self.__DialogGroup.add(self.__resignDialog)

    def __reset_game_state(self):
        self.__DialogGroup.empty()
        self.__fieldsGroup.empty()
        
        for field in self.__fields.values():
            figure = field.getFigure()
            if figure is not None:
                figure.kill()
            field.setFigure(None)
        
        self.__fields.clear()
        self.__fields = self.__createFields()
        self.__fieldsGroup = self.__createFieldsGroup()
        
        self.setupDialogGroup()
        self.__resignDialog.hideSurface()
        
        self.SetupTurnVars()
        
        self.__setupBrett()
        self.__generateImage()

    def start(self)->None:
        if self.__running:
            raise Exception("Bereits gestartet!")
        if not(self.__startKlar):
            return
        self.__running = True
        self.__eventMode = "chooseFigure"

    def __setupBrett(self)->None:
        #Wird später sauberer geschrieben !!!
        self.__FigureScale:float = 0.9
        self.__blackTower = Turm("assets/graphics/s_turm.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1)
        self.__whiteTower = Turm("assets/graphics/w_turm.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0)
        
        self.__blackQueen = Dame("assets/graphics/s_dame.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1)
        self.__whiteQueen = Dame("assets/graphics/w_dame.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0)
        
        self.__blackKnight = Springer("assets/graphics/s_springer.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1)
        self.__whiteKnight = Springer("assets/graphics/w_springer.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0)
        
        self.__blackBishop = Laeufer("assets/graphics/s_laeufer.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1)
        self.__whiteBishop = Laeufer("assets/graphics/w_laeufer.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0)
        
        self.__blackKing = Koenig("assets/graphics/s_koenig.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 1)
        self.__whiteKing= Koenig("assets/graphics/w_koenig.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0)
        
        self.__fields["a8"].setFigure(self.__blackTower)
        self.__fields["h8"].setFigure(self.__blackTower)

        self.__fields["a1"].setFigure(self.__whiteTower)
        self.__fields["h1"].setFigure(self.__whiteTower)
        
        self.__fields["b8"].setFigure(self.__blackKnight)
        self.__fields["g8"].setFigure(self.__blackKnight)
            
        self.__fields["c8"].setFigure(self.__blackBishop)
        self.__fields["f8"].setFigure(self.__blackBishop)

        self.__fields["d8"].setFigure(self.__blackQueen)
        self.__fields["e8"].setFigure(self.__blackKing)

        self.__buildPawnRow(7, self.__FigureScale, "assets/graphics/s_bauer.png", 1)
        self.__buildPawnRow(2, self.__FigureScale, "assets/graphics/w_bauer.png", 0)

        self.__fields["b1"].setFigure(self.__whiteKnight)
        self.__fields["g1"].setFigure(self.__whiteKnight)
    
        self.__fields["c1"].setFigure(self.__whiteBishop)
        self.__fields["f1"].setFigure(self.__whiteBishop)

        self.__fields["d1"].setFigure(self.__whiteQueen)
        self.__fields["e1"].setFigure(self.__whiteKing)

    def __buildPawnRow(self, RowNumber:int, scale:float, texturePath:str, teamID:int) -> None:
        for i in range(self.__fields_count):
            fieldLabelLetter:str = chr(ord(self.__field_label_start_letter)+i)
            fieldLabel:str = fieldLabelLetter + str(RowNumber)
            targetField:Feld = self.__fields[fieldLabel]
            targetField.setFigure(Bauer(texturePath, self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, teamID))

    def setRotation(self, rotation:int)->None:
        if rotation % 90 != 0:
            raise Exception("Rotation not available!")
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
            raise Exception("Rotation not available!")
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
        if len(self.__startDialogGruppe.sprites()) != 0:
            self.__startDialogGruppe.draw(self.image)
        if self.__resignDialog.getIfShown():
            print("true")
            self.__DialogGroup.draw(self.image)
        for PromoteData in self.__PawnPromotes:
            if PromoteData["Dialog"].getIfShown():
                PromoteData["Group"].draw(self.image)
        
        
    def update(self) -> None:
        if self.__nameDialog != None:
            self.__nameDialog.update()

    def __CheckIfIsNotAFeldInstance(self, testObject:object) ->bool:
        return type(testObject) != Feld
    
    def handleLeftClickEvent(self, pos:tuple[int, int])->None:
        if self.__modusDialog != None and self.__modusDialog.getIfShown():
            self.__modusDialog.handleLeftClick(pos)
            return
        if self.__nameDialog != None and self.__nameDialog.getIfShown():
            self.__nameDialog.handleLeftClick(pos)
            return
        if self.__netzStatusDialog != None and self.__netzStatusDialog.getIfShown() and not(self.__netzVerbundenEvent.is_set()):
            self.__netzStatusDialog.handleLeftClick(pos)
            return

        if self.__resignDialog.getIfShown():
            self.__resignDialog.handleLeftClick(pos)
            return
        
        for pawnPromoteData in reversed(self.__PawnPromotes):
            PromoteDialog = pawnPromoteData["Dialog"]
            if type(PromoteDialog) != Dialog:
                continue
            if PromoteDialog.getIfShown():
                PromoteDialog.handleLeftClick(pos)
                return
        if not(self.__running):
            return

        if self.__netzAktiv and self.__onTurnTeam != self.__meinTeam:
            return
        
        clickedField = self.getFieldByCords(pos)
        if self.__CheckIfIsNotAFeldInstance(clickedField):
            return
        clickedFieldLabel = clickedField.getLabel()
        if self.__eventMode == "chooseFigure":
            self.__eventMode = "processing"
            self.__chooseFigureEvent(clickedField)
            self.__generateImage()
            return
        
        if self.__eventMode == "setFigure":
            self.__eventMode = "processing"
            self.__setFigureEvent(clickedField)
            self.__generateImage()
            return
        
        if self.__eventMode == "processing":
            print("Please slow down. I'm still Calculating! \n    You thing this is in an Error? Please communicate with us!")
            return
        print(f"Didn't found the Event for the current EventMode: {self.__eventMode}")

    def handleRightClickEvent(self, pos:tuple[int, int])->None:
        if not(self.__startKlar):
            return
        if not(self.__resignDialog.getIfShown()):
            self.__resignDialog.showSurface()
            self.__generateImage()

    def handleKeyDownEvent(self, event:pygame.event.Event)->None:
        if self.__nameDialog != None and self.__nameDialog.getIfShown():
            self.__nameDialog.handleKeyDown(event)

    def __resetCursorAndSetEventMode(self, eventMode:str):
        self.__cursor = None
        self.__eventMode = eventMode
    
    def __getMatchingTurnData(self, startField:Feld, targetField:Feld)->dict|None:
        FullTurnDataFromStartField:list[dict] = self.getPossibleTurnFieldsFullData(startField)
        for Data in FullTurnDataFromStartField:
            if Data["fieldLabel"] == targetField.getLabel():
                return Data
        return None

    def __setFigureEvent(self, clickedField:Feld)->None:
        self.__clearAllFieldHighlights()
        if self.__chooseFigureEvent(clickedField):
            return
        if self.__CheckIfIsNotAFeldInstance(self.__cursor):
            raise Exception("Cursor muss ein Feld sein")
        
        clickedFigure = clickedField.getFigure()
        

        matchingTurnData = self.__getMatchingTurnData(self.__cursor, clickedField)
        if matchingTurnData == None:
            self.__resetCursorAndSetEventMode("chooseFigure")
            self.__clearAllFieldHighlights()
            return
        
               
        beforeClickedFieldFigure = clickedField.getFigure()
        beforeCursorFigur = self.__cursor.getFigure()

        if matchingTurnData["needFigureOnField"] != None:
            if matchingTurnData["endPointNeededFigure"] != None:
                try:
                    needFigureField:Feld = self.__fields[matchingTurnData["needFigureOnField"]]
                    targetFigureField:Feld = self.__fields[matchingTurnData["endPointNeededFigure"]]
                except KeyError:
                    print("Oh, that should't happen. You need to restart the game. ERROR: MAJOR ERROR in Function Brett.__setFigureEvent - endPointNeededFigure/needFigureOnField")
                    return
                targetFigureField.setFigure(needFigureField.getFigure())
                needFigureField.setFigure(None)

        if matchingTurnData["onDoneTurnCall"] != None:
            matchingTurnData["onDoneTurnCall"](self.__turnNumber)

        if matchingTurnData["killMaybeFigureField"] != None:
            try:
                killMaybeFigureField:Feld = self.__fields[matchingTurnData["killMaybeFigureField"]]
            except KeyError:
                print("Oh, that should't happen. You need to restart the game. ERROR: MAJOR ERROR in Function Brett.__setFigureEvent - killMaybeFigureField")
                return
            killMaybeFigure = killMaybeFigureField.getFigure()
            if matchingTurnData["killMaybeFigureType"] == type(killMaybeFigure):
                    if type(killMaybeFigure) == Bauer:
                        if not(matchingTurnData["killMaybeFigureMustHadDoubleWalkLastTurn"]):
                            killMaybeFigureField.setFigure(None)
                        elif matchingTurnData["killMaybeFigureMustHadDoubleWalkLastTurn"] and killMaybeFigure.hasDidDoubleWalkInTurn(self.__turnNumber-1):
                            killMaybeFigureField.setFigure(None)

        startLabel = self.__cursor.getLabel()
        targetLabel = clickedField.getLabel()

        clickedField.setFigure(beforeCursorFigur)
        self.__cursor.setFigure(None)

        if clickedFigure != None:
            if clickedFigure.getTeam() == self.__onTurnTeam:
                self.__eventMode = "chooseFigure"
                self.__chooseFigureEvent(clickedField)
                return
            else:
                print("Es wird eine Figur geschlagen!")

        beforeCursorFigur.moved()
        self.__finishTurn()
        if self.__netzAktiv and not(self.__wendeRemoteZugAn):
            self.__sendeNetzMessage(f"MOVE;{startLabel};{targetLabel}")
    
    def __promoteTower(self):
        self.__doPromote(self.__whiteTower, self.__blackTower, "TURM")
    
    def __promoteBishop(self):
        self.__doPromote(self.__whiteBishop, self.__blackBishop, "LAEUFER")
    
    def __promoteKnight(self):
        self.__doPromote(self.__whiteKnight, self.__blackKnight, "SPRINGER")

    def __promoteQueen(self):
        self.__doPromote(self.__whiteQueen, self.__blackQueen, "DAME")

    def __doPromote(self, Team0Figure, Team1Figure, promotionName:str):
        promoteData = self.__PawnPromotes[-1]
        promoteField:Feld = self.__fields[promoteData["Label"]]
        promoteDialog:Dialog = promoteData["Dialog"]
        if promoteField.getFigure().getTeam() == 1:
            promoteField.setFigure(Team1Figure)
        elif promoteField.getFigure().getTeam() == 0:
            promoteField.setFigure(Team0Figure)
        promoteDialog.hideSurface()
        promoteDialog.kill()
        self.__PawnPromotes.pop(-1)
        if self.__netzAktiv and not(self.__wendeRemoteZugAn):
            self.__sendeNetzMessage(f"PROMO;{promoteField.getLabel()};{promotionName}")

    def __finishTurn(self):
        for row in [1, 8]:
            for field in self.getFieldRow(row):
                if type(field.getFigure()) == Bauer:
                    print("DETECT PROMOTE PAWN" + field.getLabel())
                    if self.__netzAktiv and self.__wendeRemoteZugAn:
                        continue
                    PromoteInfos = {}
                    PromoteInfos["Dialog"] = Dialog(
                        self.rect.width, self.rect.height, 
                        (self.rect.width//2, self.rect.height//2), 
                        "Zu was soll sich der Bauer auf " + field.getLabel() + "\n entwickeln Team:" + str(self.__onTurnTeam) + "?", self.rect.height//15, 
                        [
                            ["Turm!", self.__promoteTower],
                            ["Läufer!", self.__promoteBishop],
                            ["Springer!", self.__promoteKnight],
                            ["Dame!", self.__promoteQueen]
                            ], 
                        self.rect.height//18, 0.4, False, 
                        onVoidClick=self.__generateImage, 
                        posOffset=self.rect.topleft, 
                        onSurfaceChange=self.__generateImage
                    )
                    PromoteInfos["Group"] = pygame.sprite.GroupSingle()
                    PromoteInfos["Group"].add(PromoteInfos["Dialog"])
                    PromoteInfos["Label"] = field.getLabel()
                    self.__PawnPromotes.append(PromoteInfos)
                    self.__generateImage()
        self.__turnNumber += 1
        self.__switchToOtherPlayer()
        self.__eventMode = "chooseFigure"
        self.__clearAllFieldHighlights()
        matedTeams = self.checkIfMate()
        if matedTeams != [-1]:
            for field in self.__fields.values():
                if type(field) != Feld:
                    continue
                field.addFieldHighlight("GreenOutlineBox")
                field.addFieldHighlight("SmallGreenMiddleCircle")
            print("MATT: ", matedTeams)
        elif not(self.checkIfTeamCanMove(self.__onTurnTeam)):
            for field in self.__fields.values():
                if type(field) != Feld:
                    continue
                field.addFieldHighlight("GreenOutlineBox")
            print("Remis, durch keine Zugmöglichkeit mehr!")
    
    def checkIfTeamCanMove(self, team:int):
        for field in self.__fields.values():
            if type(field) != Feld:
                continue
            fieldFigure = field.getFigure()
            if fieldFigure == None:
                continue
            if fieldFigure.getTeam() == team:
                if len(self.getPossibleTurnFields(field)) != 0:
                    return True
        return False

    def checkIfMate(self)->list[int]:
        checkedTeams = self.__getCheckedTeams()
        if len(checkedTeams) == 0:
            return [-1]
        matedTeams = []
        for team in checkedTeams:
            if not(self.checkIfTeamCanMove(team)):
                matedTeams.append(team)
        if len(matedTeams) == 0:
            return [-1]
        for team in matedTeams:
            self.__running = False
        return matedTeams
    
    def __getKingFieldsInDanger(self)->list[Feld]:
        KingFields:list[Feld] = self.__getFieldsWithKings()
        checkedKings:list[int] = []
        for KingField in KingFields:
            if len(self.__getDangerFieldsToTheField(KingField)) != 0:
                checkedKings.append(KingField)
        return checkedKings 
    
    def __getCheckedTeams(self)->list[int]:
        KingFieldsInDanger:list[Feld] = self.__getKingFieldsInDanger()
        checkedTeams:list[int] = []
        for CheckedKingFeld in KingFieldsInDanger:
            King = CheckedKingFeld.getFigure()
            if type(King) == None:
                continue
            if King.getTeam() in checkedTeams:
                continue
            checkedTeams.append(King.getTeam())
        return checkedTeams 
    
    def __getDangerFieldsWhenMove(self, targetField:Feld, OriginField:Feld)->list[Feld]:
        resultingDangerFields:list[Feld] = [] 
        MovingFigure = OriginField.getFigure()
        if MovingFigure == None:
            raise Exception("There must be a Figure on OriginField!")
        
        targetFieldFigur = targetField.getFigure()

        OriginField = self.__fields[OriginField.getLabel()]
        targetField = self.__fields[targetField.getLabel()]

        OriginField.getFigure().moved()
        targetField.setFigure(MovingFigure)
        OriginField.setFigure(None)
        resultingDangerFields = self.__getDangerFieldsToTheField(targetField)
        targetField.setFigure(targetFieldFigur)
        OriginField.setFigure(MovingFigure)
        MovingFigure.undoMovedCounterByOne()

        return resultingDangerFields
    
    def __getDangerFieldsToTheField(self, testForField:Feld, TeamID:int|None = None)->list[Feld]:
        resultingDangerFields:list[Feld] = [] 
        FieldFigure = testForField.getFigure()
        if TeamID == None:
            if FieldFigure == None:
                FigureTeam = -1     # Damit getestet wird, ob es von beiden Teams geschlagen wird wenn keine Figur von einem Team draufsteht
            else:
                FigureTeam = FieldFigure.getTeam()
        else:
            FigureTeam = TeamID
        
        for field in self.__fields.values():
            if type(field) != Feld:
                continue

            figureOnField = field.getFigure()
            
            if figureOnField == None:
                continue

            if field == testForField:            # Das nach Bedrohung zu Kontrollierende Feld wird nicht durch sich selbst bedroht
                continue

            if not(figureOnField.getCanKillMates()) and figureOnField.getTeam() == FigureTeam:
                continue

            if testForField in self.getPossibleTurnFields(field, True, True, True):
                resultingDangerFields.append(field)
        return resultingDangerFields

    def __getFieldsWithKings(self)->list[Feld]:
        fieldsWithKings:list[Feld] = []
        for field in self.__fields.values():
            if type(field) != Feld:
                continue
            figure:None|Springer|Turm|Bauer|Laeufer|Dame|Koenig = field.getFigure()
            if figure == None:
                continue
            if figure.getKingRole():
                fieldsWithKings.append(field)
        return fieldsWithKings
    
    def __switchToOtherPlayer(self)->None:
        self.__onTurnTeam = (self.__onTurnTeam+1)%2

    def __chooseFigureEvent(self, clickedField:Feld)->bool:
        clickedFigure:None|Springer|Turm|Bauer|Laeufer|Dame|Koenig = clickedField.getFigure()
        clickedFieldLabel:str = clickedField.getLabel()
        if clickedFigure == None:
            self.__clearAllFieldHighlights() 
            self.__eventMode = "chooseFigure"
            return False
        # clickedFigure ist ab jetzt Aufjedenfall eine Figur

        if clickedFigure.getTeam() != self.__onTurnTeam:
            self.__eventMode = "chooseFigure"
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

    def getPossibleTurnFields(self, Field:Feld, ignoreChecksOrAnxiety:bool=False, ignoreBuildingChecks:bool=False, ignoreCastling:bool=False)->list[Feld]:        # Geht sicher, dass nicht doch irgendwie Ein Feld außerhalb des Brettes ist arbeitet noch Relative
        PossibleTurnFields = []
        relativePossibleTurnFields:list[dict] = self.getPossibleTurnFieldsFullData(Field, ignoreChecksOrAnxiety, ignoreBuildingChecks, ignoreCastling)
        for relativeField in relativePossibleTurnFields:
            try:
                field = self.__fields[relativeField["fieldLabel"]]
            except KeyError:
                continue
            if type(field) != Feld:
                continue
            PossibleTurnFields.append(field)
        return PossibleTurnFields

    def __markAllPosibleFields(self, FigureFieldLabel:str)->None:
        for field in self.getPossibleTurnFields(self.__fields[FigureFieldLabel]):
            if type(field) == Feld:
                field.addFieldHighlight("SmallGreenMiddleCircle")
            
    def __getOnlyPointsList(self,TurnsDatas:list[dict])->list[tuple]:
        PointsList:list = []                      #
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

    def getPossibleTurnFieldsFullData(self, startingPointField:Feld, ignoreChecksOrAnxiety:bool=False, ignoreBuildingChecks:bool=False, ignoreCastling:bool=False)->list[dict]:
        startFigure:None|Springer|Turm|Bauer|Laeufer|Dame|Koenig = startingPointField.getFigure()
        if startFigure == None:
            return []       # Ein Feld ohne Figur kann seine Figur nirgendwo hinsetzen
        
        startFieldLabel:str = startingPointField.getLabel()

        canJump:bool = startFigure.getCanJump()
        canKillMates:bool = startFigure.getCanKillMates()
        relativeMaybePossibleTurnsData:list[dict] = startFigure.getMaybePossibleTurns(startFieldLabel)                           # Diese sollten eig. nicht Links zu nicht existenten Feldern haben
        relativeMaybePossibleTurnsData:list[dict] = self.__getOnlyTurnDataWithValidFields(relativeMaybePossibleTurnsData)   # Das ist jetzt trotzdem nochmal Sichergestellt, wer weiß oder so...

        if not(canJump):
            relativeMaybePossibleTurnsData:list[dict] = self.__getTurnDataWithoutWalkThroughFigures(relativeMaybePossibleTurnsData, startingPointField)
        if not(canKillMates):
            relativeMaybePossibleTurnsData:list[dict] = self.__getTurnsNotKillingMatesFromTurnData(relativeMaybePossibleTurnsData, startFigure.getTeam())


        possibleRelativeFields:list[dict] = []                                                                                             
        for relativeMaybePossibleTurnData in relativeMaybePossibleTurnsData:                                                                        # Für jeden Punkt prüfen, welche der zusätzlichen Eigenschaften den Zuges erfüllt sein müssen um den Zug auszuführen und wenn diese nicht erfüllt ist ihn aussortieren
            if type(relativeMaybePossibleTurnData) != dict:
                raise Exception("Unexpectet Type error in Brett: Line 309")
            targetFieldOfTurn:Feld = self.__fields[relativeMaybePossibleTurnData["fieldLabel"]]
            if self.__CheckIfIsNotAFeldInstance(targetFieldOfTurn):
                    continue
            
            if relativeMaybePossibleTurnData["needFigureOnField"] != None:
                try:
                    FieldOfNeededFigure:Feld = self.__fields[relativeMaybePossibleTurnData["needFigureOnField"]]
                except KeyError:
                    # Wenn die Erwartete Figur auf einem Feld stehen soll, welches nicht existiert, ist davon auszugen das da keine steht, also kann der Zug nicht gemacht werden -> continue damit er nicht als zugmöglichkeit hinzugefügt wird.
                    continue


                NeededFigure:None|Springer|Turm|Bauer|Laeufer|Dame|Koenig = FieldOfNeededFigure.getFigure()
                if NeededFigure == None:
                    continue
                if relativeMaybePossibleTurnData["neededFigureType"] != None and relativeMaybePossibleTurnData["neededFigureType"] != type(NeededFigure):
                    continue
                if relativeMaybePossibleTurnData["allowNeededFigureHasTurned"] != None and not(relativeMaybePossibleTurnData["allowNeededFigureHasTurned"]) and NeededFigure.getHasMoved():
                    continue

            if relativeMaybePossibleTurnData["specialTurnType"] == "castling" and not(ignoreCastling):
                if not(self.__checkCastlingConditions(startingPointField, FieldOfNeededFigure)):
                    continue


            if targetFieldOfTurn.getFigure() == None and relativeMaybePossibleTurnData["onlyOnKill"]:
                if relativeMaybePossibleTurnData["killMaybeFigureField"] == None:
                    continue
                try:
                    killMaybeFigureField:Feld = self.__fields[relativeMaybePossibleTurnData["killMaybeFigureField"]]
                except KeyError:
                    # Wenn die Erwartete Figur auf einem Feld stehen soll, welches nicht existiert, ist davon auszugen das da keine steht, also kann der Zug nicht gemacht werden -> continue damit er nicht als zugmöglichkeit hinzugefügt wird.
                    raise Exception("Killmaybefigure Field couldn't be found!")
                killMaybeFigureFieldFigure = killMaybeFigureField.getFigure()
                if killMaybeFigureFieldFigure == None:
                    continue
                if relativeMaybePossibleTurnData["killMaybeFigureType"] != None and relativeMaybePossibleTurnData["killMaybeFigureType"] != type(killMaybeFigureFieldFigure):
                    continue
                if relativeMaybePossibleTurnData["killMaybeFigureMustHadDoubleWalkLastTurn"] and not(killMaybeFigureFieldFigure.hasDidDoubleWalkInTurn(self.__turnNumber-1)):
                    continue

            if targetFieldOfTurn.getFigure() != None and not(relativeMaybePossibleTurnData["canKill"]):
                continue

            if not(ignoreChecksOrAnxiety):
                if relativeMaybePossibleTurnData["hasAnxiety"]:
                    if len(self.__getDangerFieldsWhenMove(targetFieldOfTurn, startingPointField)) != 0:
                        continue

            if not(ignoreBuildingChecks):
                targetFigure = targetFieldOfTurn.getFigure()
                StartFeldLink = self.__fields[startingPointField.getLabel()]
                if type(StartFeldLink) == Feld:
                    skip = False
                    StartFeldLink.setFigure(None)
                    targetFieldOfTurn.setFigure(startFigure)
                    if startFigure.getTeam() in self.__getCheckedTeams():
                        skip = True
                    targetFieldOfTurn.setFigure(targetFigure)
                    StartFeldLink.setFigure(startFigure)
                    if skip:
                        continue
            possibleRelativeFields.append(relativeMaybePossibleTurnData)  
        return possibleRelativeFields
    
    def __getFieldLabelsPositionIDs(self, FieldLabel:str)->list[int, int]:
        return [ord(FieldLabel[0]), int(FieldLabel[1])]
    
    def __getLabelByPositionIDs(self, PositionIDs:list[int, int])->str:
        return chr(PositionIDs[0])+str(PositionIDs[1])

    def __getFieldsBetweenHorizontalVerticalOnly(self, startingField:Feld, targetField:Feld)->list[Feld]:
        resultFieldList:list[Feld] = []
        startFieldPositionIDs:list[int, int] = self.__getFieldLabelsPositionIDs(startingField.getLabel())
        targetFieldPositionIDs:list[int, int] = self.__getFieldLabelsPositionIDs(targetField.getLabel())

        if startFieldPositionIDs[0] == targetFieldPositionIDs[0] and startFieldPositionIDs[1] != targetFieldPositionIDs[1]:
            ChangingLineTypeIndex:int = 1
        elif startFieldPositionIDs[1] == targetFieldPositionIDs[1] and startFieldPositionIDs[0] != targetFieldPositionIDs[0]:
            ChangingLineTypeIndex:int = 0
        else:
            raise Exception("Error: Not a Horizontal")
        
        if startFieldPositionIDs[ChangingLineTypeIndex]>targetFieldPositionIDs[ChangingLineTypeIndex]:
            chacheToChangeField:list = targetFieldPositionIDs 
            targetFieldPositionIDs:list = startFieldPositionIDs
            startFieldPositionIDs:list = chacheToChangeField 


        currentTestingFieldPositionIDs:int = startFieldPositionIDs
        currentTestingFieldPositionIDs[ChangingLineTypeIndex] += 1
        while currentTestingFieldPositionIDs[ChangingLineTypeIndex] < targetFieldPositionIDs[ChangingLineTypeIndex]:
            testingField = self.__fields[self.__getLabelByPositionIDs(currentTestingFieldPositionIDs)]
            if type(testingField) != Feld:
                raise Exception("var: testingField has the wrong type!")
            resultFieldList.append(testingField)
            currentTestingFieldPositionIDs[ChangingLineTypeIndex] += 1
        return resultFieldList

    def __checkCastlingConditions(self, KingField:Feld, TargetField:Feld)->bool:
        FieldsBetween:list[Feld] = self.__getFieldsBetweenHorizontalVerticalOnly(KingField, TargetField)
        for Field in FieldsBetween:
            if Field.getFigure() != None:
                return False
        FieldsWithoutCheck:list[Feld] = FieldsBetween
        FieldsWithoutCheck.append(KingField)
        
        for Field in FieldsWithoutCheck:
            if len(self.__getDangerFieldsToTheField(Field, KingField.getFigure().getTeam())) != 0:
                return False
        return True

    def __getTurnDataWithoutWalkThroughFigures(self, relativeMaybePossibleTurnsData:list[dict], startField:Feld)->list|list[dict]:
        xLine:list = []
        yLine:list = []
        DiagonalXandY:list = []
        DiagonalXdiffY:list = []
        
        unsortet:list[tuple] = relativeMaybePossibleTurnsData.copy()
        for TurnData in relativeMaybePossibleTurnsData:
            # Vertikal -> (nur X ändert sich, Y = 0)
            if TurnData["point"][1] == 0:
                xLine.append(TurnData)
                unsortet.remove(TurnData)
                continue
            # Horizontal -> (nur Y ändert sich, X = 0)
            if TurnData["point"][0] == 0:
                yLine.append(TurnData)
                unsortet.remove(TurnData)
                continue
            # Diagonale -> (X und Y gleich)
            if TurnData["point"][1] == TurnData["point"][0]:
                DiagonalXandY.append(TurnData)
                unsortet.remove(TurnData)
                continue
            # Diagonale -> (X und Y entgegengesetzt)
            if TurnData["point"][1] == -TurnData["point"][0]:
                DiagonalXdiffY.append(TurnData)
                unsortet.remove(TurnData)
                continue
        
        if unsortet != []:
            raise Exception("Nicht unterstütztes Bewegungsraster, wenn canJump = False!")
        
        xLines:list[list[dict]]|list = self.__sortToDestination(xLine, 0)
        yLines:list[list[dict]]|list = self.__sortToDestination(yLine, 1)
        DiagonalXandY:list[list[dict]]|list = self.__sortToDestination(DiagonalXandY, 0)
        DiagonalXdiffY:list[list[dict]]|list = self.__sortToDestination(DiagonalXdiffY, 0)
        # Jetzt sind alle Listen nach Richtungen Sortiert und in der richtigen reinfolge um jetzt von Vorne bis nach hinten zu prüfen, ob was im Weg steht um dahin zu laufen 
        resultFields:list[dict] = []
        for lines in [xLines, yLines, DiagonalXandY, DiagonalXdiffY]:
            for line in lines:
                for resultRelative in self.__cutLineAtWalkingThroughFigures(line, startField):
                    resultFields.append(resultRelative)

        return resultFields
    
    def __cutLineAtWalkingThroughFigures(self, Line:list[dict], startField:Feld)->list[dict]|list:
        '''
        Vor.: 'Line' ist nach zunehmenden Abstand sortiert und geht entweder Wagerecht oder Horizontal
        Eff.: -
        Erg.: Eine Liste die nur noch die relativen beinhaltet die von dem startFeld aus, wenn man die Linie von links nach rechts durchläuft nicht durch eine andere Figur läuft, sondern diese schlagen würde.
        '''
        resultLine = []
        for relative in Line: # Für jedes Feld in der Liste in der bereits richtigen Reignfolge durchgehen und zum ergebniss hinzufügen, wenn etwas im Weg stegt, dann stoppen
            inspectField:Feld|None = self.__fields[relative["fieldLabel"]]
            if type(inspectField) != Feld:
                continue
            if inspectField.getFigure() != None:
                resultLine.append(relative)
                break
            resultLine.append(relative)
        return resultLine
    
    def __getPointFromDict(self, DataDict:dict)->tuple:
        return DataDict['point']
    
    def __sortToDestination(self, Line:list[dict], sortIndex:int)->list[list[dict]]:
        Line.sort(key=self.__getPointFromDict)
        Line = self.__SpitNegativePoints(Line, sortIndex)
        return self.__reverseFirstPart(Line)
    
    def __reverseFirstPart(self, Line:list)->list:
        firstPartLine = Line[0]
        if type(firstPartLine) == list:
            firstPartLine.reverse()
        return firstPartLine, Line[1]
    
    def __SpitNegativePoints(self, Line:list[dict], SplitNumberIndex:int)->list[list, list]:
        LinePositives = []
        LineNegatives = []

        for Element in Line:
            if Element['point'][SplitNumberIndex] < 0:
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
    TestBrettGroup.add(Spielbrett)

    
    while True:
        screen.fill("grey")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                continue
            if event.type == pygame.KEYDOWN:
                Spielbrett.handleKeyDownEvent(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    startClick = time()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if (time() - startClick) >= 5:
                         Spielbrett.handleRightClickEvent(pygame.mouse.get_pos())
                    else:
                        Spielbrett.handleLeftClickEvent(pygame.mouse.get_pos())
                elif event.button == 3:
                    Spielbrett.handleRightClickEvent(pygame.mouse.get_pos())
            
        TestBrettGroup.draw(screen)
        TestBrettGroup.update()
        pygame.display.update()
        clock.tick(60)
        #Spielbrett.setRotation(int(input()))
