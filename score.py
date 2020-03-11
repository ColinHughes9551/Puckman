import pygame


class SCORE(pygame.sprite.Sprite):
    """A class to manage small number prompts."""

    def __init__(self, puck_game, x, y, value):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        """Initialize the puck and set its starting position."""
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings

        # Load the score image
        temp_file = 'sprites/score/' + str(value) + '.png'
        self.image = pygame.image.load(temp_file)
        self.rect = self.image.get_rect()
        self.life = 40
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.life -= 1
        if self.life % 4 == 0:
            self.rect.y -= 1
        if not self.life:
            # perish
            self.kill()
            del self

    def blitme(self):
        self.screen.blit(self.image, self.rect)
