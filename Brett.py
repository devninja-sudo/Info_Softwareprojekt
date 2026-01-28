import pygame
from sys import exit
from Feld import Feld

class Brett(pygame.sprite.Sprite):
    def __init__(self, edge_length:int, topLeftCorner:tuple[int, int], field_color1:str="yellow", field_color2:str="red", rotation:int=0, fields_count:int=8):
        super().__init__()

        self.__rotation = rotation
        self.__edge_length = edge_length
        self.__field_length = edge_length//fields_count
        self.__fields_count = fields_count

        self.__field_color_1 = field_color1
        self.__field_color_2 = field_color2

        self.__field_label_start_letter = "a"

        #die Variablen müssen so heißen und public sein wegen Pygame
        self.image = pygame.surface.Surface((edge_length, edge_length))
        self.rect = self.image.get_rect(topleft = topLeftCorner)

        self.__fields = self.__createFields()
        self.__generateImage()

    def setRotation(self, rotation:int):
        self.__rotation = rotation
        self.__correctFieldPositions()

    def __correctFieldPositions(self):
        for key in self.__fields.keys():
            self.__fields[key].setFieldPosition(self.__getFieldPositionByName(key))
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
                field_current = Feld((self.__field_length, self.__field_length), self.__getFieldPositionByName(chr(spread)+str(lengths)), color)
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
            x, y = self.__rotate90degree((x, y))
        return x, y
    

    def __rotate90degree(self, point:tuple[int, int]):
        return (self.__edge_length-point[1]-self.__field_length, point[0])
    
    def __getFieldsGroup(self)->pygame.sprite.Group:
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
        pass

    def getFieldByCords(self, pos:tuple[int, int]):
        x = pos[0]-self.rect.topleft[0]
        y = pos[1]-self.rect.topleft[1]
        if not(self.rect.collidepoint(x, y)):
            return 
        
        for key in self.__fields.keys():
            field = self.__fields[key]
            if field.getRect().collidepoint(x, y):
                return key

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption('Brett Test')
    clock = pygame.time.Clock()


    TestBrettGroup = pygame.sprite.GroupSingle()
    Spielbrett = Brett(800, (10, 10), "white", "black")
    TestBrettGroup.add(Spielbrett)
    
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                continue
            if event.type == pygame.MOUSEBUTTONUP:
                print(Spielbrett.getFieldByCords(pygame.mouse.get_pos()))
        TestBrettGroup.draw(screen)
        TestBrettGroup.update()
        pygame.display.update()
        clock.tick(60)
        #Spielbrett.setRotation(int(input()))
