"""Contains the code needed to create and manage an entity, i.e. the
player or an enemy.
"""

from math import sin

import pygame


class Entity(pygame.sprite.Sprite):
    """A being in the game world."""

    def __init__(self, groups):
        super().__init__(groups)

        # animations
        self.frame_index = 0
        self.animation_speed = 0.15

        # movement 
        self.direction = pygame.math.Vector2()

    def check_collision(self, direction):
        """Check if the entity has collided with an obstacle. If so, update
        the entity position.
        """

        if direction == "horizontal":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == "vertical":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def move(self, speed):
        """Move the entity, checking for collisions along the way."""

        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # move and check collisions on hitbox first
        self.hitbox.x += self.direction.x * speed
        self.check_collision("horizontal")

        self.hitbox.y += self.direction.y * speed
        self.check_collision("vertical")

        # move sprite to new hitbox location
        self.rect.center = self.hitbox.center

    def wave_value(self):
        """Use a sign wave to toggle between 255 and 0."""

        return 255 if sin(pygame.time.get_ticks()) >= 0 else 0
