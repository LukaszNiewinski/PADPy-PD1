from GameView import *
from GameMenu import *
from GameModel import *
from GameOptions import *
import sys


class Gauntlet(pygame.sprite.Sprite):
    resolution = (60, 60)

    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("gauntlet.jpg", -1)
        self.clickedImage = pygame.transform.scale(self.image, (self.resolution[0]-8, self.resolution[1]-8))
        self.normalImage = pygame.transform.scale(self.image, self.resolution)
        self.image = self.normalImage
        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(False)
        self.clickedSound = FunContainer.load_sound("click.wav")
        self.muted = None

    def update(self):
        self.rect.midtop = pygame.mouse.get_pos()

    def clicked(self):
        if not self.muted:
            self.clickedSound.play()
        self.image = self.clickedImage

    def unclicked(self):
        self.image = self.normalImage


class GameController:
    FPS = 30
    music = "stronghold.mp3"

    def __init__(self, gameView: GameView, gameMenu: GameMenu, gameOptions: GameOptions, deep: tuple):
        self.muted = False
        self.game_mode = None
        self.deep = deep

        self.gauntlet = Gauntlet()
        self.gauntlet.muted = self.muted

        self.gameView = gameView
        self.gameView.gauntlet = self.gauntlet

        self.gameModel = self.gameView.gameModel

        self.gameOptions = gameOptions
        self.gameOptions.gauntlet = self.gauntlet

        self.gameOptions.backToMenuButton.action = self.main_menu
        self.gameOptions.soundButton.action = self.on_off_sound
        self.gameOptions.changePlayerButton.action = self.change_mode

        self.set_indicators()

        self.gameMenu = gameMenu
        self.gameMenu.gauntlet = self.gauntlet
        self.gameMenu.optionsButton.action = self.main_options

        self.gameMenu.playButton.action = self.game_mode
        self.gameMenu.quitButton.action = self.exit

        self.clock = pygame.time.Clock()

        pygame.mixer.music.load(os.path.join(FunContainer.data_dir, self.music))

    def set_indicators(self):
        self.gameOptions.changePlayerIndicator.set_state(False)
        self.gameOptions.soundIndicator.set_state(False)
        self.game_mode = self.player_vs_computer

    def main_menu(self):
        if not pygame.mixer.music.get_busy() and not self.muted:
            pygame.mixer.music.play(-1)
        pygame.time.delay(500)
        self.gameMenu.init_draw()
        while True:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    self.gauntlet.clicked()
                    pos = pygame.mouse.get_pos()
                    spriteClicked = self.gameMenu.allButtons.focused_sprite(pos)
                    if spriteClicked:
                        self.gameMenu.view_update()
                        spriteClicked.action()
                elif event.type == MOUSEBUTTONUP:
                    self.gauntlet.unclicked()
            self.gameMenu.view_update()



    def main_game(self):
        pygame.time.delay(500)
        pygame.mixer.music.stop()
        self.gameView.init_draw()
        spriteClicked = None
        while True:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.main_menu()
                elif event.type == MOUSEBUTTONDOWN:
                    self.gauntlet.clicked()
                    if not spriteClicked:
                        pos1 = pygame.mouse.get_pos()
                        pos1 = self.gameView.cartesian2board(pos1)
                        ballsClickedColor = self.gameModel.ballsMap[pos1]
                        if ballsClickedColor == self.gameModel.activePlayer.color:
                            spriteClicked = True
                            print("bill taken correctly")
                    else:
                        pos2 = pygame.mouse.get_pos()
                        pos2 = self.gameView.cartesian2board(pos2)
                        try:
                            if self.gameModel.move_ball(pos1, pos2):
                                self.gameView.balls_update()
                                if self.gameModel.check_if_game_finish():
                                    raise EndGame
                                self.gameModel.change_player()
                                print("bill moved corectly")
                        except(SystemExit):
                            exit(0)
                            # self.game.new_game()
                            # self.set_player_indicator()
                            # self.main_menu()
                        spriteClicked = False
                elif event.type == MOUSEBUTTONUP:
                    self.gauntlet.unclicked()
            self.gameView.view_update()

    def computer_vs_computer(self):
        pygame.time.delay(500)
        pygame.mixer.music.stop()
        self.gameView.init_draw()
        player1Turn = True
        while True:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.main_menu()
                if player1Turn:
                    if event.type == MOUSEBUTTONDOWN:
                        print("Player 1 - Black - is making his move", self.gameModel.activePlayer.color)
                        self.gameModel.intelligent_move(self.deep[0])
                        self.gameView.balls_update()
                        print("Computer 1 made his move!")
                        if self.gameModel.check_if_game_finish():
                            raise EndGame
                        player1Turn = False
                        self.gameModel.change_player()
                else:
                    print("Player 2 - White - is making his move", self.gameModel.activePlayer.color)
                    self.gameModel.intelligent_move(self.deep[1])
                    self.gameView.balls_update()
                    print("Computer 2 made his move!")
                    if self.gameModel.check_if_game_finish():
                        raise EndGame
                    player1Turn = True
                    self.gameModel.change_player()
            self.gameView.view_update()

    def player_vs_computer(self):
        pygame.time.delay(500)
        pygame.mixer.music.stop()
        self.gameView.init_draw()
        spriteClicked = None
        player1Turn = True
        while True:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.main_menu()
                if player1Turn:
                    if event.type == MOUSEBUTTONDOWN:
                        self.gauntlet.clicked()
                        if not spriteClicked:
                            pos1 = pygame.mouse.get_pos()
                            pos1 = self.gameView.cartesian2board(pos1)
                            ballsClickedColor = self.gameModel.ballsMap[pos1]
                            if ballsClickedColor == self.gameModel.activePlayer.color:
                                spriteClicked = True
                                print("Sprite clicked")
                        else:
                            pos2 = pygame.mouse.get_pos()
                            pos2 = self.gameView.cartesian2board(pos2)
                            try:
                                if self.gameModel.move_ball(pos1, pos2):
                                    self.gameView.balls_update()
                                    self.gameModel.change_player()
                                    player1Turn = False
                                    print("player changed")
                            except(SystemExit):
                                exit(0)
                                # self.game.new_game()
                                # self.set_player_indicator()
                                # self.main_menu()
                            print("Sprite unclicked")
                            spriteClicked = False
                    elif event.type == MOUSEBUTTONUP:
                        self.gauntlet.unclicked()
                else:
                    #funkcja inteligent move, atrybut to parametr określający głębokość drzewa przeszukiwania
                    self.gameModel.intelligent_move(self.deep[1])
                    self.gameView.balls_update()
                    if self.gameModel.check_if_game_finish():
                        raise EndGame
                    self.gameModel.change_player()
                    player1Turn = True
            self.gameView.view_update()

    def main_options(self):
        pygame.time.delay(500)
        self.gameOptions.init_draw()
        while True:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.main_menu()
                elif event.type == MOUSEBUTTONDOWN:
                    self.gauntlet.clicked()
                    pos = pygame.mouse.get_pos()
                    spriteClicked = self.gameOptions.allButtons.focused_sprite(pos)
                    if spriteClicked:
                        self.gameOptions.view_update()
                        spriteClicked.action()
                elif event.type == MOUSEBUTTONUP:
                    self.gauntlet.unclicked()
            self.gameOptions.view_update()

    def change_mode(self):
        self.gameOptions.changePlayerIndicator.change_state()
        if self.game_mode == self.player_vs_computer:
            self.game_mode = self.computer_vs_computer
            self.gameMenu.playButton.action = self.game_mode
            print("Computer vs computer set")
        else:
            self.game_mode = self.player_vs_computer
            self.gameMenu.playButton.action = self.game_mode
            print("Player vs computer set")

    def on_off_sound(self):
        self.gameOptions.soundIndicator.change_state()
        if self.muted:
            pygame.mixer.unpause()
            pygame.mixer.music.play()
            self.muted = False
            print("Sound turned on")
        else:
            pygame.mixer.music.stop()
            pygame.mixer.pause()
            self.muted = True
            print("Sound turned off")
        self.gauntlet.muted = self.muted

    @classmethod
    def exit(cls):
        pygame.time.delay(500)
        pygame.quit()
        sys.exit(0)
