import pygame


class PORTAL(pygame.sprite.Sprite):
    """A class to manage portals"""

    def __init__(self, puck_game, portal_id):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        """Initialize the puck and set its starting position."""
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings
        # save the array position of portal to identify by
        self.id = portal_id

        # Load the portal image and get it's rect
        self.image = pygame.image.load('sprites/puck/closed16.png')
        self.rect = self.image.get_rect()

        # starting position
        if portal_id:
            self.rect.x = self.game.settings.screen_width - 24
        else:
            self.rect.x = 8
        self.rect.y = 112

    def blitme(self):
        """Draw the puckin' guy at its current location."""
        self.screen.blit(self.image, self.rect)
