import pygame
from sys import exit
from FigurBuilder import FigurBuilder
from Turm import Turm
class Koenig(FigurBuilder):
    def __init__(self, image:str, size:int, field_length:int, feldanzahl:int, buchstabeFeldbezeichnung:str, teamID:int, mussSchlagen:bool=False):
        super().__init__(image, size, field_length, feldanzahl, buchstabeFeldbezeichnung, teamID, True)

        self.__mussSchlagen:bool = mussSchlagen
        self.__kannSchlagen:bool = True


        self.__hatAngst:bool = True
        self.setKingRole(True)
        


    def getMaybePossibleTurns(self, vorherigesFeldBezeichnung:str)->list[dict]:
        moeglicheZuege = []
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if i == 0 and j == 0:
                    continue
                moeglicheZuege = self.gebeNeueZuglisteMitNeuemZug(vorherigesFeldBezeichnung, moeglicheZuege, (i, j), self.__mussSchlagen, self.__kannSchlagen, self.__hatAngst)
        if not(self.getHasMoved()):
            moeglicheZuege = self.gebeNeueZuglisteMitNeuemZug(vorherigesFeldBezeichnung, moeglicheZuege, (2, 0), False, False, True, "castling", self.konvertiererelativenPunktzuFeldbezeichnung(vorherigesFeldBezeichnung, (3, 0)), Turm, False, self.konvertiererelativenPunktzuFeldbezeichnung(vorherigesFeldBezeichnung, (1, 0)))
            moeglicheZuege = self.gebeNeueZuglisteMitNeuemZug(vorherigesFeldBezeichnung, moeglicheZuege, (-2, 0), False, False, True, "castling", self.konvertiererelativenPunktzuFeldbezeichnung(vorherigesFeldBezeichnung, (-3, 0)), Turm, False, self.konvertiererelativenPunktzuFeldbezeichnung(vorherigesFeldBezeichnung, (-2, 0)))
        return moeglicheZuege




if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,400))
    pygame.display.set_caption('Koenig Test')
    clock = pygame.time.Clock()


    TestKoenigGroup = pygame.sprite.GroupSingle()
    TestKoenig = Koenig("assets/graphics/s_koenig.png", 80, 400, 8, "a", 1)
    TestKoenigGroup.add(TestKoenig)
    print(TestKoenig.getMaybePossibleTurns("a1"))
    while True:
        screen.fill("white")
        for event in pygame.event.get():
	        if event.type == pygame.QUIT:
                  pygame.quit()
                  exit()
        TestKoenigGroup.draw(screen)
        TestKoenigGroup.update()
        pygame.display.update()
        clock.tick(60)
