"""Contains all the code needed to create and manage a map tile."""

import pygame

from settings import *

class Tile(pygame.sprite.Sprite):
    """A tile on the world map, i.e. an obstacle."""

    def __init__(self, pos, group, sprite_type, 
                 surface=pygame.Surface((TILESIZE,TILESIZE))):
        # initialize parent Sprite class
        super().__init__(group)

        self.sprite_type = sprite_type

        # set up sprite rect
        self.image = surface

        if sprite_type == "large_object":
            # offset to account for object size
            self.rect = self.image.get_rect(topleft=(pos[0],pos[1]-TILESIZE))
        else:
            self.rect = self.image.get_rect(topleft=pos)

        # custom hit box
        self.hitbox = self.rect.inflate(0, -10)
