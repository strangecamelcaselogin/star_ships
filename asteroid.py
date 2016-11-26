import pygame

from settings_storage import settings
from game_object import GameObject


class Asteroid(GameObject):
    def __init__(self, pygame, surface, radius, angle, mass, position):
        super().__init__(pygame, surface, radius, angle, mass, position)

    def render(self):
        x, y = (int(round(v)) for v in self.position)
        self.pygame.draw.circle(self.surface, settings.black, (x, y), self.radius, 1)