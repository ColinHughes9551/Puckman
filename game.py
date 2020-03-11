import sys
import pygame
from settings import SETTINGS
from puckman import PUCK
from ghosts import GHOST
from maze_node import MAZE
from timers import TIMER
from portals import PORTAL
from score import SCORE
from fruit import FRUIT
from menu import MENU


class GAME:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = SETTINGS()

        self.sfx = pygame.mixer.Channel(6)
        self.music = pygame.mixer.Channel(2)

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height + 16))
        pygame.display.set_caption("Puckman!")

        # variables that exist outside of the game
        self.lives = 2
        self.lives_image = pygame.image.load('sprites/menu/life.png')
        self.score = 0
        # 0 = menu, 1 = game
        self.state = 0
        # read high score from a file
        with open('hiscore.txt') as h:
            value = [int(x) for x in h]
        self.hiscore = sum(d * 10 ** i for i, d in enumerate(value[::-1]))

        # load all sound effects and music
        self.sfx_gameover = pygame.mixer.Sound('sounds/death_1.wav')
        self.sfx_ghost = pygame.mixer.Sound('sounds/siren_1.wav')
        self.sfx_ghost_scared = pygame.mixer.Sound('sounds/power_pellet.wav')
        self.sfx_ghost_eaten = pygame.mixer.Sound('sounds/retreating.wav')
        self.sfx_intro = pygame.mixer.Sound('sounds/game_start.wav')
        self.sfx_start = pygame.mixer.Sound('sounds/credit.wav')
        self.previous_sound = 3

        # score text group
        self.score_text = pygame.sprite.Group()

        # timers and frame rate
        self.timers = []
        self.clock = pygame.time.Clock()

        # create the title screen
        self.menu = MENU(self)

        # create the font and colors used for text
        self.text = pygame.font.Font('sprites/arcade.ttf', 8)
        self.c_red = (255, 0, 0)
        self.c_white = (225, 225, 255)
        self.c_yellow = (255, 255, 0)
        self.c_black = (0, 0, 0)
        self.text_title = False
        self.text_start = False
        self.text_score = False
        self.text_gameover = False

        # create puck man
        self.puck = PUCK(self)

        # ghost stuff
        self.ghosts = pygame.sprite.Group()
        for i in range(0, 4):
            temp_ghost = GHOST(self, i)
            self.ghosts.add(temp_ghost)
        self.ghost_state = 1
        self.ghost_combo = 1

        # fruit stuff
        self.fruit_counter = 0
        self.fruit = pygame.sprite.Group()

        # maze stuff
        self.maze = MAZE(self)
        # portal stuff
        self.portals = pygame.sprite.Group()
        self.blue_portal = PORTAL(self, 0)
        self.portals.add(self.blue_portal)
        self.org_portal = PORTAL(self, 1)
        self.portals.add(self.org_portal)

        # out of game timers
        self.timer_freeze = TIMER(self, 0, False)
        self.timer_gameover = TIMER(self, 0, False)
        self.timer_gameover.stop()
        # in game timers
        self.timer_1f = TIMER(self, 1, True)
        self.timers.append(self.timer_1f)
        self.timer_scatter = TIMER(self, 420, False)
        self.timers.append(self.timer_scatter)
        self.timer_chase = TIMER(self, 1200, False)
        self.timer_chase.stop()
        self.timers.append(self.timer_chase)
        self.timer_power = TIMER(self, 0, False)
        self.timer_power.stop()
        self.timers.append(self.timer_power)
        self.timer_subpower = TIMER(self, 0, False)
        self.timers.append(self.timer_subpower)
        self.timer_fruit = TIMER(self, 1800, True)
        self.timers.append(self.timer_fruit)

    def run_game(self):
        """Start the main loop for the game."""
        self.music.play(self.sfx_intro)
        while True:
            self.timer_freeze.update()
            self.timer_gameover.update()
            self._update_text()
            if self.timer_gameover.counting and not self.timer_gameover.count:
                self._gameover()
            if self.state:
                # game loop
                self._check_events()
                if not self.timer_freeze.count:
                    self.puck.update()
                    for ghost in self.ghosts:
                        ghost.update()
                    self._ghost_sounds()
                    for fruit in self.fruit:
                        fruit.update()
                    for score in self.score_text:
                        score.update()
                    self._update_timers()
                    self.check_complete_level()
                self._update_screen()
            else:
                # menu loop
                self._check_events()
                self.menu.update_timers()
                self.menu.blitme()
            # manage frame rate
            self.clock.tick(60)

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        # Redraw the screen during each pass through the loop.
        self.screen.fill(self.settings.bg_color)
        self.maze.blitme()
        for portal in self.portals:
            portal.blitme()
        self.puck.blitme()
        if not self.timer_gameover.count:
            for fruit in self.fruit:
                fruit.blitme()
            for ghost in self.ghosts:
                ghost.blitme()
            for score in self.score_text:
                score.blitme()
        self.write_text()
        # Make the most recently drawn screen visible.
        pygame.display.flip()

    def _update_timers(self):
        for timer in self.timers:
            timer.update()
        # manage ghost state
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
        # manage fruit timer
        if self.timer_fruit.count == 0:
            # create a fruit and increment counter
            temp_fruit = FRUIT(self, self.fruit_counter)
            self.fruit.add(temp_fruit)
            if self.fruit_counter < 7:
                self.fruit_counter += 1
        # when the power pellet effect ends
        if self.timer_power.count == 0:
            self.timer_power.set_time(self.settings.power_duration)
            self.timer_power.stop()
            self.ghost_combo = 1
            # revert all frightened ghosts to normal
            for ghost in self.ghosts:
                if ghost.state == 2:
                    ghost.state = self.ghost_state
        elif self.timer_power.count < 120 and self.timer_power.count % 24 == 0:
            self.timer_subpower.set_time(12)

    def create_score(self, x, y, value):
        # global call to create a score sprite
        temp_score = SCORE(self, x, y, value)
        self.score_text.add(temp_score)

    def check_complete_level(self):
        if self.maze.all_pellets_invisible():
            # play a song here probably
            self.restart_game()
            self.maze.refresh_pellets()
            self.timer_freeze.set_time(30)

    def restart_game(self):
        self.puck.restart()
        self.previous_sound = 3
        for ghost in self.ghosts:
            ghost.restart()
        self.timer_scatter.set_time(300)
        self.timer_scatter.start()
        self.timer_chase.set_time(1200)
        self.timer_chase.stop()
        self.timer_fruit.set_time(1800)
        for fruit in self.fruit:
            fruit.life = 0
        for portal in self.portals:
            if portal.id:
                portal.rect.x = self.settings.screen_width - 24
            else:
                portal.rect.x = 8
            portal.rect.y = 112
        self.puck.key_right = False
        self.puck.key_left = False
        self.puck.key_down = False
        self.puck.key_up = False

    def _check_events(self):
        # Watch for keyboard and mouse events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not self.state:
                    self._press_anything(event)
                else:
                    self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                if self.state:
                    self._check_keyup_events(event)

    def _press_anything(self, event):
        if event.key == pygame.K_q:
            self._quit_game()
        elif event.type == pygame.KEYDOWN:
            # let us begin the game
            self.music.stop()
            self.sfx.play(self.sfx_start)
            self.state = 1

    def _check_keydown_events(self, event):
        """Respond to key presses."""
        if not self.timer_freeze.count:
            if event.key == pygame.K_z:
                # fire blue portal
                self.puck.fire_portal(0)
            elif event.key == pygame.K_x:
                # fire orange portal
                self.puck.fire_portal(1)
        if event.key == pygame.K_RIGHT:
            self.puck.key_right = True
        elif event.key == pygame.K_LEFT:
            self.puck.key_left = True
        elif event.key == pygame.K_DOWN:
            self.puck.key_down = True
        elif event.key == pygame.K_UP:
            self.puck.key_up = True
        elif event.key == pygame.K_q:
            self._quit_game()

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

    def _ghost_sounds(self):
        current_sound = 0
        for ghost in self.ghosts:
            if ghost.state > current_sound:
                current_sound = ghost.state
        if current_sound == 3 and self.previous_sound !=3:
            self.music.play(self.sfx_ghost_eaten, -1)
        if current_sound == 2 and self.previous_sound !=2:
            self.music.play(self.sfx_ghost_scared, -1)
        if current_sound <= 1 and self.previous_sound > 1:
            self.music.play(self.sfx_ghost, -1)
        self.previous_sound = current_sound

    def kill_puck(self):
        self.music.play(self.sfx_gameover)
        self.timer_freeze.set_time(140)
        self.timer_gameover.set_time(140)
        self.timer_gameover.start()

    def _gameover(self):
        self.timer_gameover.stop()
        if self.lives == -1:
            self._check_score()
            self.restart_game()
            self.maze.refresh_pellets()
            self.fruit_counter = 0
            self.lives = 2
            self.state = 0
            # start intro music again
            self.music.play(self.sfx_intro)
        elif self.lives == 0:
            # freeze the screen for another second
            self.timer_freeze.set_time(40)
            self.timer_gameover.set_time(40)
            self.timer_gameover.start()
            self.lives = -1
        else:
            self.lives -= 1
            self.restart_game()

    def _quit_game(self):
        # write over hiscore if needed and quit game
        self._check_score()
        sys.exit()

    def _check_score(self):
        if self.score > self.hiscore:
            self.hiscore = self.score
            with open('hiscore.txt', 'w') as f:
                f.write('%d' % self.score)
        self.score = 0

    def write_text(self):
        if self.text_title:
            text_start = self.text.render("Z - BLUE PORTAL", False, self.c_white, self.c_black)
            self.screen.blit(text_start, (self.settings.screen_width / 2 - text_start.get_width() / 2,
                                          self.settings.screen_height - text_start.get_height() / 2 - 48))
            text_start = self.text.render("X - ORANGE PORTAL", False, self.c_white, self.c_black)
            self.screen.blit(text_start, (self.settings.screen_width / 2 - text_start.get_width() / 2,
                                          self.settings.screen_height - text_start.get_height() / 2 - 32))
            # HISCORE display
            text_score = self.text.render(str(self.hiscore), False, self.c_white, self.c_black)
            self.screen.blit(text_score,
                             (self.settings.screen_width/2 - text_score.get_width()/2, 8))

            # PUCKMAN! display
            text_start = self.text.render("PUCKMAN!", False, self.c_yellow, self.c_black)
            self.screen.blit(text_start, (self.settings.screen_width / 2 - text_start.get_width() / 2,
                                          self.settings.screen_height/2 - text_start.get_height() / 2 + 40))

        if self.text_start:
            text_start = self.text.render("PRESS ANY KEY TO START", False, self.c_white, self.c_black)
            self.screen.blit(text_start, (self.settings.screen_width / 2 - text_start.get_width() / 2,
                                          self.settings.screen_height - text_start.get_height() / 2 - 8))
        if self.text_score:
            # LIVES display
            for i in range(self.lives):
                self.screen.blit(self.lives_image, (2 + i*13, self.settings.screen_height))

            # SCORE display
            text_score = self.text.render("SCORE", False, self.c_white, self.c_black)
            self.screen.blit(text_score, (32, self.settings.screen_height))
            text_score = self.text.render(str(self.score), False, self.c_white, self.c_black)
            self.screen.blit(text_score, (114 - text_score.get_width(), self.settings.screen_height))

            # HISCORE display
            text_score = self.text.render("HISCORE", False, self.c_white, self.c_black)
            self.screen.blit(text_score, (120, self.settings.screen_height))
            text_score = self.text.render(str(self.hiscore), False, self.c_white, self.c_black)
            self.screen.blit(text_score,
                             (self.settings.screen_width - text_score.get_width(), self.settings.screen_height))

        if self.text_gameover:
            text_gameover = self.text.render("GAME OVER", False, self.c_red, self.c_black)
            self.screen.blit(text_gameover, (self.settings.screen_width / 2 - text_gameover.get_width() / 2,
                                             self.settings.screen_height / 2 - text_gameover.get_height() / 2 + 16))

    def _update_text(self):
        self.text_title = False
        self.text_start = False
        self.text_score = False
        self.text_gameover = False

        if self.state:
            self.text_score = True
        else:
            self.text_title = True
            self.text_start = True
        if self.lives == -1:
            self.text_gameover = True


if __name__ == '__main__':
    # Make a game instance, and run the game.
    game = GAME()
    game.run_game()
