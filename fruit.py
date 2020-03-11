import pygame


class FRUIT(pygame.sprite.Sprite):
    """A class to manage fruits on the map."""

    def __init__(self, puck_game, value):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        """Initialize the puck and set its starting position."""
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings

        # decide sprite via fruit type
        self.value = value
        temp_file = 'sprites/items/' + str(value) + '.png'
        self.image = pygame.image.load(temp_file)
        self.rect = self.image.get_rect()
        self.life = 600

        # decide score value via fruit type
        if value == 0:
            self.score = 100
        if value == 1:
            self.score = 300
        if value == 2:
            self.score = 500
        if value == 3:
            self.score = 700
        if value == 4:
            self.score = 1000
        if value == 5:
            self.score = 2000
        if value == 6:
            self.score = 3000
        if value == 7:
            self.score = 5000

        # place in the one spot that fruits go
        self.rect.x = 104
        self.rect.y = 136

    def update(self):
        self.life -= 1
        if self.life <= 0:
            # perish
            self.kill()
            del self

    def blitme(self):
        self.screen.blit(self.image, self.rect)
