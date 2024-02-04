"""Utility functions for use throughout the source code."""


from os import walk
from csv import reader

import pygame


def import_csv_layout(path):
    """Import map data from the provided csv."""

    with open(path) as level_map:
        layout = reader(level_map, delimiter=",")
        terrain_map = [list(row) for row in layout]

    return terrain_map        


def import_folder(path):
    """Import all images from a folder into pygame."""

    surface_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = f"{path}/{image}"

            image_surf = pygame.image.load(full_path)
            image_surf.convert_alpha()

            surface_list.append(image_surf)

    return surface_list
