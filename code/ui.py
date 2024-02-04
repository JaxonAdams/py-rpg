"""Contains all the code necessary to create and manage the UI or HUD."""

import pygame
from settings import *

class UI:
    """The UI, or HUD."""

    def __init__(self):
        
        # general
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # bar setup
        self.health_bar_rect = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        # weapon assets
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            path = weapon["graphic"]
            weapon_img = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon_img)

        # spell assets
        self.spell_graphics = []
        for spell in magic_data.values():
            path = spell["graphic"]
            spell_img = pygame.image.load(path).convert_alpha()
            self.spell_graphics.append(spell_img)


    def show_bar(self, current, max, bg_rect, color):
        """Create and display a UI bar."""

        # draw bg bar
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # convert stat to pixel
        ratio = current / max
        current_width = bg_rect.width * ratio

        # draw "current" stat bar
        current_rect = bg_rect.copy()
        current_rect.width = current_width
        pygame.draw.rect(self.display_surface, color, current_rect)

        # draw a border around the bar
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_exp(self, exp):
        """Display the current player exp."""

        text_surf = self.font.render(str(int(exp)), False, TEXT_COLOR)
        txt_x, txt_y = self.display_surface.get_size()
        text_rect = text_surf.get_rect(bottomright=(txt_x - 20, txt_y - 20))

        # background
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20, 20))
        # exp text
        self.display_surface.blit(text_surf, text_rect)
        # frame
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

    def show_selection_box(self, left, top, has_switched):
        """Display a weapon or magic selection box."""

        # draw selection box
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # draw border
        border_clr = UI_BORDER_COLOR_ACTIVE if has_switched else UI_BORDER_COLOR
        pygame.draw.rect(self.display_surface, border_clr, bg_rect, 3)

        return bg_rect

    def show_weapon_overlay(self, weapon_index, has_switched):
        """Manage the display of a weapon in a selection box."""

        # create a selection box
        bg_rect = self.show_selection_box(10, 630, has_switched)

        weapon_surf = self.weapon_graphics[weapon_index]
        weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

        # draw the weapon inside the selection box
        self.display_surface.blit(weapon_surf, weapon_rect)

    def show_magic_overlay(self, spell_index, has_switched):
        """Manage the display of a weapon in a selection box."""

        # create a selection box
        bg_rect = self.show_selection_box(80, 635, has_switched)

        spell_surf = self.spell_graphics[spell_index]
        spell_rect = spell_surf.get_rect(center=bg_rect.center)

        # draw the spell inside the selection box
        self.display_surface.blit(spell_surf, spell_rect)

    def display(self, player):
        """Display player stats to the screen."""
        
        # health bar
        self.show_bar(player.health, player.stats["health"],
                      self.health_bar_rect, HEALTH_COLOR)

        # energy bar
        self.show_bar(player.energy, player.stats["energy"],
                      self.energy_bar_rect, ENERGY_COLOR)
        
        # experience
        self.show_exp(player.exp)

        # weapon selection
        self.show_weapon_overlay(player.weapon_index, not player.can_switch_weapon)
        # magic selection
        self.show_magic_overlay(player.spell_index, not player.can_switch_spell)
