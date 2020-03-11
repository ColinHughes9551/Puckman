import pygame
import math
import random
from timers import TIMER


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
        self.state = 1
        # variables to delay ghosts exiting the spawn
        self.spawn_delay = 0
        self.wait = 0

        # Load the ghost image and get its rect
        self.image_eye = pygame.image.load('sprites/ghosts/eyes/u.png')
        self.imagea = pygame.image.load('sprites/ghosts/empty.png')
        self.imageb = pygame.image.load('sprites/ghosts/empty.png')
        # load all eye sprites into memory
        self.image_eyeu = pygame.image.load('sprites/ghosts/eyes/u.png')
        self.image_eyel = pygame.image.load('sprites/ghosts/eyes/l.png')
        self.image_eyed = pygame.image.load('sprites/ghosts/eyes/d.png')
        self.image_eyer = pygame.image.load('sprites/ghosts/eyes/r.png')
        self.image_eyee = pygame.image.load('sprites/ghosts/eyes/e.png')

        # sprites for blue/white mode
        self.imagef0 = pygame.image.load('sprites/ghosts/f0.png')
        self.imagef1 = pygame.image.load('sprites/ghosts/f1.png')
        self.imagef2 = pygame.image.load('sprites/ghosts/f2.png')
        self.imagef3 = pygame.image.load('sprites/ghosts/f3.png')
        self.image_empty = pygame.image.load('sprites/ghosts/empty.png')

        # set color based on behavior
        if self.behavior == 0:
            self.image0 = pygame.image.load('sprites/ghosts/r0.png')
            self.image1 = pygame.image.load('sprites/ghosts/r1.png')
        if self.behavior == 1:
            self.image0 = pygame.image.load('sprites/ghosts/p0.png')
            self.image1 = pygame.image.load('sprites/ghosts/p1.png')
        if self.behavior == 2:
            self.image0 = pygame.image.load('sprites/ghosts/b0.png')
            self.image1 = pygame.image.load('sprites/ghosts/b1.png')
        if self.behavior == 3:
            self.image0 = pygame.image.load('sprites/ghosts/o0.png')
            self.image1 = pygame.image.load('sprites/ghosts/o1.png')

        self.rect = self.image0.get_rect()

        self.timer_ani = TIMER(self, 12, True)
        self.game.timers.append(self.timer_ani)
        # Store an integer value for the ghosts position
        self.x = self.rect.x
        self.y = self.rect.y

        # behavior dependant things
        if behavior == 0:
            self.corner_x = self.settings.screen_width - 32
            self.corner_y = 0
            self.spawn_x = 104
            self.spawn_y = 88
            self.spawn_delay = 30
        if behavior == 1:
            self.corner_x = 32
            self.corner_y = 0
            self.spawn_x = 104
            self.spawn_y = 88
            self.spawn_delay = 120
        if behavior == 2:
            self.corner_x = self.settings.screen_width - 8
            self.corner_y = self.settings.screen_height
            self.spawn_x = 120
            self.spawn_y = 88
            self.spawn_delay = 240
        if behavior == 3:
            self.corner_x = 8
            self.corner_y = self.settings.screen_height
            self.spawn_x = 88
            self.spawn_y = 88
            self.spawn_delay = 320

        self.wait = self.spawn_delay
        self.x = self.spawn_x
        self.y = self.spawn_y

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

        # Flag for avoiding entering portal repeatedly
        self.portal_flag = False

        self.subpixel = 0.0

    def update(self):
        self._verify_state()
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

            if not self.wait:
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
            self._check_portal_collision(self.game)

    def _verify_state(self):
        # switch between chase and scatter when in a valid state
        if self.state <= 1:
            self.speed = 1
            if self.state != self.game.ghost_state:
                self.state = self.game.ghost_state
                self.turnaround()
        # change speed when in a different state
        if self.state == 2:
            self.speed = .5
        if self.state == 3:
            self.speed = 2
        if self.wait:
            self.wait -= 1

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

    def _check_portal_collision(self, game):
        # get a list of any portals the ghost is touching
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

    def _pathfinding(self):
        # store current intended direction to avoid turning backwards
        target_x = self.x
        target_y = self.y
        temp_up = self.key_up
        temp_left = self.key_left
        temp_down = self.key_down
        temp_right = self.key_right
        self._clear_intent()
        if self.state == 0:
            # get puckman's coordinates
            target_x = self.game.puck.rect.x
            target_y = self.game.puck.rect.y
            # refine target based on behavior
            if self.behavior == 1:
                # pinky's target is ahead of puckman
                if self.game.puck.facing_up:
                    target_y += -4*8
                    target_x += -4*8
                if self.game.puck.facing_left:
                    target_x += -4*8
                if self.game.puck.facing_down:
                    target_y += 4*8
                if self.game.puck.facing_right:
                    target_x += 4*8
            if self.behavior == 2:
                # pinky's target is ahead of puckman
                if self.game.puck.facing_up:
                    target_y += -2*8
                    target_x += -2*8
                if self.game.puck.facing_left:
                    target_x += -2*8
                if self.game.puck.facing_down:
                    target_y += 2*8
                if self.game.puck.facing_right:
                    target_x += 2*8
                # find inky's position
                temp_ghost = self
                for ghost in self.game.ghosts:
                    if ghost.behavior == 0:
                        temp_ghost = ghost
                # flip the vector pointing from inky to current target
                temp_x = temp_ghost.x - target_x
                temp_y = temp_ghost.y - target_y
                target_x -= temp_x
                target_y -= temp_y
            if self.behavior == 3:
                if self.heuristic(self.x, self.y, target_x, target_y) < 64:
                    target_x = self.corner_x
                    target_y = self.corner_y
        if self.state == 1:
            # go to your corner for scatter mode
            target_x = self.corner_x
            target_y = self.corner_y
        if self.state == 2:
            # go wherever if you're running away
            target_x = random.randint(0, self.settings.screen_width)
            target_y = random.randint(0, self.settings.screen_height)
        if self.state == 3:
            # go in front of the ghost house
            target_x = self.game.settings.screen_width/2
            target_y = (self.game.settings.screen_height/2)-40
            if math.floor(self.rect.x/4) == math.floor(target_x/4) and \
                    math.floor(self.rect.y/4) == math.floor(target_y/4):
                # revert to normal when you pass the ghost house
                self.wait = 5
                self.state = self.game.ghost_state

        # choose next direction, prioritizing up, left, down, then right, skipping directions with walls or backwards
        short_distance = 9000.1
        if not self._check_node_collision(self.game, 0, -1) and not temp_down:
            temp_distance = self.heuristic(self.x + (8 * 0), self.y + (8 * -1), target_x, target_y)
            if temp_distance < short_distance:
                short_distance = temp_distance
                self._clear_intent()
                self.key_up = True
        if not self._check_node_collision(self.game, -1, 0) and not temp_right:
            temp_distance = self.heuristic(self.x + (8 * -1), self.y + (8 * 0), target_x, target_y)
            if temp_distance < short_distance:
                short_distance = temp_distance
                self._clear_intent()
                self.key_left = True
        if not self._check_node_collision(self.game, 0, 1) and not temp_up:
            temp_distance = self.heuristic(self.x + (8 * 0), self.y + (8 * 1), target_x, target_y)
            if temp_distance < short_distance:
                short_distance = temp_distance
                self._clear_intent()
                self.key_down = True
        if not self._check_node_collision(self.game, 1, 0) and not temp_left:
            temp_distance = self.heuristic(self.x + (8 * 1), self.y + (8 * 0), target_x, target_y)
            if temp_distance < short_distance:
                self._clear_intent()
                self.key_right = True

        # turn around if in a dead end
        if self.key_up == self.key_left == self.key_down == self.key_right == 0:
            self.key_up = temp_up
            self.key_left = temp_left
            self.key_down = temp_down
            self.key_right = temp_right
            self.turnaround()

    def restart(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.wait = self.spawn_delay
        self.state = 1

    @staticmethod
    def heuristic(x1, y1, x2, y2):
        return math.sqrt(((x2 - x1)**2) + ((y2 - y1)**2))

    def turnaround(self):
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
        # correct eye direction
        if self.moving_up:
            self.image_eye = self.image_eyeu
        if self.moving_left:
            self.image_eye = self.image_eyel
        if self.moving_down:
            self.image_eye = self.image_eyed
        if self.moving_right:
            self.image_eye = self.image_eyer

        # body color
        if self.state == 2:
            # no eyes when scared
            self.image_eye = self.image_eyee
            # specify further based on time remaining in power pellet
            if self.game.timer_subpower.count:
                self.imagea = self.imagef2
                self.imageb = self.imagef3
            else:
                self.imagea = self.imagef0
                self.imageb = self.imagef1
        elif self.state == 3:
            # have no body if transparent
            self.imagea = self.image_empty
            self.imageb = self.image_empty
        else:
            self.imagea = self.image0
            self.imageb = self.image1

        if self.game.timer_1f.count > 6:
            self.screen.blit(self.imageb, self.rect)
        else:
            self.screen.blit(self.imagea, self.rect)

        self.screen.blit(self.image_eye, self.rect)
