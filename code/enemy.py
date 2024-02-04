"""Contains all code needed to create and manage an enemy."""


import pygame

from settings import *
from support import *
from entity import Entity


class Enemy(Entity):
    """An enemy in the game."""

    def __init__(self, monster_name, pos, groups, obstacle_sprites):
        super().__init__(groups)

        # general setup
        self.sprite_type = "enemy"

        # graphics setup
        self.import_graphics(monster_name)
        self.status = "idle"
        self.image = self.animations[self.status][self.frame_index]

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # stats
        self.monster_name = monster_name

        monster_info = monster_data[self.monster_name]
        self.health = monster_info["health"]
        self.exp = monster_info["exp"]
        self.speed = monster_info["speed"]
        self.damage = monster_info["damage"]
        self.resistance = monster_info["resistance"]
        self.attack_radius = monster_info["attack_radius"]
        self.notice_radius = monster_info["notice_radius"]
        self.attack_type = monster_info["attack_type"]

        # player interaction
        self.can_attack = True
        self.atack_time = None
        self.attack_cooldown = 400

    def import_graphics(self, name):
        """Import the graphics for an enemy."""

        self.animations = {"idle": [], "move": [], "attack": []}

        main_path = f"../graphics/monsters/{name}"
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(f"{main_path}/{animation}")

    def get_player_distance_direction(self, player):
        """Return the distance from the player and the direction towards them."""

        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)

        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def set_status(self, player):
        """Set the enemy status."""

        distance, _ = self.get_player_distance_direction(player)

        if distance <= self.attack_radius and self.can_attack:
            if self.status != "attack":
                self.frame_index = 0
            self.status = "attack"
        elif distance <= self.notice_radius:
            self.status = "move"
        else:
            self.status = "idle"

    def perform_action(self, player):
        """Perform an action depending on the current status."""

        if self.status == "attack":
            self.attack_time = pygame.time.get_ticks()
        elif self.status == "move":
            self.direction = self.get_player_distance_direction(player)[1]
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        """Manage the enemy animation."""

        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == "attack":
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def cooldowns(self):
        """Manage enemy cooldowns with a custom timer."""

        if not self.can_attack:
            current_time = pygame.time.get_ticks()

            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

    def update(self):
        """Update the sprite on the screen."""

        self.move(self.speed)
        self.animate()

    def enemy_update(self, player):
        """Update the sprite on the screen (enemy specific)."""

        self.set_status(player)
        self.perform_action(player)
        self.cooldowns()
