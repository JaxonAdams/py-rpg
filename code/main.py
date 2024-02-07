"""Main python script. Contains the "Game" class, which runs the game."""


import sys

import pygame

from settings import *
from level import Level


class Game:
    """A running instance of our game."""

    def __init__(self):
        """Initialize a new Game object."""

        # general setup
        pygame.init() # initialize pygame

        # set up display window
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PyRPG")

        # set up clock for steady fps
        self.clock = pygame.time.Clock()

        # initialize a new level
        self.level = Level()

    def run(self):
        """Run the game. Set up a game loop and an event listener."""

        # event loop
        while True:
            # get events
            for event in pygame.event.get():
                # if player quit, stop the program
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()
                
            # fill in screen
            self.screen.fill("black")
            # call the current level's run method
            self.level.run()
            # update screen
            pygame.display.update()
            # update clock
            self.clock.tick(FPS)


# !---------------------------------------------------------------------------
if __name__ == "__main__":
    game = Game()
    game.run()
