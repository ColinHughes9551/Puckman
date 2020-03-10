import sys
import pygame
from settings import SETTINGS
from puckman import PUCK
from ghosts import GHOST
from maze_node import MAZE
from timers import TIMER
from portals import PORTAL


class GAME:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = SETTINGS()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height + 16))
        pygame.display.set_caption("Puckman!")

        self.lives = 2
        self.score = 0

        self.puck = PUCK(self)

        # ghost stuff
        self.ghosts = pygame.sprite.Group()
        for i in range(0, 4):
            temp_ghost = GHOST(self, i)
            self.ghosts.add(temp_ghost)
        self.ghost_state = 1
        self.ghost_combo = 1
        # maze stuff
        self.maze = MAZE(self)
        # portal stuff
        self.portals = pygame.sprite.Group()
        self.blue_portal = PORTAL(self, 0)
        self.portals.add(self.blue_portal)
        self.org_portal = PORTAL(self, 1)
        self.portals.add(self.org_portal)
        # timers and frame rate
        self.timers = []
        self.create_timers()
        self.clock = pygame.time.Clock()

    def create_timers(self):
        self.timer_freeze = TIMER(self, 0, False)
        self.timer_5f = TIMER(self, 5, True)
        self.timers.append(self.timer_5f)
        self.timer_10f = TIMER(self, 10, True)
        self.timers.append(self.timer_10f)
        self.timer_20f = TIMER(self, 20, True)
        self.timers.append(self.timer_20f)
        self.timer_30f = TIMER(self, 30, True)
        self.timers.append(self.timer_30f)
        self.timer_scatter = TIMER(self, 420, False)
        self.timers.append(self.timer_scatter)
        self.timer_chase = TIMER(self, 1200, False)
        self.timer_chase.stop()
        self.timers.append(self.timer_chase)
        self.timer_power = TIMER(self, 300, False)
        self.timer_power.stop()
        self.timers.append(self.timer_power)

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self.timer_freeze.update()
            if not self.timer_freeze.count:
                self._check_events()
                self.puck.update()
                for ghost in self.ghosts:
                    ghost.update()
                self._update_timers()
                self._update_screen()
            self.clock.tick_busy_loop(60)

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color)
        self.maze.blitme()
        for portal in self.portals:
            portal.blitme()
        self.puck.blitme()
        for ghost in self.ghosts:
            ghost.blitme()
        # Make the most recently drawn screen visible.
        pygame.display.flip()

    def _update_timers(self):
        for timer in self.timers:
            timer.update()
        # manage general game timers
        if self.timer_scatter.count == 0:
            self.timer_scatter.set_time(300)
            self.timer_scatter.stop()
            self.timer_chase.start()
            self.ghost_state = 0
        if self.timer_chase.count == 0:
            self.timer_chase.set_time(1200)
            self.timer_chase.stop()
            self.timer_scatter.start()
            self.ghost_state = 1
        # when the power pellet effect ends
        if self.timer_power.count == 0:
            self.timer_power.set_time(300)
            self.timer_power.stop()
            self.ghost_combo = 1
            # revert all frightened ghosts to normal
            for ghost in self.ghosts:
                if ghost.state == 2:
                    ghost.state = self.ghost_state

    def _check_events(self):
        # Watch for keyboard and mouse events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """Respond to key presses."""
        if event.key == pygame.K_RIGHT:
            self.puck.key_right = True
        elif event.key == pygame.K_LEFT:
            self.puck.key_left = True
        elif event.key == pygame.K_DOWN:
            self.puck.key_down = True
        elif event.key == pygame.K_UP:
            self.puck.key_up = True
        elif event.key == pygame.K_z:
            # fire blue portal
            self.puck._fire_portal(0)
        elif event.key == pygame.K_x:
            # fire orange portal
            self.puck._fire_portal(1)
        elif event.key == pygame.K_q:
            # display score on quit
            print("SCORE:", self.score)
            sys.exit()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.puck.key_right = False
        elif event.key == pygame.K_LEFT:
            self.puck.key_left = False
        elif event.key == pygame.K_DOWN:
            self.puck.key_down = False
        elif event.key == pygame.K_UP:
            self.puck.key_up = False


if __name__ == '__main__':
    # Make a game instance, and run the game.
    game = GAME()
    game.run_game()
