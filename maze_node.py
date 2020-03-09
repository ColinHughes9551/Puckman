import sys
import pygame


class NODE(pygame.sprite.Sprite):
    """A class to manage nodes on the map."""

    def __init__(self, puck_game, x, y, ch):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        """Initialize the puck and set its starting position."""
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings

        self.collision = False
        self.portal = False

        if ch == 'x':
            self.collision = True

        if self.collision:
            self.image = pygame.image.load('sprites/tiles/square.png')
        else:
            self.image = pygame.image.load('sprites/tiles/open.png')
        self.rect = self.image.get_rect()

        # Update rect object from given x and y
        self.rect.x = x
        self.rect.y = y

    def __repr__(self):
        if self.collision:
            return "X"
        elif self.portal:
            return "O"
        else:
            return "-"


class GRAPH(pygame.sprite.Sprite):
    """A class to manage graph nodes on the map."""

    def __init__(self, puck_game, x, y):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        """Initialize the puck and set its starting position."""
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings

        # flags that hold cost of each direction, with -1 meaning no valid path
        self.up = -1
        self.down = -1
        self.left = -1
        self.right = -1

        self.image = pygame.image.load('sprites/tiles/graph.png')
        self.rect = self.image.get_rect()

        # Update rect object from given x and y
        self.rect.x = x
        self.rect.y = y

    def generate_costs(self, maze):
        self.up = self._costs(maze, 0, -1)
        self.down = self._costs(maze, 0, 1)
        self.left = self._costs(maze, -1, 0)
        self.right = self._costs(maze, 1, 0)
        # test values
        print(self.up, self.down, self.left, self.right)

    def _costs(self, maze, x_dir=0, y_dir=0):
        # save position
        temp_x = self.rect.x
        temp_y = self.rect.y
        cost = 0
        _exit = False
        while not _exit:
            cost += 1
            # adjust position
            self.rect.x = temp_x + 8*cost*x_dir
            self.rect.y = temp_y + 8*cost*y_dir

            # get a list of all nodes the graph collides with
            node_col_list = pygame.sprite.spritecollide(self, maze.nodes, False)
            graph_col_list = pygame.sprite.spritecollide(self, maze.graph, False)

            # Check the list of colliding sprites, and check if they have collisions enabled
            for graph in graph_col_list:
                if graph != self:
                    _exit = True
            if not _exit:
                for node in node_col_list:
                    if node.collision:
                        cost = -1
                        _exit = True

        # return to previous position
        self.rect.x = temp_x
        self.rect.y = temp_y

        # return calculated cost
        return cost


class PELLET(pygame.sprite.Sprite):
    """A class to manage pellets on the map."""

    def __init__(self, puck_game, x, y, power):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        """Initialize the puck and set its starting position."""
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings

        self.visible = True
        self.power = power
        if self.power:
            self.image = pygame.image.load('sprites/items/p_pellet.png')
        else:
            self.image = pygame.image.load('sprites/items/pellet.png')
        self.rect = self.image.get_rect()

        # Update rect object from given x and y
        self.rect.x = x
        self.rect.y = y


class MAZE:
    def __init__(self, puck_game):
        self.game = puck_game
        self.screen = puck_game.screen
        self.screen_rect = puck_game.screen.get_rect()
        self.settings = puck_game.settings

        # create array of nodes
        self.maze_text = open("maze.txt", "r")
        self.nodes = pygame.sprite.Group()
        self.pellets = pygame.sprite.Group()
        self.graph = pygame.sprite.Group()
        with open("maze.txt") as maze_text:
            w = 0
            h = 0
            for line in maze_text:
                for ch in line:
                    temp_node = NODE(self.game, w*8, h*8, ch)
                    self.nodes.add(temp_node)
                    if ch == 'p':
                        temp_pellet = PELLET(self.game, (w*8+7), (h*8+7), False)
                        self.pellets.add(temp_pellet)
                    if ch == 'P':
                        temp_pellet = PELLET(self.game, (w*8+4), (h*8+4), True)
                        self.pellets.add(temp_pellet)
                    if ch == 'g':
                        temp_graph = GRAPH(self.game, (w*8-4), (h*8-4))
                        self.graph.add(temp_graph)
                    if ch == 'G':
                        # exception case for when pellet and intersection overlap
                        temp_pellet = PELLET(self.game, (w*8+7), (h*8+7), False)
                        self.pellets.add(temp_pellet)
                        temp_graph = GRAPH(self.game, (w*8-4), (h*8-4))
                        self.graph.add(temp_graph)
                    w += 1
                h += 1
                w = 0
        # generate the costs for all graph nodes
        for graph in self.graph:
            graph.generate_costs(self)

    def update_pellets(self):
        # reassigns sprites to all pellets, use when resetting level
        for pellet in self.pellets:
            if pellet.visible:
                if pellet.power:
                    pellet.image = pygame.image.load('sprites/items/p_pellet.png')
                else:
                    pellet.image = pygame.image.load('sprites/items/pellet.png')
            else:
                pellet.image = pygame.image.load('sprites/items/no_pellet.png')

    def all_pellets_invisible(self):
        # check if ANY pellets are visible
        for pellet in self.pellets:
            if pellet.visible:
                return False
        return True

    def blitme(self):
        self.nodes.draw(self.screen)
        self.graph.draw(self.screen)
        self.pellets.draw(self.screen)
        """Draw the maze based on current nodes
        for w in range(self.settings.maze_width):
            for h in range(self.settings.maze_height):
                self.screen.blit(self.open, [w*8, h*8])"""