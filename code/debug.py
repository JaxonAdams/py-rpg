"""Contains the debug function, which can be used to display data in-game."""

import pygame

pygame.init()
font = pygame.font.Font(None, 30)

def debug(info, y=10, x=10):
    """Print the provided info in the PyGame window."""

    display_surface = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, "White")
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    pygame.draw.rect(display_surface, "Black", debug_rect)
    display_surface.blit(debug_surf, debug_rect)
