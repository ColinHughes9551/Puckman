import pygame


class GHOST(pygame.sprite.Sprite):
    """A class to manage the ghosts."""

    def __init__(self, puck_game):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        """Initialize the puck and set its starting position."""
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings

        # Load the puck image and get its rect.
        self.image = pygame.image.load('sprites/ghosts/ghost_test.png')
        self.rect = self.image.get_rect()
        # Start ghost at starting location
        self.rect.center = self.screen_rect.center

        # Store a decimal value for the puck's horizontal position.
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # have a personal speed setting so it can be lowered when blue
        self.speed = 1

        # Movement flag
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def update(self):
        # put automated movement through maze and path finding

        # only move up and down if not moving left and right
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.speed
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.speed
        if self.moving_up and self.rect.top > 0:
            self.y -= self.speed

        # Update rect object from x and y
        self.rect.x = self.x
        self.rect.y = self.y

    def _clear_movement(self):
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def _check_node_collision(self, game, x_adj=0, y_adj=0):
        # adjust position
        self.rect.x = self.x + x_adj
        self.rect.y = self.y + y_adj

        # get a list of all nodes puck_man is in
        node_col_list = pygame.sprite.spritecollide(self, game.maze.nodes, False)

        # return to previous position
        self.rect.x = self.x - x_adj
        self.rect.y = self.y - y_adj

        # Check the list of colliding sprites, and check if they have collisions enabled
        for node in node_col_list:
            if node.collision:
                return True
        # if no collision found
        return False

    def blitme(self):
        """Draw the puckin' guy at its current location."""
        self.screen.blit(self.image, self.rect)
