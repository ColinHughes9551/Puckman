import pygame
import math

class GHOST(pygame.sprite.Sprite):
    """A class to manage the ghosts."""

    def __init__(self, puck_game, behavior):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        """Initialize the puck and set its starting position."""
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings
        # have a personal speed value in case it needs to change
        self.speed = 1.33
        # 0 = red, 1 = pink, 2 = blue, 3 = orange
        self.behavior = behavior
        # 0 = chase, 1 = scatter, 2 = blue, 3 = dead
        self.state = 0

        # Load the ghost image and get its rect
        self.image = pygame.image.load('sprites/ghosts/ghost_test.png')
        self.rect = self.image.get_rect()
        # Start ghost at starting location
        self.rect.center = self.screen_rect.center

        # Store a decimal value for the puck's horizontal position.
        self.x = self.rect.x
        self.y = self.rect.y
        # correct placement
        self.y -= 32

        # Key flag, repurposed to show intended direction
        self.key_right = False
        self.key_left = False
        self.key_up = False
        self.key_down = False

        # Movement flag
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

        self.subpixel = 0.0

    def update(self):
        self.subpixel += self.speed
        for i in range(math.floor(self.subpixel)):
            self.subpixel -= 1
            # determine key direction
            if self.x % 8 == 0 and self.y % 8 == 0:
                self._pathfinding()

            # change movement based on key direction
            if self.key_right:
                if not self._check_node_collision(self.game, 1, 0):
                    self._clear_movement()
                    self.moving_right = True
            elif self.key_left:
                if not self._check_node_collision(self.game, -1, 0):
                    self._clear_movement()
                    self.moving_left = True
            elif self.key_down:
                if not self._check_node_collision(self.game, 0, 1):
                    self._clear_movement()
                    self.moving_down = True
            elif self.key_up:
                if not self._check_node_collision(self.game, 0, -1):
                    self._clear_movement()
                    self.moving_up = True

            if self._check_node_collision(self.game, (self.moving_right - self.moving_left),
                                          (self.moving_down - self.moving_up)):
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

    def _clear_intent(self):
        self.key_right = False
        self.key_left = False
        self.key_up = False
        self.key_down = False

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

    def _check_graph_collision(self, game):
        # get a list of all pellets puckman is touching
        graph_col_list = pygame.sprite.spritecollide(self, game.maze.graph, False, collided=pygame.sprite.collide_rect_ratio(0.3))
        # Check the list of colliding sprites, and check if they have collisions enabled
        for graph in graph_col_list:
            return True
        return False

    def _pathfinding(self):
        # get puckman's coordinates
        target_x = self.game.puck.rect.x
        target_y = self.game.puck.rect.y
        # store current intended direction to avoid turning backwards
        temp_up = self.key_up
        temp_left = self.key_left
        temp_down = self.key_down
        temp_right = self.key_right
        self._clear_intent()
        # refine target based on behavior

        # choose next direction, prioritizing up, left, down, then right, skipping directions with walls or backwards
        temp_distance = 0.0
        short_distance = 9000.1
        if not self._check_node_collision(self.game, 0, -1) and not temp_down:
            temp_distance = self.heuristic(self.rect.x + (8 * 0), self.rect.y + (8 * -1), target_x, target_y)
            if temp_distance < short_distance:
                short_distance = temp_distance
                self._clear_intent()
                self.key_up = True
        if not self._check_node_collision(self.game, -1, 0) and not temp_right:
            temp_distance = self.heuristic(self.rect.x + (8 * -1), self.rect.y + (8 * 0), target_x, target_y)
            if temp_distance < short_distance:
                short_distance = temp_distance
                self._clear_intent()
                self.key_left = True
        if not self._check_node_collision(self.game, 0, 1) and not temp_up:
            temp_distance = self.heuristic(self.rect.x + (8 * 0), self.rect.y + (8 * 1), target_x, target_y)
            if temp_distance < short_distance:
                short_distance = temp_distance
                self._clear_intent()
                self.key_down = True
        if not self._check_node_collision(self.game, 1, 0) and not temp_left:
            temp_distance = self.heuristic(self.rect.x + (8 * 1), self.rect.y + (8 * 0), target_x, target_y)
            if temp_distance < short_distance:
                self._clear_intent()
                self.key_right = True

        # turn around if in a dead end
        if self.key_up == self.key_left == self.key_down == self.key_right == 0:
            self.key_up = temp_up
            self.key_left = temp_left
            self.key_down = temp_down
            self.key_right = temp_right
            self._turnaround()

    def heuristic(self, x1, y1, x2, y2):
        return math.sqrt( ((x2 - x1)**2) + ((y2 - y1)**2) )

    def _turnaround(self):
        # invert intended direction
        if self.key_up or self.key_down:
            temp = self.key_up
            self.key_up = self.key_down
            self.key_down = temp
        if self.key_left or self.key_right:
            temp = self.key_left
            self.key_left = self.key_right
            self.key_right = temp

    def blitme(self):
        """Draw the puckin' guy at its current location."""
        self.screen.blit(self.image, self.rect)
