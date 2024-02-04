"""Contains all code needed to create and manage a weapon."""


import pygame


class Weapon(pygame.sprite.Sprite):
    """A weapon. (pretty self-explanatory)"""
    
    def __init__(self, player, groups):
        super().__init__(groups)

        direction = player.status.split("_")[0]
        offset_h = pygame.math.Vector2(0,16)
        offset_v = pygame.math.Vector2(-10,0)

        self.sprite_type = "weapon"

        # graphic
        full_path = f"../graphics/weapons/{player.weapon}/{direction}.png"
        self.image = pygame.image.load(full_path).convert_alpha()

        # placement
        if direction == "right":
            self.rect = self.image.get_rect(midleft=player.rect.midright + offset_h)
        elif direction == "left":
            self.rect = self.image.get_rect(midright=player.rect.midleft + offset_h)
        elif direction == "down":
            self.rect = self.image.get_rect(midtop=player.rect.midbottom + offset_v)
        elif direction == "up":
            self.rect = self.image.get_rect(midbottom=player.rect.midtop + offset_v)
