import pygame
from pygame.locals import *
import sys, os
import numpy as np

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")


class FunContainer:
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, "resources")

    def __init__(self):
        pass

    @classmethod
    def load_image(cls, name, colorkey=None):
        fullname = os.path.join(cls.data_dir, name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error:
            print("Cannot load image {}".format(name))
            raise SystemExit
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image

    @classmethod
    def load_sound(cls, name):
        class NoneSound:
            def play(self): pass

        if not pygame.mixer:
            return NoneSound()
        fullname = os.path.join(cls.data_dir, name)
        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error:
            print("Cannot load sound: {}".format(name))
            raise SystemExit
        return sound


class WhiteBall(pygame.sprite.Sprite):
    resolution = (35, 35)

    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("white-ball.jpg", -1)
        self.imageOnFocus = pygame.transform.scale(self.image, (self.resolution[0]+5, self.resolution[1]+5))
        self.imageBase = pygame.transform.scale(self.image, (self.resolution[0], self.resolution[1]))
        self.image = self.imageBase
        self.rect = self.image.get_rect()
        self.rect.move_ip(100, 100)

        self.clicked = False

    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.image = self.imageOnFocus
        else:
            self.image = self.imageBase

    def click(self):
        self.clicked = True

    def unclick(self):
        self.clicked = False


class BlackBall(WhiteBall):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = FunContainer.load_image("black-ball.jpg", -1)
        self.imageOnFocus = pygame.transform.scale(self.image, (self.resolution[0]+5, self.resolution[1]+5))
        self.imageBase = pygame.transform.scale(self.image, (self.resolution[0], self.resolution[1]))
        self.image = self.imageBase
        self.rect = self.image.get_rect()
        self.rect.move_ip(200, 100)

    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.image = self.imageOnFocus
        else:
            self.image = self.imageBase


class App(FunContainer):
    windowWidth = 800
    windowHeight = 800
    numOfCells = 19
    cellWidth = np.floor_divide(windowWidth, numOfCells)
    cellHeight = np.floor_divide(windowHeight, numOfCells)
    windowName = "Castle game"

    def __init__(self):
        super().__init__()
        pygame.init()
        self.screen = pygame.display.set_mode((self.windowWidth, self.windowHeight))
        pygame.display.set_caption(self.windowName)
        self.background = FunContainer.load_image("background.jpg")
        self.background = pygame.transform.scale(self.background, (self.windowWidth, self.windowHeight))
        self.screen.blit(self.background, (0, 0))
        pygame.display.update()
        self.clock = pygame.time.Clock()
        self.whiteBall = WhiteBall()
        self.blackBall = BlackBall()
        self.abc = pygame.sprite.RenderPlain((self.whiteBall, self.blackBall))
        self.board = self.board_init()
        self.app_loop()

    def board_init(self):
        board = np.array([[0]*19], dtype=Rect)
        for i in range(self.numOfCells):
            for j in range(self.numOfCells):
                board[i][j] = Rect(i*self.cellWidth, j*self.cellWidth, self.cellWidth-1, self.cellHeight-1)
            return board

    def position2board(self, pos):
        x = np.floor_divide(pos[0], self.cellWidth)
        y = np.floor_divide(pos[1], self.cellHeight)
        return x, y

    def app_loop(self):
        while 1:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    print(self.position2board(pos))
                    for s in self.abc.sprites():
                        if s.rect.collidepoint(pos):
                            print("yo")


            self.abc.update()
            self.abc.clear(self.screen, self.background)
            self.abc.draw(self.screen)
            pygame.display.update()


if __name__ == "__main__":
    App()

