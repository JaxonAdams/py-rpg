"""Contains the code needed to create and manage the game's upgrade menu."""


import pygame

from settings import *


class UpgradeMenu:
    """The game's upgrade menu."""

    def __init__(self, player):

        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player

        self.attibute_num = len(player.stats)
        self.attribute_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())

        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # item dimensions
        self.height = self.display_surface.get_size()[1] * 0.8
        self.width = self.display_surface.get_size()[0] // (self.attibute_num + 1)

        # item creation
        self.item_list = []
        self.create_items()

        # selection system
        self.selection_index = 0
        self.selection_time = None
        self.can_move = True

    def get_input(self):
        """Get and handle input from the player."""

        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_RIGHT] and self.selection_index < self.attibute_num - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()

            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                print(self.selection_index)

    def selection_cooldown(self):
        """Manage the selection movement cooldown with a custom timer."""

        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if current_time - self.selection_time >= 300:
                self.can_move = True

    def create_items(self):
        """Create a new Item for each stat that can be upgraded."""

        for item in range(self.attibute_num):
            # horizontal pos
            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.attibute_num
            left = (item * increment) + (increment - self.width) // 2

            # vertical pos
            top = self.display_surface.get_size()[1] * 0.1

            # create the object
            item = Item(left, top, self.width, self.height, item, self.font)
            self.item_list.append(item)

    def display(self):
        """Display the game menu."""

        self.get_input()
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):

            # get attributes
            name = self.attribute_names[index]
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.player.get_cost_by_index(index)

            # display item
            item.display(self.display_surface, self.selection_index, name, value, max_value, cost)


class Item:
    """A box which manages a stat upgrade."""

    def __init__(self, l, t, w, h, index, font):

        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font

    def display_name(self, surface, name, cost, selected):
        """Display the stat's name on the screen."""

        # title
        title_surf = self.font.render(name, False, TEXT_COLOR)
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

        # cost
        cost_surf = self.font.render(str(int(cost)), False, TEXT_COLOR)
        cost_rect = cost_surf.get_rect(midbottom=self.rect.midbottom + pygame.math.Vector2(0, -20))

        # draw
        surface.blit(title_surf, title_rect)
        surface.blit(cost_surf, cost_rect)

    def display(self, surface, selection_num, name, value, max_value, cost):
        """Display an item on the screen."""

        pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
        self.display_name(surface, name, cost, False)
