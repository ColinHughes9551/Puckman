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

        # Store a decimal value for the puck's position
        self.x = self.rect.x
        self.y = self.rect.y
        # correct placement
        self.x = 104
        self.y = 184

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

        # Direction flag for animations
        self.facing_right = True
        self.facing_left = False
        self.facing_up = False
        self.facing_down = False

        # Flag for avoiding entering portal repeatedly
        self.portal_flag = False

        # variable to register subpixel movement
        self.subpixel = 0.0

    def update(self):
        self.subpixel += self.settings.puck_speed
        for i in range(math.floor(self.subpixel)):
            self.subpixel -= 1
            if self.key_right:
                if not self._check_node_collision(self.game, 1, 0):
                    self._clear_movement()
                    self._clear_facing()
                    self.facing_right = True
                    self.moving_right = True
            elif self.key_left:
                if not self._check_node_collision(self.game, -1, 0):
                    self._clear_movement()
                    self._clear_facing()
                    self.facing_left = True
                    self.moving_left = True
            elif self.key_down:
                if not self._check_node_collision(self.game, 0, 1):
                    self._clear_movement()
                    self._clear_facing()
                    self.facing_down = True
                    self.moving_down = True
            elif self.key_up:
                if not self._check_node_collision(self.game, 0, -1):
                    self._clear_movement()
                    self._clear_facing()
                    self.facing_up = True
                    self.moving_up = True

            if self._check_node_collision(self.game, (self.moving_right-self.moving_left),
                                          (self.moving_down-self.moving_up)):
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
            self._check_ghost_collision(self.game)
            self._check_portal_collision(self.game)

    def _clear_movement(self):
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def _clear_facing(self):
        self.facing_right = False
        self.facing_left = False
        self.facing_up = False
        self.facing_down = False

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
        pellet_col_list = pygame.sprite.spritecollide(self, game.maze.pellets, False,
                                                      collided=pygame.sprite.collide_rect_ratio(0.3))

        # Check the list of colliding sprites, and check if they have collisions enabled
        for pellet in pellet_col_list:
            if pellet.visible:
                # add score
                game.score += game.settings.pellet_score
                pellet.visible = False
                pellet.image = pygame.image.load('sprites/items/no_pellet.png')
                if pellet.power:
                    game.score += game.settings.p_pellet_score
                    pellet.visible = False
                    # activate power pellet sequence or reset duration
                    game.timer_power.set_time(300)
                    game.timer_power.start()
                    for ghost in self.game.ghosts:
                        if ghost.state <= 2:
                            ghost._turnaround()
                            ghost.state = 2

    def _check_ghost_collision(self, game):
        # get a list of all ghosts puckman is touching
        ghost_col_list = pygame.sprite.spritecollide(self, game.ghosts, False,
                                                     collided=pygame.sprite.collide_rect_ratio(0.5))

        # Check the list of colliding sprites, and perform actions based on state
        for ghost in ghost_col_list:
            if ghost.state <= 1:
                # fucking die
                game.score = 0
            elif ghost.state == 2:
                # eat the ghost
                ghost.state = 3
                game.timer_freeze.set_time(20)
                # gain increasingly more score as you eat ghosts
                game.score += game.settings.ghost_score * game.ghost_combo
                game.ghost_combo *= 2

    def _check_portal_collision(self, game):
        # get a list of any portals puckman is touching
        portal_col_list = pygame.sprite.spritecollide(self, game.portals, False,
                                                      collided=pygame.sprite.collide_rect_ratio(0.1))

        if not portal_col_list:
            self.portal_flag = False

        # Check the list of colliding sprites, and move puckman to the other portals location if possible
        for portal in portal_col_list:
            if not self.portal_flag:
                if portal == game.blue_portal:
                    self.x = game.org_portal.rect.x
                    self.y = game.org_portal.rect.y
                elif portal == game.org_portal:
                    self.x = game.blue_portal.rect.x
                    self.y = game.blue_portal.rect.y
                self.portal_flag = True

    def _fire_portal(self, portal_id):
        end = False
        i = 1
        x_adj = 0
        y_adj = 0
        if self.facing_up:
            y_adj = -1
        if self.facing_left:
            x_adj = -1
        if self.facing_down:
            y_adj = 1
        if self.facing_right:
            x_adj = 1
        # loop to find wall
        while not end:
            end = self._check_node_collision(self.game, x_adj*(1*i), y_adj*(1*i))
            i += 1
            if i > 1000:
                end = True
        # account for rect coordinates being in the top left by nudging portal back a bit
        if x_adj + y_adj < 0:
            i -= 2
        # move the portal to new location
        if portal_id:
            self.game.org_portal.rect.x = math.floor((self.x + x_adj*(1*i))/8)*8
            self.game.org_portal.rect.y = math.floor((self.y + y_adj*(1*i))/8)*8
            print(self.game.org_portal.rect.x, self.game.org_portal.rect.y)
        else:
            self.game.blue_portal.rect.x = math.floor((self.x + x_adj*(1*i))/8)*8
            self.game.blue_portal.rect.y = math.floor((self.y + y_adj*(1*i))/8)*8
            print(self.game.blue_portal.rect.x, self.game.blue_portal.rect.y)

    def blitme(self):
        """Draw the puckin' guy at its current location."""
        self.screen.blit(self.image, self.rect)
