import pygame
from timers import TIMER
import math


class MENU:
    def __init__(self, puck_game):
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings

        self.image = pygame.image.load('sprites/menu/menu.png')
        self.rect = self.image.get_rect()

        self.timer_start = TIMER(self, 30, True)
        self.timer_ani = TIMER(self, 11, True)

    def update_timers(self):
        self.timer_start.update()
        self.timer_ani.update()

    def blitme(self):
        self.screen.fill(self.settings.bg_color)
        self.screen.blit(self.image, self.rect)

        # slowly blink text
        if self.timer_start.count < 15:
            self.game.text_start = False
        # print text
        self.game.write_text()
        # animate giant puckman
        image_index = math.floor(self.timer_ani.count / 4)
        temp_file = 'sprites/menu/' + str(image_index) + '.png'
        image_puck = pygame.image.load(temp_file)
        self.screen.blit(image_puck, (40, 150))

        pygame.display.flip()
