import pygame
from sys import exit
from FigurBuilder import FigurBuilder

class Bauer(FigurBuilder):
    def __init__(self, image:str, size:int, field_length:int, field_count:int, BuchstabeFeldbezeichnung:str, teamID:int, mussSchlagen:bool=False):
        super().__init__(image, size, field_length, field_count, BuchstabeFeldbezeichnung, teamID, False)
        self.__mussSchlagen:bool = mussSchlagen
        self.__SchritteInDenenDoppelschritteGemachtWurden:list = []

    def hatDoppelschrittgemacht(self, ZugNummer:int)->None:
        self.__SchritteInDenenDoppelschritteGemachtWurden.append(ZugNummer)

    def hatDoppelzuginZugnummer(self, testZugNummer:int)->bool:
        return testZugNummer in self.__SchritteInDenenDoppelschritteGemachtWurden

    def gebeMoeglicheZuege(self, vorherigesFeldBezeichnung:str)->list[dict]:
        moeglicheZuege:list = []
        if self.getTeam() == 0:
            richtung = 1
        else:
            richtung = -1
        moeglicheZuege = self.gebeneueZugListemitneuemZug(vorherigesFeldBezeichnung, moeglicheZuege, (0, 1*richtung), self.__mussSchlagen, False)
        if int(vorherigesFeldBezeichnung[1]) == 2 and richtung == 1:
            moeglicheZuege = self.gebeneueZugListemitneuemZug(vorherigesFeldBezeichnung, moeglicheZuege, (0, 2*richtung), self.__mussSchlagen, False, onDoneTurnCall=self.hatDoppelschrittgemacht)
        elif int(vorherigesFeldBezeichnung[1]) == 7 and richtung == -1:
            moeglicheZuege = self.gebeneueZugListemitneuemZug(vorherigesFeldBezeichnung, moeglicheZuege, (0, 2*richtung), self.__mussSchlagen, False, onDoneTurnCall=self.hatDoppelschrittgemacht)

        moeglicheZuege = self.gebeneueZugListemitneuemZug(vorherigesFeldBezeichnung, moeglicheZuege, (1, 1*richtung), True, True, schlagbareFigurenFelder=self.konvertiererelativenPunktzuFeldbezeichnung(vorherigesFeldBezeichnung, (1, 0)), moeglicherweiseSchlagbarerFigurenTyp=Bauer, zuSchlagendeFigurHatDoppelschrittGemacht=True)
        moeglicheZuege = self.gebeneueZugListemitneuemZug(vorherigesFeldBezeichnung, moeglicheZuege, (-1, 1*richtung), True, True, schlagbareFigurenFelder=self.konvertiererelativenPunktzuFeldbezeichnung(vorherigesFeldBezeichnung, (-1, 0)), moeglicherweiseSchlagbarerFigurenTyp=Bauer, zuSchlagendeFigurHatDoppelschrittGemacht=True)
        
        return moeglicheZuege

    

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Bauer Test')
    clock = pygame.time.Clock()


    TestBauerGroup = pygame.sprite.GroupSingle()
    BauerDame = Bauer("assets/graphics/s_bauer.png", 80, 400, 1)
    TestBauerGroup.add(BauerDame)
    print(BauerDame.gebeMoeglicheZuege("a1"))
    while True:
        screen.fill("white")
        for event in pygame.event.get():
	        if event.type == pygame.QUIT:
                  pygame.quit()
                  exit()
        TestBauerGroup.draw(screen)
        TestBauerGroup.update()
        pygame.display.update()
        clock.tick(60)
