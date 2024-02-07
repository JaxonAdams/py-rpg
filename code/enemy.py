"""Contains all code needed to create and manage an enemy."""


import pygame

from settings import *
from support import *
from entity import Entity


class Enemy(Entity):
    """An enemy in the game."""

    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, award_xp):
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
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.award_xp = award_xp

        # invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

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
            self.damage_player(self.damage, self.attack_type)
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

        # logic for flickering image when hit
        if not self.vulnerable:
            alpha = self.wave_value()

            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        """Manage enemy cooldowns with a custom timer."""

        current_time = pygame.time.get_ticks()

        if not self.can_attack:

            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player, attack_type):
        """Get the number of hit points which should be taken from the enemy
        when it is hit by an attack.
        """

        if not self.vulnerable:
            return
        
        self.direction = self.get_player_distance_direction(player)[1]

        if attack_type == "weapon":
            self.health -= player.get_full_weapon_dmg()
        else: # magic damage
            self.health -= player.get_full_spell_dmg()

        self.hit_time = pygame.time.get_ticks()
        self.vulnerable = False

    def check_death(self):
        """Check if a death should occur; i.e. health is less than zero."""

        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.award_xp(self.exp)

    def hit_reaction(self):
        """If just attacked, get knocked back."""

        if not self.vulnerable:
            self.direction *= -self.resistance

    def update(self):
        """Update the sprite on the screen."""

        self.move(self.speed)
        self.animate()

    def enemy_update(self, player):
        """Update the sprite on the screen (enemy specific)."""

        self.set_status(player)
        self.perform_action(player)
        self.cooldowns()
        self.hit_reaction()
        self.check_death()
