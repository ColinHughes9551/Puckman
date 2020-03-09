import pygame
import math


class PUCK(pygame.sprite.Sprite):
    """A class to manage the pucking man."""

    def __init__(self, puck_game):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        """Initialize the puck and set its starting position."""
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings

        # Load the puck image and get its rect.
        self.image = pygame.image.load('sprites/puck/closed16.png')
        self.rect = self.image.get_rect()
        # Start puck at starting location
        self.rect.center = self.screen_rect.center

        # Store a decimal value for the puck's horizontal position.
        self.x = self.rect.x
        self.y = self.rect.y
        # correct placement
        self.y += 64

        # Key flag
        self.key_right = False
        self.key_left = False
        self.key_up = False
        self.key_down = False

        # Movement flag
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

        # variable to register subpixel movement
        self.subpixel = 0.0

    def update(self):
        self.subpixel += self.settings.puck_speed
        for i in range(math.floor(self.subpixel)):
            self.subpixel -= 1
            check_distance = 1
            if self.key_right:
                if not self._check_node_collision(self.game, check_distance, 0):
                    self._clear_movement()
                    self.moving_right = True
            elif self.key_left:
                if not self._check_node_collision(self.game, -check_distance, 0):
                    self._clear_movement()
                    self.moving_left = True
            elif self.key_down:
                if not self._check_node_collision(self.game, 0, check_distance):
                    self._clear_movement()
                    self.moving_down = True
            elif self.key_up:
                if not self._check_node_collision(self.game, 0, -check_distance):
                    self._clear_movement()
                    self.moving_up = True

            if self._check_node_collision(self.game, (self.moving_right-self.moving_left)*check_distance, (self.moving_down-self.moving_up)*check_distance):
                self._clear_movement()

            # only move up and down if not moving left and right
            if self.moving_right and self.rect.right < self.screen_rect.right:
                self.x += 1
            if self.moving_left and self.rect.left > 0:
                self.x -= 1
            if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
                self.y += 1
            if self.moving_up and self.rect.top > 0:
                self.y -= 1

            # Update rect object from x and y
            self.rect.x = self.x
            self.rect.y = self.y
            self._check_pellet_collision(self.game)

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

    def _check_pellet_collision(self, game):
        # get a list of all pellets puckman is touching
        pellet_col_list = pygame.sprite.spritecollide(self, game.maze.pellets, False, collided=pygame.sprite.collide_rect_ratio(0.3))

        # Check the list of colliding sprites, and check if they have collisions enabled
        for pellet in pellet_col_list:
            if pellet.visible:
                # add score
                game.score += game.settings.pellet_score
                pellet.visible = False
                pellet.image = pygame.image.load('sprites/items/no_pellet.png')
                if pellet.power:
                    # activate power pellet sequence
                    game.score += game.settings.p_pellet_score
                    pellet.visible = False

    def blitme(self):
        """Draw the puckin' guy at its current location."""
        self.screen.blit(self.image, self.rect)
