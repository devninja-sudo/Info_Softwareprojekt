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
    '''
    Vor.: -edge_length- ist vom Typ Integer und beschreibt die Kantenlaenge des quadratischen Schachbretts in Pixeln. Der Wert muss groesser als 0 sein.
          -topLeftCorner- ist ein Tupel aus zwei Integern und beschreibt die linke obere Ecke des Brettes in Pixelkoordinaten.
          -field_color1- ist vom Typ String und beschreibt die Farbe des ersten Feldmusters.
          -field_color2- ist vom Typ String und beschreibt die Farbe des zweiten Feldmusters.
          -rotation- ist vom Typ Integer und beschreibt die Rotation des Brettes in Grad. Sinnvolle Werte sind Vielfache von 90.
    Eff.: Das Brett, die Felder, die Startdialoge und alle Spiel-/Netzwerk-Zustandsvariablen sind initialisiert.
    Erg.: Eine Brettinstanz ist geliefert, welche -pygame.sprite.Sprite- geerbt hat und fuer den Spielstart vorbereitet ist.
    '''
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
        '''
        Vor.: -
        Eff.: Alle Statusvariablen für Züge sind initialisiert. 
            Die Variablen: self.__onTurnTeam:int, self.__cursor, self.__turnNumber:int, self.__eventMode:str, self.__PawnPromotes:list und self.__running:bool sind eventuell beeinflusst worden. 
        Erg.: -
        '''
        self.__onTurnTeam:int = 0 
        self.__cursor = None
        self.__eventMode:str|None = None 
        self.__running:bool = False
        self.__turnNumber:int = 0
        self.__PawnPromotes:list = []

    def __setupNetzwerkVars(self):
        '''
        Vor.: -
        Eff.: Alle Netzwerk relevaten Variablen sind initialisiert.
        Erg.: -
        '''
        self.__ready:bool = False
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
        self.__ipDialog:TextInputDialog|None = None
        self.__netzStatusDialog:Dialog|None = None
        self.__startDialogGruppe = pygame.sprite.Group()

    def __setupStartDialogs(self):
        '''
        Vor.: Das Brett und die Dialoge sind initialisiert.
        Eff.: Der Startmodus-Dialog ist erstellt und angezeigt. 
            Inform einer weißen Box, welche sich ueber das Schachbrett streckt und die Ueberschrift "Spielmodus wählen" traegt.
            Mit den Unterueberschriften "Spiel an einem Rechner" und "Spiel über Netzwerk", welche Interaktionsmoeglichkeiten darstellen im Bezug zur Ueberschrift.
        Erg.: -
        '''
        self.__startDialogGruppe.empty()
        self.__modusDialog = Dialog(
            self.rect.width, self.rect.height,
            (self.rect.width//2, self.rect.height//2),
            "Spielmodus wählen", self.rect.height//10,
            [
                ["Spiel an einem Rechner", self.__waehleSingleplayer],
                ["Spiel über Netzwerk", self.__zeigeNameDialog]
            ],
            self.rect.height//8, 0.42, False,
            onVoidClick=self.__generateImage,
            posOffset=self.rect.topleft,
            onSurfaceChange=self.__generateImage
        )
        self.__startDialogGruppe.add(self.__modusDialog)
        self.__generateImage()

    def __zeigeNameDialog(self):
        '''
        Vor.: Die Startdialoggruppe ist initialisiert.
        Eff.: Der Dialog zur Namenseingabe ist erstellt und aktiv gesetzt.
            Inform einer weißen Box, welche sich ueber das Schachbrett streckt und die Ueberschrift "Name eingeben" traegt.
            Mit den Unterueberschriften "Weiter", welche Interaktionsmoeglichkeiten darstellen im Bezug zur Ueberschrift.
            Texteingaben sind in einem Eingabeberreich dargestellt.
        Erg.: -
        '''
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
        '''
        Vor.: -headline- ist ein String und beschreibt die anzuzeigende Ueberschrift.
        Eff.: Der Dialog zur Netzwerkinit und Suche ist erstellt und angezeigt.
            Inform einer weißen Box, welche sich ueber das Schachbrett streckt und die Ueberschrift -headline- mittig traegt.
            Mit den Unterueberschriften "Erneut suchen", welche eine Interaktionsmoeglichkeit darstellen im Bezug zur Ueberschrift.
        Erg.: -
        '''
        self.__netzStatusDialog = Dialog(
            self.rect.width, self.rect.height,
            (self.rect.width//2, self.rect.height//2),
            headline, self.rect.height//14,
            [["Erneut suchen", self.__starteNetzSuche], ["IP eingeben", self.__zeigeIpDialog]],
            self.rect.height//10, 0.7, False,
            onVoidClick=self.__generateImage,
            posOffset=self.rect.topleft,
            onSurfaceChange=self.__generateImage
        )
        self.__startDialogGruppe.empty()
        self.__startDialogGruppe.add(self.__netzStatusDialog)
        self.__generateImage()

    def __zeigeIpDialog(self):
        self.__ipDialog = TextInputDialog(
            self.rect.width, self.rect.height,
            (self.rect.width//2, self.rect.height//2),
            "IP eingeben", self.rect.height//10,
            self.rect.height//10,
            "Verbinden", self.rect.height//10,
            False,
            onSubmit=self.__verbindeMitIpText,
            onVoidClick=self.__generateImage,
            posOffset=self.rect.topleft,
            onSurfaceChange=self.__generateImage,
            maxInputLength=15
        )
        self.__startDialogGruppe.empty()
        self.__startDialogGruppe.add(self.__ipDialog)
        self.__generateImage()

    def __istIPv4Gueltig(self, ipText:str)->bool:
        teile = ipText.split(".")
        if len(teile) != 4:
            return False
        for teil in teile:
            if teil == "":
                return False
            if not(teil.isdigit()):
                return False
            wert = int(teil)
            if wert < 0 or wert > 255:
                return False
        return True

    def __verbindeMitIpText(self, ipText:str):
        ipText = ipText.strip()
        if not(self.__istIPv4Gueltig(ipText)):
            if self.__ipDialog != None:
                self.__ipDialog.setHeadline("IP ungueltig")
            return
        if self.__netzVerbundenEvent.is_set():
            return
        connectThread = threading.Thread(target=self.__direktConnectWorker, args=(ipText,), daemon=True)
        connectThread.start()

    def __direktConnectWorker(self, targetIp:str):
        self.__zeigeNetzStatusDialog("Verbinde mit " + targetIp)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex((targetIp, self.__netzPort)) != 0:
            sock.close()
            self.__zeigeNetzStatusDialog("IP nicht erreichbar")
            return
        sock.sendall(("ASK;" + self.__spielerName + "\n").encode("utf-8"))
        raw = sock.recv(2048)
        if len(raw) == 0:
            sock.close()
            self.__zeigeNetzStatusDialog("Keine Antwort von IP")
            return
        responseText = raw.decode("utf-8").strip()
        if responseText.startswith("OK;"):
            self.__setzeNetzSocket(sock, 0)
            return
        sock.close()
        self.__zeigeNetzStatusDialog("Handshake fehlgeschlagen")

    def __waehleSingleplayer(self):
        '''
        Vor.: -
        Eff.: Der Einzelspielermodus ist gesetzt und das Spiel gestartet.
        Erg.: -
        '''
        self.__netzAktiv = False
        if self.__modusDialog != None:
            self.__modusDialog.hideSurface()
        self.__startDialogGruppe.empty()
        self.__ready = True
        self.start()
        self.__generateImage()

    def __uebernehmeSpielerName(self, playerName:str):
        '''
        Vor.: -playerName- ist vom Typ String.
        Eff.: Der Spielername ist überprueft und bei Gueltigkeit uebernommen. Bei ungueltigkeit ist die Dialogueberschrift nun "Name darf nicht leer sein" .
        Erg.: -
        '''
        playerName = playerName.strip()
        if playerName == "":
            if self.__nameDialog != None:
                self.__nameDialog.setHeadline("Name darf nicht leer sein")
            return
        self.__spielerName = playerName
        self.__starteMultiplayer()

    def __starteMultiplayer(self):
        '''
        Vor.: Ein gueltiger Spielername ist gesetzt.
        Eff.: Multiplayer ist aktiviert, Listener gestartet und Suche wird gestartet.
            Mittels einen bereits in der optik Beschriebenden Dialogfensters ist der Suchstatus mittels der Ueberschrift "Suche im  Netzwerk nach Spiel" abzulesen.
        Erg.: -
        '''
        self.__netzAktiv = True
        print("Netzwerkstart auf Host:", socket.gethostname(), "IP:", self.__holeLokaleIp())
        self.__zeigeNetzStatusDialog("Suche im  Netzwerk nach Spiel")
        if self.__netzListenerThread == None or not(self.__netzListenerThread.is_alive()):
            self.__netzListenerThread = threading.Thread(target=self.__listenerWorker, daemon=True)
            self.__netzListenerThread.start()
        self.__starteNetzSuche()

    def __starteNetzSuche(self):
        '''
        Vor.: -
        Eff.: Ein Suchthread ist gestartet, falls dieser nicht bereits läuft.
        Erg.: -
        '''
        if self.__netzVerbundenEvent.is_set():
            return
        self.__zeigeNetzStatusDialog("Suche im  Netzwerk nach Spiel")
        self.__netzSucheThread = threading.Thread(target=self.__discoveryWorker, daemon=True)
        self.__netzSucheThread.start()

    def __holeLokaleIp(self)->str:
        '''
        Vor.: -
        Eff.: -
        Erg.: Die lokale IP ist als String geliefert.
        '''
        allIps = socket.gethostbyname_ex(socket.gethostname())[2]
        for ip in allIps:
            if not(ip.startswith("127.")):
                return ip
        if len(allIps) != 0:
            return allIps[0]
        return "127.0.0.1"

    def __listenerWorker(self):
        '''
        Vor.: Netzwerkmodus ist aktiv und der definierte Port ist gueltig und ohne Netzwerkeinschraenkungen nutzbar.
        Eff.: Wartet auf eingehende Partieanfrgen und beantwortet den "Handshake".
        Erg.: -
        '''
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("0.0.0.0", self.__netzPort))
        listener.listen(3)
        print("Listener aktiv auf Port", self.__netzPort)
        while self.__netzAktiv and not(self.__netzVerbundenEvent.is_set()):
            conn, _addr = listener.accept()
            print("Eingehende Verbindung von", _addr)
            raw = conn.recv(2048)
            if len(raw) == 0:
                conn.close()
                continue
            msgText = raw.decode("utf-8").strip()
            print("Empfangen:", msgText)
            msgParts = msgText.split(";")
            if len(msgParts) < 2 or msgParts[0] != "ASK":
                conn.close()
                continue
            if self.__netzVerbundenEvent.is_set():
                conn.sendall("BUSY\n".encode("utf-8"))
                conn.close()
                continue
            conn.sendall(("OK;" + self.__spielerName + "\n").encode("utf-8"))
            print("Antwort gesendet: OK;" + self.__spielerName)
            self.__setzeNetzSocket(conn, 1)
            return

    def __discoveryWorker(self):
        '''
        Vor.: Netzwerkmodus ist aktiv.
        Eff.: Sucht im lokalen Netz nach Gegenstellen und fuehrt ggf. Handshake aus. Bei Fehlern ist der Fehler im Dialogfenster "LAN-Suche fehlgeschlagen" oder "Kein Spiel gefunden, warte auf Anfrage" ablesbar.
        Erg.: -
        '''
        localIp = self.__holeLokaleIp()
        chunks = localIp.split(".")
        if len(chunks) != 4:
            self.__zeigeNetzStatusDialog("LAN-Suche fehlgeschlagen")
            return
        prefix = f"{chunks[0]}.{chunks[1]}.{chunks[2]}"
        own = int(chunks[3])
        print("Starte Suche in", prefix + ".1-254", "eigene IP-Endung:", own)
        for host in range(1, 255):
            if not(self.__netzAktiv) or self.__netzVerbundenEvent.is_set():
                return
            if host == own:
                continue
            target = f"{prefix}.{host}"
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if sock.connect_ex((target, self.__netzPort)) != 0:
                sock.close()
                continue
            print("Port offen auf", target)
            sock.sendall(("ASK;" + self.__spielerName + "\n").encode("utf-8"))
            print("Gesendet an", target, ": ASK;" + self.__spielerName)
            raw = sock.recv(2048)
            if len(raw) == 0:
                sock.close()
                continue
            responseText = raw.decode("utf-8").strip()
            print("Antwort von", target, ":", responseText)
            if responseText.startswith("OK;"):
                self.__setzeNetzSocket(sock, 0)
                return
            sock.close()
        if not(self.__netzVerbundenEvent.is_set()):
            print("Suche fertig, kein Spiel gefunden")
            self.__zeigeNetzStatusDialog("Kein Spiel gefunden, warte auf Anfrage")

    def __setzeNetzSocket(self, sock:socket.socket, localTeam:int):
        '''
        Vor.: -sock- ist ein offener Socket, -localTeam- ist eine Team-ID.
        Eff.: Uebernimmt die Verbindung, setzt Team/Zustand und startet Empfang. Das Brett ist gestartet und auf dem Brett -image- gezeichnet, 
            wenn kein Element sich ueber dem Brett befindet ist es im Fenster sichtbar.
        Erg.: -
        '''
        if self.__netzVerbundenEvent.is_set():
            sock.close()
            return
        self.__netzSock = sock
        self.__meinTeam = localTeam
        self.__netzVerbundenEvent.set()
        print("Verbindung hergestellt. Eigenes Team:", localTeam)
        if self.__modusDialog != None:
            self.__modusDialog.hideSurface()
        if self.__nameDialog != None:
            self.__nameDialog.hideSurface()
        if self.__ipDialog != None:
            self.__ipDialog.hideSurface()
        if self.__netzStatusDialog != None:
            self.__netzStatusDialog.hideSurface()
        self.__startDialogGruppe.empty()
        self.__ready = True
        self.start()
        self.__starteNetzEmpfang()
        self.__generateImage()

    def __starteNetzEmpfang(self):
        '''
        Vor.: Eine Netzwerkverbindung ist aufgebaut.
        Eff.: Teil des Netzwerk-Multitrheadings, startet falls dieser nicht existiert den Empfangs-Thread.
        Erg.: -
        '''
        if self.__netzEmpfangThread != None and self.__netzEmpfangThread.is_alive():
            return
        self.__netzEmpfangThread = threading.Thread(target=self.__receiverWorker, daemon=True)
        self.__netzEmpfangThread.start()

    def __receiverWorker(self):
        '''
        Vor.: Netzwerkmodus aktiv und Verbindung gesetzt.
        Eff.: Verantwortlich fuer den Empfang von Nachrichten, liest Zeilen und verarbreitet Zuege, dass heißt die Nachricht hat ggf. einen Zugumgesetzt.
        Erg.: -
        '''
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
        '''
        Vor.: -text- ist eine  Nachrichtenzeile ohne Zeilenumbrüche.
        Eff.: Sendet die Nachricht an den verbundenen Rechner, falls die Verbindung aktiv ist.
        Erg.: -
        '''
        if not(self.__netzAktiv) or not(self.__netzVerbundenEvent.is_set()):
            return
        if self.__netzSock == None:
            return
        self.__netzSock.sendall((text + "\n").encode("utf-8"))

    def __setzeRemoteZug(self, startLabel:str, targetLabel:str):
        '''
        Vor.: -startLabel- und -targetLabel- sind gueltige Feldbezeichnungen.
        Eff.: Der Zug welcher ensteht, wenn das Feld mit der Bezeichnung -startLabel- und dann dem Feld mit der Bezeichnung -targetLabel- anklickt und das Brett fuer das Team gerade Bewegungsaufforderungen annimmt ist umgesetzt.
            Auch ist das Brett -image- aktualisiert.
        Erg.: -
        '''
        startPos = self.__getClickPosByLabel(startLabel)
        targetPos = self.__getClickPosByLabel(targetLabel)
        if startPos == None or targetPos == None:
            return
        self.__wendeRemoteZugAn = True
        if self.__resignDialog.getIfShown():
            self.__resignDialog.hideSurface()
        self.handleLeftClickEvent(startPos)
        self.handleLeftClickEvent(targetPos)
        self.__wendeRemoteZugAn = False
        self.__generateImage()

    def __getClickPosByLabel(self, fieldLabel:str)->tuple[int, int]|None:
        '''
        Vor.: -fieldLabel- ist eine gueltige Feldbezeichnungen. Brett ist ohne zusaetzliche Verschiebung durch nachtraegliche Einwirkung auf dem Bildschirm abgebildet.
        Eff.: -
        Erg.: Die Mittelpunktkordinate des Feldes auf dem Bildschirm ist als tuple geliefert, wobei der erste Wert fuer die X-Kordinate steht und die zweite fuer die Y-Kordinate. 
        '''
        field = self.__fields.get(fieldLabel)
        if type(field) != Feld:
            return None
        fieldRect = field.getRect()
        return (int(self.rect.x + fieldRect.centerx), int(self.rect.y + fieldRect.centery))

    def __setzeRemotePromo(self, fieldLabel:str, pieceName:str):
        '''
        Vor.: -fieldLabel- ist eine gueltige Feldbezeichnung, -pieceName- ein bekannter Figurtyp.
        Eff.: Eine empfangene Bauernumwandlung auf dem angegebenen Feld ist ausgefuert und das Brett -image- ist aktualiesiert.
        Erg.: -
        '''
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
        '''
        Vor.: -
        Eff.: Der Spielzustand ist zurueck gesetzt und eine neue Partie gestartet.
        Erg.: -
        '''
        self.__reset_game_state()
        if self.__netzAktiv:
            self.__ready = True
        self.start()
    
    def getFieldRow(self, RowNumber:int)->list[Feld]:
        '''
        Vor.: -RowNumber- ist eine gueltige Reihen-ID des Brettes.
        Eff.: -
        Erg.: Eine Liste mit allen Feldern der angegebenen Reihe ist geliefert.
        '''
        RowFields = []
        for i in range(self.__fields_count):
            letter = chr(ord(self.__field_label_start_letter)+i)
            RowFields.append(self.__fields[letter+str(RowNumber)])
        return RowFields
    
    def setupDialogGroup(self):
        '''
        Vor.: -
        Eff.: Ein Dialog fuer Aktionen zum Aufgeben/beenden das Spiels in der Variable -self.__resignDialog- ist erstellt und ist der Spritegruppe in der Variable -self.__DialogGroup- hinzugefuegt.
        Erg.: -
        '''
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
        '''
        Vor.: -
        Eff.: Figuren/Feldgruppen sind geleert und die Felder neuinitialisiert.
            Das hat meistens Auswirkungen auf das Brett -image- haben kann, weil die dort evtl. befundenen Elemente/Effekte nun nicht mehr dargestellt sind.
        Erg.: -
        '''
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
        '''
        Vor.: Das Brett ist bereit zum Starten.
        Eff.: das Spiel ist auf aktiv und die Variable -self.__eventMode- ist in den Auswahlmodus gesetzt.
        Erg.: -
        '''
        if self.__running:
            raise Exception("Bereits gestartet!")
        if not(self.__ready):
            return
        self.__running = True
        self.__eventMode = "chooseFigure"

    def __setupBrett(self)->None:
        '''
        Vor.: Das Feldraster ist initialisiert.
        Eff.: Figureninstanzen (self.__blackTower, self.__whiteTower, self.__blackQueen, self.__whiteQueen, self.__blackKnight, self.__whiteKnight, self.__blackBishop, self.__whiteBishop, self.__blackKing, self.__whiteKing) 
            sind beschrieben und die Startaufstellung ist gesetzt.
        Erg.: -
        '''
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
        self.__whiteKing = Koenig("assets/graphics/w_koenig.png", self.__field_length*self.__FigureScale, self.__field_length, self.__fields_count, self.__field_label_start_letter, 0)
        
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
        '''
        Vor.: Parameter beschreiben eine gueltige Reihe und Figurenkonfiguration.
        Eff.: Die angegebene Reihe, mit Bauern des Teams mit der -teamID-, ist in den Datensaetzen befuellt. Das Brett -self.image- ist nicht aktualisiert.
        Erg.: -
        '''
        for i in range(self.__fields_count):
            fieldLabelLetter:str = chr(ord(self.__field_label_start_letter)+i)
            fieldLabel:str = fieldLabelLetter + str(RowNumber)
            targetField:Feld = self.__fields[fieldLabel]
            targetField.setFigure(Bauer(texturePath, self.__field_length*scale, self.__field_length, self.__fields_count, self.__field_label_start_letter, teamID))

    def setRotation(self, rotation:int)->None:
        '''
        Vor.: -rotation- ist ein Vielfaches von 90 Grad oder 0 und Feldobjekte sind bereits vorhanden.
        Eff.: Die Brettrotation ist auf -rotation- gesetzt und Feldpositionen sind korriegiert und nun ist das Brett mit der angegebenden Rotation in -self.image- beschrieben.
        Erg.: -
        '''
        if rotation % 90 != 0:
            raise Exception("Rotation not available!")
        self.__rotation:int = rotation
        self.__correctFieldPositions()

    def getRotation(self)->int:
        '''
        Vor.: -
        Eff.: -
        Erg.: Die aktuelle Brettrotation in Grad ist geliefert.
        '''
        return self.__rotation
    
    def __correctFieldPositions(self)->None:
        '''
        Vor.: Feldobjekte sind vorhanden.
        Eff.: Berechnet und setzt die aktuelle Position aller Felder neu. Das Brett -self.image- ist nun neugeneriert.
        Erg.: -
        '''
        for key in self.__fields.keys():
            currentField:Feld = self.__fields[key]
            currentField.setFieldPosition(self.__getFieldPositionByName(key))
        self.__generateImage()

    def __createFields(self)->dict:
        '''
        Vor.: Brettparameter sind gesetzt.
        Eff.: Die Feldobjekte sind erstellt.
        Erg.: Ein Dictionary mit Feldlabeln als Keys und Feldobjekten als Werten ist geliefert.
        '''
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
        '''
        Vor.: -field_name- ist eine gültige Feldbezeichnung.
        Eff.: -
        Erg.: Die Feldposition innerhalb des Brettbildes ist als Tupel (x, y) ist geliefert.
        '''
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
        '''
        Vor.: -point- ist eine Koordinate als Tuple (x, y) im Brettsystem.
        Eff.: -
        Erg.: Die Koordinate, welche die Position beschreibt, wenn das Brett um 90 Grad gedreht ist, ist geliefert.
        '''
        return (self.__edge_length-point[1]-self.__field_length, point[0])
    
    def __getFieldsGroup(self)->pygame.sprite.Group:
        '''
        Vor.: -
        Eff.: -
        Erg.: Die Sprite-Gruppe der Felder ist geliefert (-self.__fieldsGroup-).
        '''
        return self.__fieldsGroup
    
    def __createFieldsGroup(self)->pygame.sprite.Group:
        '''
        Vor.: Feldobjekte sind korrekt erstellt. self.__fields sind allle Werte Sprites. 
        Eff.: -
        Erg.: Eine erzeugte Sprite.Group mit allen Sprites aus dem Werten von -self.__fields- ist geliefert.
        '''
        fieldsGroup = pygame.sprite.Group()
        
        for key in self.__fields.keys():
            field = self.__fields[key]
            fieldsGroup.add(field)

        return fieldsGroup

    def __generateImage(self) -> None:
        '''
        Vor.: Brettoberflaeche und Zeichenobjekte sind initialisiert.
        Eff.: Momentan sichtbare Felder und sichtbare Dialoge auf der Brettoberflaeche sind in -self.image- als Surface beschrieben.
        Erg.: -
        '''
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
        '''
        Vor.: -self.__nameDialog- ist None oder eine TextDialoginstanz.
        Eff.: Wenn -self.__nameDialog- nicht None entspricht ist der TextDialog -self.__nameDialog- aktualisiert.
        Erg.: -
        '''
        if self.__nameDialog != None:
            self.__nameDialog.update()
        if self.__ipDialog != None:
            self.__ipDialog.update()

    def __CheckIfIsNotAFeldInstance(self, testObject:object) ->bool:
        '''
        Vor.: -testObject- ist ein beliebiges Objekt.
        Eff.: -
        Erg.: falls -testObject- kein Feld ist -True- geliefert, sonst ist -False- geliefert.
        '''
        return type(testObject) != Feld
    
    def handleLeftClickEvent(self, pos:tuple[int, int])->None:
        '''
        Vor.: -pos- ist eine gueltige Mausposition in Pixeln und das Brett ist auf dem Screen ohne zusaetzliche Verschiebungen ausgegeben.
        Eff.: Ein Klick an der Position -pos- ist als Linksklick verarbeitet, dadurch konnten Figuren fuer ein Zug gesetzt, ausgewehlt werden, mit einen Dialogfenster interagiert werden oder auch ein Hinweis ausgeben werden, alls das ist ggf. abhaengig von -self.__eventMode- 
            self.image ist aktualiesiert.
        Erg.: -
        '''
        if self.__modusDialog != None and self.__modusDialog.getIfShown() and self.__modusDialog in self.__startDialogGruppe:
            self.__modusDialog.handleLeftClick(pos)
            return
        if self.__nameDialog != None and self.__nameDialog.getIfShown() and self.__nameDialog in self.__startDialogGruppe:
            self.__nameDialog.handleLeftClick(pos)
            return
        if self.__ipDialog != None and self.__ipDialog.getIfShown() and self.__ipDialog in self.__startDialogGruppe:
            self.__ipDialog.handleLeftClick(pos)
            return
        if self.__netzStatusDialog != None and self.__netzStatusDialog.getIfShown() and self.__netzStatusDialog in self.__startDialogGruppe and not(self.__netzVerbundenEvent.is_set()):
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

        if self.__netzAktiv and self.__onTurnTeam != self.__meinTeam and not(self.__wendeRemoteZugAn):
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
        '''
        Vor.: -pos- ist eine gueltige Mausposition in Pixeln.
        Eff.: Oeffnet den Ingame-Dialog. Die Brett.image Surface ist aktualiesiert.
        Erg.: -
        '''
        if not(self.__ready):
            return
        if not(self.__resignDialog.getIfShown()):
            self.__resignDialog.showSurface()
            self.__generateImage()

    def handleKeyDownEvent(self, event:pygame.event.Event)->None:
        '''
        Vor.: -event- ist ein gueltiges pygame KEYDOWN-Event.
        Eff.: Die Tastatureingaben ist an den Nameneingabedialog weitergeleitet, wenn dieser geofnet ist. Damit der Buchstabe korrekt in der Namenseingabe beim Nameneingabefeld angezeigt werden kann.
        Erg.: -
        '''
        if self.__nameDialog != None and self.__nameDialog.getIfShown():
            self.__nameDialog.handleKeyDown(event)
        if self.__ipDialog != None and self.__ipDialog.getIfShown():
            self.__ipDialog.handleKeyDown(event)

    def __resetCursorAndSetEventMode(self, eventMode:str):
        '''
        Vor.: -eventMode- ist ein gueltiger Eventmodus.
        Eff.: der Cursor (self.__cursor) ist zurueck gesetzt und setzt den uebergebenen Eventmodus fuer Eingaben um an der Variable (self.__eventMode).
        Erg.: -
        '''
        self.__cursor = None
        self.__eventMode = eventMode
    
    def __getMatchingTurnData(self, startField:Feld, targetField:Feld)->dict|None:
        '''
        Vor.: -startField- und -targetField- sind gueltige Felder.
        Eff.: -
        Erg.: Das passende ZugdatenDictionary oder -None- ist geliefert.
            Das evtl. gelieferte passende ZugdatenDictionary besteht aus:
                "" steht fuer den Key und das hinter dem = fuer die Erklaerung des Values
                "point" = :tuple[int, int] (gueltige Feldbezeichnung, die relativ zu -originFieldLabel- die Anzahl der Felder angibt, die fuer einen Zug in Buchstaben und Zahlen Richtung noetig sind)
                "fieldLabel" = :str eine gueltige Feldbezeichnung (das erste Zeichen ist ein Buchstabe im Berreich des Buchstaben der Anfangsbeschriftungs und dem Buchstaben der Anfangsbeschriftungs versetzt um die Feldanzahl / das zweite Zeichen ist eine Zahl im Berreich der Zahl der Anfangsbeschriftungs und der Zahl der Anfangsbeschriftungs versetzt um die Feldanzahl) zu dem sich die Figur bewegen soll.
                "onlyOnKill" = :bool (-True-, wenn die Figur nur den Zug machen kann, wenn sie dabei eine andere Figur schlagen wuerde)
                "canKill" = :bool (-True-, wenn die Figur beim Zug auf das Zielfeld eine andere Figur schlagen koennte)
                "killMaybeFigureType" =  (Klasse der Figur, die geschlagen werden kann)
                "killMaybeFigureField" = :str (Feldbezeichnung des Feldes, auf dem eine Figur geschlagen werden kann)
                "killMaybeFigureMustHadDoubleWalkLastTurn" = :bool (beschreibt, ob die Figur, die geschlagen werden kann, im letzten Zug einen Doppelzug gemacht hat)
                "hasAnxiety" = :boool oder immer True, wenn die Figur die Koenigsrolle traegt (beschreibt, ob die Figur auf dem Zeilfeld des Zuges geschlagen werden koennte)
                "specialTurnType" = :str (spezielle Zugbezeichnung)
                "needFigureOnField" = :str (Zug ist nur moeglich, wenn auf dem Feld eine Figur steht und ein anderes Feld angegeben ist)
                "neededFigureType" =  (ueberprueft, ob der Zug einer bestimmten hier angegebender Figur als Figurklasse mit der Figur auf dem Feld uebereinstimmt)
                "allowNeededFigureHasTurned" = :bool (beschreibt, ob sie die Figur auf dem Feld -needFigureOnField- schon bewegt hat)
                "endPointNeededFigure" = :str (Feldbezeichnung, auf dem die Firgur nach dem Zug steht)
                "onDoneTurnCall" = :Callable (beschreibt die Methode/Funktion, die nach dem Zug ausgefuerht wird)
        '''
        FullTurnDataFromStartField:list[dict] = self.getPossibleTurnFieldsFullData(startField)
        for Data in FullTurnDataFromStartField:
            if Data["fieldLabel"] == targetField.getLabel():
                return Data
        return None

    def __setFigureEvent(self, clickedField:Feld)->None:
        '''
        Vor.: -clickedField- ist ein gueltiges Feldobjekt.
        Eff.: Das setzen eines Zuges ist ausgefuehrt, wenn das -clickedField- ein gueltiger Zug, fuer die Figur des auf dem Feld, welches in -self.__cursor- gespeichert, ist. 
            Wenn sich das Brett im Netzwerkbetrieb befindet ist die Bewegung an den anderen Rechner weitergeleitet.
            Nach dem Zug ist der self.__eventMode zu "chooseFigure" geändert und der andere Spieler ist an der Reihe, außer das Spiel ist durch den Zug beendent, weil ein Patt oder ein Matt ausgeloest wurde.
            In diesem Fall ist die Situation in der Konsole beschrieben und beim Matt sind alle Felder einzeln umrandet und mit einem gruenen Punkt versehen.
            Bei einer Pattsituation sind nur alle Felder, jeweils grün eingeramt.
            Auch ist, dann das Brett.image aktualiesiert.
        Erg.: -
        '''
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
        '''
        Vor.: Ein Bauer steht zur Umwandlung bereit.
        Eff.: Der Bauer, welcher in der Liste der zu Umwandelbarenbauern hinten steht ist in einen Turm, des seines gleichen Teams, umgewandelt.
                Und der andere Spieler ist an der Reihe.
        Erg.: -
        '''
        self.__doPromote(self.__whiteTower, self.__blackTower, "TURM")
    
    def __promoteBishop(self):
        '''
        Vor.: Ein Bauer steht zur Umwandlung bereit.
        Eff.: Der Bauer, welcher in der Liste der zu Umwandelbarenbauern hinten steht ist in einen Laeufer, des seines gleichen Teams, umgewandelt.
                Und der andere Spieler ist an der Reihe. Das -image- ist aktualiesiert.
        Erg.: -
        '''
        self.__doPromote(self.__whiteBishop, self.__blackBishop, "LAEUFER")
    
    def __promoteKnight(self):
        '''
        Vor.: Ein Bauer steht zur Umwandlung bereit.
        Eff.: Der Bauer, welcher in der Liste der zu Umwandelbarenbauern hinten steht ist in einen Springer, des seines gleichen Teams, umgewandelt.
                Und der andere Spieler ist an der Reihe. Das -image- ist aktualiesiert.
        Erg.: -
        '''
        self.__doPromote(self.__whiteKnight, self.__blackKnight, "SPRINGER")

    def __promoteQueen(self):
        '''
        Vor.: Ein Bauer steht zur Umwandlung bereit.
        Eff.: Der Bauer, welcher in der Liste der zu Umwandelbarenbauern hinten steht ist in einen Dame, des seines gleichen Teams, umgewandelt.
                Und der andere Spieler ist an der Reihe. Das -image- ist aktualiesiert.
        Erg.: -
        '''
        self.__doPromote(self.__whiteQueen, self.__blackQueen, "DAME")

    def __doPromote(self, Team0Figure, Team1Figure, promotionName:str):
        '''
            Vor.: Es existiert ein aktiver Promotion-Kontext in der Liste -__PawnPromotes-. 
            Team0Figure ist eine Figur instanz, welche beschreibt zu welche Figure auf dem Feld des Bauern für Team 0 auf dem Feld des Bauern zu setzten ist. 
            Team1Figure ist eine Figur instanz, welche beschreibt zu welche Figure auf dem Feld des Bauern für Team 1 auf dem Feld des Bauern zu setzten ist. 
            promotionName ist eine gueltige Netzwerkbezeichnung des Schachprotokolls, welche die Promotion beschreibt.
        Eff.: Der Bauer, welcher in der Liste der zu Umwandelbarenbauern hinten steht ist in eine, des seines gleichen Teams, umgewandelt.
                Und der andere Spieler ist an der Reihe. Das -image- ist aktualiesiert. Wenn das Brett in Netzwerkmodus ist, ist die Promotion, dem anderen Schachbrett mitgeteilt.
        Erg.: -
        '''
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
        '''
        Vor.: Ein regelkonformer Zug wurde ausgefuehrt.
        Eff.: Promotion/Matt/Remis sind ueberprueft und erzeugen die jeweiligen grafischen Aenderungen.
            Der self.__eventMode ist zu "chooseFigure" geändert und der andere Spieler ist an der Reihe, außer das Spiel ist durch den Zug beendent, weil ein Patt oder ein Matt ausgeloest wurde.
            In diesem Fall ist die Situation in der Konsole beschrieben und beim Matt sind alle Felder einzeln umrandet und mit einem gruenen Punkt versehen.
            Bei einer Pattsituation sind nur alle Felder, jeweils grün eingeramt.
            Auch ist, dann das Brett.image aktualiesiert.
            Wenn eine Bauerentwicklungsmoeglichkeit erkannt wurde ist ein neues Dialogfenster auf der -self.image- Surface gezeichnet mit der Interaktionsmoeglichkeit auszuwaehlen, zu was sich der Bauer entwickeln soll.
            der aktualisiert Spielzustand ist aktualiesiert und der andere Spieler ist nun an der Reihe, wenn keine Eingaben mehr von dem Spieler zu den Zug benoetigt wurden.
        Erg.: -
        '''
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
        '''
        Vor.: -team- ist eine gueltige Team-ID.
        Eff.: -
        Erg.: -True- ist geliefert, wenn das Team mindestens einen legalen Zug hat, sonst ist -False- geliefert.
        '''
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
        '''
        Vor.: -
        Eff.: -
        Erg.: Eine Liste mattgesetzter Teams oder [-1], falls kein Matt vorliegt.
            Matt bedeutet, dass eine Figur mit Koenigsrolle bedroht wird und kein Zug durchgefuert werden kann, welche dafuer sorgt, dass dies nicht mehr der Fall ist.
        '''
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
        '''
        Vor.: -self.fields- ist eine Liste mit ausschließlichen Feldinstanzen des eigenen Brettes.
        Eff.: -
        Erg.: Eine Liste aller Figuren mit Koenigsrolle, welche von anderen Figuren im naechsten gegnerischen Zug geschlagen werden koennten, ist geliefert.
        '''
        KingFields:list[Feld] = self.__getFieldsWithKings()
        checkedKings:list[int] = []
        for KingField in KingFields:
            if len(self.__getDangerFieldsToTheField(KingField)) != 0:
                checkedKings.append(KingField)
        return checkedKings 
    
    def __getCheckedTeams(self)->list[int]:
        '''
        Vor.: -
        Eff.: -
        Erg.: Eine Liste aller Teams, deren Figur mit Koenigsrolle aktuell im Schach steht, ist geliefert.
        '''
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
        '''
        Vor.: -OriginField- enthaelt eine Figur und beide Felder sind Feldinstanzen aus -self.fields-.
        Eff.: -
        Erg.: Eine Liste bedrohender Felder nach dem simulierten Zug ist geliefert.
        '''
        resultingDangerFields:list[Feld] = [] 
        MovingFigure = OriginField.getFigure()
        if MovingFigure == None:
            raise Exception("ERROR: Es muss schon ne Figur auf dem Ursprungsfeld stehen (__getDangerFieldsWhenMove)")
        
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
        '''
        Vor.: -testForField- ist ein gueltiges Feld, -TeamID- optional eine Team-ID.
        Eff.: -
        Erg.: Eine Liste aller Felder, deren Figuren das Zielfeld bedrohen, ist geliefert.
        '''
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
        '''
        Vor.: -
        Eff.: -
        Erg.: Eine Liste aller Felder auf dem eine Figur mit Koenigsrolle steht ist geliefert.
        '''
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
        '''
        Vor.: -
        Eff.: Das aktive Team ist gewechselt.
        Erg.: -
        '''
        self.__onTurnTeam = (self.__onTurnTeam+1)%2

    def __chooseFigureEvent(self, clickedField:Feld)->bool:
        '''
        Vor.: -clickedField- ist ein gueltiges Feld.
        Eff.: Wenn auf -clickedField- eine Figur steht, welche der aktuelle Spieler bewegen darf sind moegliche Ziele von der Figur -clickedField- markiert und der Eventmodus ist auf setFigure angepasst.
        Erg.: -True- ist geliefert, wenn eine waehlbare Figur aktiviert wurde, sonst ist -False- geliefert.
        '''
        clickedFigure:None|Springer|Turm|Bauer|Laeufer|Dame|Koenig = clickedField.getFigure()
        clickedFieldLabel:str = clickedField.getLabel()
        if clickedFigure == None:
            self.__clearAllFieldHighlights() 
            self.__eventMode = "chooseFigure"
            return False

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
        '''
        Vor.: -
        Eff.: Alle Hervorhebungen von Feldern aus -self.fields- sind entfernt.
        Erg.: -
        '''
        for key in self.__fields.keys():
            field = self.__fields[key]
            if type(field) != Feld:
                continue
            field.clearFieldHighlights()

    def getPossibleTurnFields(self, Field:Feld, ignoreChecksOrAnxiety:bool=False, ignoreBuildingChecks:bool=False, ignoreCastling:bool=False)->list[Feld]:        # Geht sicher, dass nicht doch irgendwie Ein Feld außerhalb des Brettes ist arbeitet noch Relative
        '''
        Vor.: -Field- ist ein gueltiges Feld; die bool Flags steuern Filterregeln.
        Eff.: -
        Erg.: Eine Liste aller moeglichen gueltigen Zielfelder fuer den Zug ist geliefert.
        '''
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
        '''
        Vor.: -FigureFieldLabel- ist ein gueltiges Feldlabel mit waehlbarer Figur.
        Eff.: Markiert alle moeglichen Zielfelder.
        Erg.: -
        '''
        for field in self.getPossibleTurnFields(self.__fields[FigureFieldLabel]):
            if type(field) == Feld:
                field.addFieldHighlight("SmallGreenMiddleCircle")
            
    def __getOnlyPointsList(self,TurnsDatas:list[dict])->list[tuple]: ## nicht genutzt
        '''
        Vor.: -TurnsDatas- ist eine Liste von Zugdaten-Dictionaries mit Key -point-.
        Eff.: -
        Erg.: Eine Liste der relativen Punkte ist geliefert. 
        '''
        PointsList:list = []                      #
        for TurnData in TurnsDatas:               #
            PointsList.append(TurnData["point"])  # Zur Weiterverarbeitung sind nur noch die Relativen Punkte notwending 
        return PointsList
    
    def __getOnlyTurnDataWithValidFields(self, turnsData:list[dict])->list[dict]:
        '''
        Vor.: -turnsData- ist eine Liste potentieller Zugdaten, die Liste hat als Inhalt ausschließlich dicts mit dem Key "fieldLabel" oder keine Inhalte.
        Eff.: -
        Erg.: Eine bereinigte Liste gueltiger Zugdaten von -turnsData- ist geliefert. Zuege mit nicht gueltigem Zielzugfeld bezeichnungen sind nicht in der Liste.
        '''
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
        '''
        Vor.: -turnsData- ist eine Liste potentieller Zugdaten, die Liste hat als Inhalt ausschließlich dicts mit dem Key "fieldLabel" oder keine Inhalte. -TeamID- die Team-ID des zu ziehenden Teams.
        Eff.: -
        Erg.: Eine gefilterte Liste ohne Zugdaten, welche eine eigene Figur schlagen wuerde, ist geliefert.
        '''
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
        '''
        Vor.: -startingPointField- ist ein gueltiges Feld; Flags steuern Regelpruefungen.
        Eff.: -
        Erg.: Eine Liste mit legalen Zugdaten ist geliefert.
            Die gelieferte Liste besitzt nur Tabellen oder keine Eintraege.
            Die Tabellen in der Liste besitzen folgende Informationen:
                "" steht fuer den Key und das hinter dem = fuer die Erklaerung des Values
                "point" = :tuple[int, int] (gueltige Feldbezeichnung, die relativ zu -originFieldLabel- die Anzahl der Felder angibt, die fuer einen Zug in Buchstaben und Zahlen Richtung noetig sind)
                "fieldLabel" = :str eine gueltige Feldbezeichnung (das erste Zeichen ist ein Buchstabe im Berreich des Buchstaben der Anfangsbeschriftungs und dem Buchstaben der Anfangsbeschriftungs versetzt um die Feldanzahl / das zweite Zeichen ist eine Zahl im Berreich der Zahl der Anfangsbeschriftungs und der Zahl der Anfangsbeschriftungs versetzt um die Feldanzahl) zu dem sich die Figur bewegen soll.
                "onlyOnKill" = :bool (-True-, wenn die Figur nur den Zug machen kann, wenn sie dabei eine andere Figur schlagen wuerde)
                "canKill" = :bool (-True-, wenn die Figur beim Zug auf das Zielfeld eine andere Figur schlagen koennte)
                "killMaybeFigureType" =  (Klasse der Figur, die geschlagen werden kann)
                "killMaybeFigureField" = :str (Feldbezeichnung des Feldes, auf dem eine Figur geschlagen werden kann)
                "killMaybeFigureMustHadDoubleWalkLastTurn" = :bool (beschreibt, ob die Figur, die geschlagen werden kann, im letzten Zug einen Doppelzug gemacht hat)
                "hasAnxiety" = :boool oder immer True, wenn die Figur die Koenigsrolle traegt (beschreibt, ob die Figur auf dem Zeilfeld des Zuges geschlagen werden koennte)
                "specialTurnType" = :str (spezielle Zugbezeichnung)
                "needFigureOnField" = :str (Zug ist nur moeglich, wenn auf dem Feld eine Figur steht und ein anderes Feld angegeben ist)
                "neededFigureType" =  (ueberprueft, ob der Zug einer bestimmten hier angegebender Figur als Figurklasse mit der Figur auf dem Feld uebereinstimmt)
                "allowNeededFigureHasTurned" = :bool (beschreibt, ob sie die Figur auf dem Feld -needFigureOnField- schon bewegt hat)
                "endPointNeededFigure" = :str (Feldbezeichnung, auf dem die Firgur nach dem Zug steht)
                "onDoneTurnCall" = :Callable (beschreibt die Methode/Funktion, die nach dem Zug ausgefuerht wird)
        '''
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
        '''
        Vor.: -FieldLabel- ist eine gueltige Feldbezeichnung.
        Eff.: -
        Erg.: Die Positions-IDs [Buchstabe als ord, Zahl] sind geliefert.
        '''
        return [ord(FieldLabel[0]), int(FieldLabel[1])]
    
    def __getLabelByPositionIDs(self, PositionIDs:list[int, int])->str:
        '''
        Vor.: -PositionIDs- enthaelt gueltige Buchstaben-/Zahlen-IDs.
        Eff.: -
        Erg.: Das Feldlabel ist geliefert.
        '''
        return chr(PositionIDs[0])+str(PositionIDs[1])

    def __getFieldsBetweenHorizontalVerticalOnly(self, startingField:Feld, targetField:Feld)->list[Feld]:
        '''
        Vor.: Start- und Zielfeld liegen auf einer gemeinsamen Zeile oder Spalte.
        Eff.: -
        Erg.: Alle dazwischenliegenden Felder ohne Endpunkte sind geliefert.
        '''
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
        '''
        Vor.: -KingField- und -TargetField- gehoeren zum Rochade-Kontext.
        Eff.: -
        Erg.: -True- bei erfuellten Rochadebedingungen, sonst -False-.
        '''
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
        '''
        Vor.: -relativeMaybePossibleTurnsData- enthaelt lineare Zugmuster, -startField- ist gueltig.
        -relativeMaybePossibleTurnsData- besteht aus Tabellen oder ist Leer. 
        Die Tabellen haben folgende Informationen:
                "" steht fuer den Key und das hinter dem = fuer die Erklaerung des Values
                "point" = :tuple[int, int] (gueltige Feldbezeichnung, die relativ zu -originFieldLabel- die Anzahl der Felder angibt, die fuer einen Zug in Buchstaben und Zahlen Richtung noetig sind)
                "fieldLabel" = :str eine gueltige Feldbezeichnung (das erste Zeichen ist ein Buchstabe im Berreich des Buchstaben der Anfangsbeschriftungs und dem Buchstaben der Anfangsbeschriftungs versetzt um die Feldanzahl / das zweite Zeichen ist eine Zahl im Berreich der Zahl der Anfangsbeschriftungs und der Zahl der Anfangsbeschriftungs versetzt um die Feldanzahl) zu dem sich die Figur bewegen soll.
                "onlyOnKill" = :bool (-True-, wenn die Figur nur den Zug machen kann, wenn sie dabei eine andere Figur schlagen wuerde)
                "canKill" = :bool (-True-, wenn die Figur beim Zug auf das Zielfeld eine andere Figur schlagen koennte)
                "killMaybeFigureType" =  (Klasse der Figur, die geschlagen werden kann)
                "killMaybeFigureField" = :str (Feldbezeichnung des Feldes, auf dem eine Figur geschlagen werden kann)
                "killMaybeFigureMustHadDoubleWalkLastTurn" = :bool (beschreibt, ob die Figur, die geschlagen werden kann, im letzten Zug einen Doppelzug gemacht hat)
                "hasAnxiety" = :boool oder immer True, wenn die Figur die Koenigsrolle traegt (beschreibt, ob die Figur auf dem Zeilfeld des Zuges geschlagen werden koennte)
                "specialTurnType" = :str (spezielle Zugbezeichnung)
                "needFigureOnField" = :str (Zug ist nur moeglich, wenn auf dem Feld eine Figur steht und ein anderes Feld angegeben ist)
                "neededFigureType" =  (ueberprueft, ob der Zug einer bestimmten hier angegebender Figur als Figurklasse mit der Figur auf dem Feld uebereinstimmt)
                "allowNeededFigureHasTurned" = :bool (beschreibt, ob sie die Figur auf dem Feld -needFigureOnField- schon bewegt hat)
                "endPointNeededFigure" = :str (Feldbezeichnung, auf dem die Firgur nach dem Zug steht)
                "onDoneTurnCall" = :Callable (beschreibt die Methode/Funktion, die nach dem Zug ausgefuerht wird)
        Eff.: -
        Erg.: -relativeMaybePossibleTurnsData- ist nur noch mit erreichbaren Zugdaten ohne Durchlaufen von Figuren geliefert.
        '''
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
        Vor.: 'Line' beschreibt Zuege und ist nach zunehmenden Zugabstand sortiert und geht entweder nur Wagerecht oder nur Horizontal in eine Linie.
            'Linie' besteht entweder aus keinen Werten oder aus Tabellen.
            Wenn sie Tabellen enthaelt hat jede Tabelle aus 'Linie' den Key "fieldLabel", weldches eine gueltige Feldbezeichnung als String enthaelt.
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
        '''
        Vor.: -DataDict- besitzt den Key -point-.
        Eff.: -
        Erg.: Der zugehoerige Punkt als Tupel ist geliefert.
        '''
        return DataDict['point']
    
    def __sortToDestination(self, Line:list[dict], sortIndex:int)->list[list[dict]]:
        '''
        Vor.: -Line- ist eine Liste von Zugdaten mit Punktwerten.
        Eff.: -
        Erg.: Zwei richtungsgetrennte, sortierte Teillisten sind geliefert.
        '''
        Line.sort(key=self.__getPointFromDict)
        Line = self.__SpitNegativePoints(Line, sortIndex)
        return self.__reverseFirstPart(Line)
    
    def __reverseFirstPart(self, Line:list)->tuple:
        '''
        Vor.: -Line- enthaelt zwei Teillisten.
        Eff.: -
        Erg.: Ein Tupel aus erster umgedrehter Teilliste und zweiter Teilliste ist geliefert.
        '''
        firstPartLine = Line[0]
        if type(firstPartLine) == list:
            firstPartLine.reverse()
        return firstPartLine, Line[1]
    
    def __SpitNegativePoints(self, Line:list[dict], SplitNumberIndex:int)->list[list, list]:
        '''
        Vor.: -Line- enthaelt Zugdaten als Tabellen mit numerischen Punktwerten als tuple und einer laenge von 2 unter dem Schluessel 'point'. -SplitNumberIndex- ist 0 oder 1
        Eff.: -
        Erg.: Eine Listen mit zwei Listen, welche die positven und negativen beschriebenden Punktwert bei dem -SplitNumberindex- Punktwert des tuples der jeweiligen Tabelle beim key 'point' (Liste mit Tabellen mit negativen Punktwert beim Tuple beim -SplitNumberIndex- aus der 'point' Tabelle aus -Line-, Liste mit positiven Punktwert beim Tuple beim -SplitNumberIndex- aus der 'point' Tabelle aus -Line-) sind geliefert.
        '''
        LinePositives = []
        LineNegatives = []

        for Element in Line:
            if Element['point'][SplitNumberIndex] < 0:
                LineNegatives.append(Element)
                continue
            LinePositives.append(Element)
        return LineNegatives, LinePositives

    def getRelativeField(self, fieldLabel:str, relativeField:tuple[int, int])->Feld|None:
        '''
        Vor.: -fieldLabel- ist ein Startlabel, -relativeField- ein relativer Versatz.
        Eff.: - HIER WEITER
        Erg.: Das relative Zielfeld oder -None- bei Ungueltigkeit ist geliefert.
        '''
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
        '''
        Vor.: -pos- ist eine Pixelkoordinate.
        Eff.: Ermittelt anhand der Koordinate das zugehoerige Feld.
        Erg.: Das gefundene Feld oder -None- ist geliefert.
        '''
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

