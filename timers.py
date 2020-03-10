import sys
import pygame


class TIMER:
    """A class to manage timers and counters."""

    def __init__(self, puck_game, start=0, loop=False):
        """Initialize the timer and if/how it loops."""
        self.game = puck_game
        self.count = start
        self.loop = loop
        self.loop_value = start
        self.counting = 1

    def update(self):
        if self.count > 0:
            self.count -= self.counting
        elif self.count <= 0 and self.loop:
            self.count = self.loop_value

    def stop(self):
        self.counting = 0

    def start(self):
        self.counting = 1

    def set_time(self, time):
        self.count = time
