class SETTINGS:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's settings."""
        # Screen settings
        self.maze_width = 28
        self.maze_height = 32
        self.screen_width = self.maze_width*8
        self.screen_height = self.maze_height*8
        self.bg_color = (0, 0, 0)

        self.pellet_score = 10
        self.p_pellet_score = 40
        self.ghost_score = 200

        # puckman should probably never move any speed besides 1
        self.puck_speed = 1.35
