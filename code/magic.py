"""Contains all code needed to create and manage a spell."""


import random

import pygame

from settings import *


class MagicPlayer:
    """A spell / magic manager."""
    
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def heal(self, player, strength, cost, groups):
        """A spell which heals the player."""
        
        if player.energy >= cost:
            player.health += strength
            player.energy -= cost
            
            if player.health >= player.stats["health"]:
                player.health = player.stats["health"]
            
            self.animation_player.create_particles(
                "aura",
                player.rect.center,
                groups,
            )
            self.animation_player.create_particles(
                "heal",
                player.rect.center + pygame.math.Vector2(0, -60),
                groups,
            )

    def flame(self, player, cost, groups):
        """A fire spell which damages enemies."""
        
        if player.energy >= cost:
            player.energy -= cost

            player_direction = player.status.split("_")[0]
            if player_direction == "right":
                direction = pygame.math.Vector2(1, 0)
            elif player_direction == "left":
                direction = pygame.math.Vector2(-1, 0)
            elif player_direction == "up":
                direction = pygame.math.Vector2(0, -1)
            else:
                direction = pygame.math.Vector2(0, 1)

            for i in range(1, 6):
                if direction.x: # horizontal
                    offset_x = (direction.x * i) * TILESIZE
                    x = player.rect.centerx + offset_x + random.randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + random.randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles("flame", (x, y), groups)
                else: # vertical
                    offset_y = (direction.y * i) * TILESIZE
                    x = player.rect.centerx + random.randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + random.randint(-TILESIZE // 3, TILESIZE // 3)
                    self.animation_player.create_particles("flame", (x, y), groups)
