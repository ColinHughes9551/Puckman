import sys
import pygame
from settings import SETTINGS
from puckman import PUCK
from maze_node import NODE
from maze_node import MAZE


class GAME:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = SETTINGS()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Puckman!")

        self.lives = 2
        self.score = 0

        self.puck = PUCK(self)
        self.maze = MAZE(self)
        self.clock = pygame.time.Clock()
        # self.bullets = pygame.sprite.Group()

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            self.puck.update()
            self._update_screen()
            self.clock.tick_busy_loop(60)

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color)
        self.maze.blitme()
        self.puck.blitme()
        # Make the most recently drawn screen visible.
        pygame.display.flip()

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
