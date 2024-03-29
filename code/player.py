"""Contains all code needed to create and manage the player."""

import pygame

from settings import *
from support import import_folder
from entity import Entity

class Player(Entity):
    """The player avatar."""

    def __init__(self, pos, group, obstacle_sprites, create_weapon, destroy_weapon,
                 create_spell, destroy_spell):
        # initialize parent Sprite class
        super().__init__(group)

        # graphics setup
        self.import_player_assets()

        self.image = pygame.image.load("../graphics/player/down_idle/idle_down.png")
        self.image.convert_alpha()

        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET["player"])

        # player state
        self.status = "down"

        # attack
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        # weapon
        self.create_weapon = create_weapon
        self.destroy_weapon = destroy_weapon
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        # magic
        self.create_spell = create_spell
        self.destroy_spell = destroy_spell
        self.spell_index = 0
        self.spell = list(magic_data.keys())[self.spell_index]
        self.can_switch_spell = True
        self.spell_switch_time = None

        # an easy reference to obstacles
        self.obstacle_sprites = obstacle_sprites

        # player stats
        self.stats = { "health": 100, "energy": 60, "attack": 10, "magic": 4, "speed": 5 }
        self.max_stats = { "health": 300, "energy": 140, "attack": 20, "magic": 10, "speed": 10 }
        self.upgrade_cost = { "health": 100, "energy": 100, "attack": 100, "magic": 100, "speed": 100 }

        self.speed = self.stats["speed"]
        self.health = self.stats["health"]
        self.energy = self.stats["energy"]
        self.exp = 500

        # damage / vulnerability timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # import sound
        self.weapon_attack_sound = pygame.mixer.Sound("../audio/sword.wav")
        self.weapon_attack_sound.set_volume(0.4)

    def import_player_assets(self):
        """Load in all assets related to the player"""

        character_path = "../graphics/player"
        self.animations = {
            "right": [],
            "left": [],
            "up": [],
            "down": [],
            "right_idle": [],
            "left_idle": [],
            "up_idle": [],
            "down_idle": [],
            "right_attack": [],
            "left_attack": [],
            "up_attack": [],
            "down_attack": [],
        }

        for animation in self.animations.keys():
            full_path = f"{character_path}/{animation}"
            self.animations[animation] = import_folder(full_path)

    def input(self):
        """Collect and process input from the player."""
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # movement input
            # vertical movement
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = "up"
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = "down"
            else:
                self.direction.y = 0
            # horizontal movement
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = "right"
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = "left"
            else:
                self.direction.x = 0

            # atack input
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()

                self.create_weapon()
                self.weapon_attack_sound.play()

            # magic input
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()

                self.create_spell(
                    self.spell,
                    magic_data[self.spell]["strength"] + self.stats["magic"],
                    magic_data[self.spell]["cost"],
                )

            # select weapon
            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                if self.weapon_index < len(list(weapon_data.keys())) - 1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                self.weapon = list(weapon_data.keys())[self.weapon_index]

            # select spell
            if keys[pygame.K_e] and self.can_switch_spell:
                self.can_switch_spell = False
                self.spell_switch_time = pygame.time.get_ticks()
                if self.spell_index < len(list(magic_data.keys())) - 1:
                    self.spell_index += 1
                else:
                    self.spell_index = 0
                self.spell = list(magic_data.keys())[self.spell_index]

    def set_status(self):
        """Get the current player status based on player input."""

        # idle status
        if (self.direction.x, self.direction.y) == (0, 0):
            if not "_idle" in self.status and not "_attack" in self.status:
                self.status += "_idle"

        # attacking
        if self.attacking:
            # do not allow player to move while attacking
            self.direction.x = 0
            self.direction.y = 0

            if not "_attack" in self.status:
                if "_idle" in self.status:
                    # overwrite _idle
                    self.status = self.status.replace("_idle", "_attack")
                else:
                    self.status += "_attack"
        # attack finished
        else:
            if "_attack" in self.status:
                self.status = self.status.replace("_attack", "")

    def cooldowns(self):
        """Manage player cooldowns with a custom timer."""

        current_time = pygame.time.get_ticks()

        # attack cooldown
        if self.attacking:
            if ((current_time - self.attack_time) 
            >= (self.attack_cooldown + weapon_data[self.weapon]["cooldown"])):
                self.attacking = False
                self.destroy_weapon()

        # weapon switch cooldown
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        # spell switch cooldown
        if not self.can_switch_spell:
            if current_time - self.spell_switch_time >= self.switch_duration_cooldown:
                self.can_switch_spell = True

        # vulnerability timer
        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def get_full_weapon_dmg(self):
        """Calculate the full damage the player can deal with their weapon."""

        base_damage = self.stats["attack"]
        weapon_damage = weapon_data[self.weapon]["damage"]

        return base_damage + weapon_damage

    def get_full_spell_dmg(self):
        """Calculate the full damage the player can deal with their spell."""

        base_damage = self.stats["magic"]
        spell_damage = magic_data[self.spell]["strength"]

        return base_damage + spell_damage

    def recover_energy(self):
        """Increase the player's energy level."""

        if self.energy < self.stats["energy"]:
            self.energy += (0.01 * self.stats["magic"])
        else:
            self.energy = self.stats["energy"]

    def animate(self):
        """Manage the player animation."""

        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        # flicker when hit
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_value_by_index(self, index):
        """Get a stat's value by a given index."""

        return list(self.stats.values())[index]

    def get_cost_by_index(self, index):
        """Get a stat's cost by a given index."""

        return list(self.upgrade_cost.values())[index]

    def update(self):
        """Collect input and update the player position."""

        self.input()
        self.cooldowns()
        self.set_status()
        self.animate()
        self.move(self.stats["speed"])
        self.recover_energy()
