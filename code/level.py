"""Code needed to build and manage a level in the game. Contains the following:

Level: A level in the game, including all sprites and logic to run the level
YSortCameraGroup: A sprite group with custom functions for a better camera
"""

import random

import pygame

from settings import *
from support import *
from tile import Tile
from player import Player
from enemy import Enemy
from weapon import Weapon
from ui import UI
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import UpgradeMenu

class Level:
    """A level in the game."""
    
    def __init__(self):
        # get display surface
        self.display_surface = pygame.display.get_surface()

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # draw all sprites in map
        self.create_map()

        # user interface
        self.ui = UI()
        self.upgrade_menu = UpgradeMenu(self.player)
        self.game_paused = False

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def create_map(self):
        """Create the level map."""
        
        layouts = {
            "boundary": import_csv_layout("../map/map_FloorBlocks.csv"),
            "grass": import_csv_layout("../map/map_Grass.csv"),
            "large_object": import_csv_layout("../map/map_LargeObjects.csv"),
            "entities": import_csv_layout("../map/map_Entities.csv"),
        }

        graphics = {
            "grass": import_folder("../graphics/Grass"),
            "large_objects": import_folder("../graphics/objects"),
        }

        # iterate through each item in 2D list making up the world map
        for style, layout in layouts.items():
            for row_i, row in enumerate(layout):
                for col_i, col in enumerate(row):
                    # set position for current sprite
                    if col != "-1":
                        x = col_i * TILESIZE
                        y = row_i * TILESIZE
                        if style == "boundary":
                            Tile((x, y), [self.obstacle_sprites], "invisible")
                        if style == "grass":
                            grass_img = random.choice(graphics["grass"])

                            Tile(
                                (x, y),
                                [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 
                                "grass",
                                grass_img
                            )
                        if style == "large_object":
                            obj_img = graphics["large_objects"][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 
                                 "large_object", obj_img)
                        if style == "entities":
                            if col == "394": # player
                                self.player = Player((x, y), [self.visible_sprites],
                                                    self.obstacle_sprites, self.create_weapon,
                                                    self.destroy_weapon, self.create_spell,
                                                    self.destroy_spell)
                            else:
                                if col == "390": monster_name = "bamboo"
                                elif col == "391": monster_name = "spirit"
                                elif col == "392": monster_name = "raccoon"
                                else: monster_name = "squid"

                                Enemy(
                                    monster_name,
                                    (x, y),
                                    [self.visible_sprites, self.attackable_sprites],
                                    self.obstacle_sprites, self.damage_player,
                                    self.trigger_death_particles, self.award_xp
                                )

    def create_weapon(self):
        """Create a weapon and draw it on the screen."""

        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_weapon(self):
        """Remove a weapon from the screen."""

        if self.current_attack:
            self.current_attack.kill()
            self.current_attack = None

    def create_spell(self, style, strength, cost):
        """Create a spell and draw it on the screen."""

        if style == "heal":
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

        if style == "flame":
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_spell(self):
        """Remove a spell from the screen."""

        pass

    def run_attack_logic(self):
        """Check if an attack sprite is colliding with an attackable sprite.
        If so, handle the logic for an attackable being hit.
        """

        for attack_sprite in self.attack_sprites:
            # spritecollide() -- checks if the sprite collides with any sprite in the group
            collision_sprites = pygame.sprite.spritecollide(
                attack_sprite,
                self.attackable_sprites,
                False,
            )

            # for each collision found...
            for target_sprite in collision_sprites:
                if target_sprite.sprite_type == "grass":
                    # run particle effect
                    pos = target_sprite.rect.center
                    offset = pygame.math.Vector2(0, 75)
                    for _ in range(random.randint(3,6)):
                        self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                    # destroy the grass
                    target_sprite.kill()
                else: # must be an enemy
                    target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        """Deal damage to the player."""

        if not self.player.vulnerable:
            return
        
        self.player.health -= amount
        self.player.vulnerable = False
        self.player.hurt_time = pygame.time.get_ticks()

        self.animation_player.create_particles(
            attack_type,
            self.player.rect.center,
            [self.visible_sprites]
        )

    def trigger_death_particles(self, pos, particle_type):
        """Trigger the particle effects for a monster death."""

        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])

    def award_xp(self, amount):
        """Award the player the specified amount of experience points."""

        self.player.exp += amount

    def toggle_menu(self):
        """Toggle the game menu."""

        self.game_paused = not self.game_paused

    def run(self):
        """Update and draw the level"""

        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:
            # display the upgrade menu
            self.upgrade_menu.display()
        else:
            # run the game
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.run_attack_logic()


class YSortCameraGroup(pygame.sprite.Group):
    """A custom sprite group with some functions for better camerawork."""

    def __init__(self):
        # initialize parent class
        super().__init__()

        # get the surface, and integers representing half the width and height
        self.display_surface = pygame.display.get_surface()
        
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2

        # create an offset for the camera, starting with [0, 0]
        self.offset = pygame.math.Vector2()

        # create the floor
        self.floor_surf = pygame.image.load("../graphics/tilemap/ground.png").convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        """Draw visible sprites, offsetting by the player's position."""

        # get the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # draw floor with offset
        offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, offset_pos)

        # draw sprites with offset (keeping player in the center of the screen)
        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda x: x.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self, player):
        """Draw and update enemy entities."""

        enemy_sprites = [sprite for sprite in self.sprites() 
                        if hasattr(sprite, "sprite_type") 
                        and sprite.sprite_type == "enemy"]
        for sprite in enemy_sprites:
            sprite.enemy_update(player)
