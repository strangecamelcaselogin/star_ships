from random import randint
from math import pi

import numpy as np

from game_object import GameObject
from settings_storage import settings


class Ship(GameObject):
    def __init__(self, pygame, surface, radius, angle, mass, position, force):
        super().__init__(pygame, surface, radius, angle, mass, position, force)

    def set_angle(self, delta):
        self.angle += delta
        self.angle %= 2 * pi

    def render(self):
        # ship
        x, y = (int(round(v)) for v in self.position)
        self.pygame.draw.circle(self.surface, settings.blue, (x, y), self.radius)  # RADIUS

        # angle direction
        dirx, diry = (int(v * self.radius) for v in self.direction)
        self.pygame.draw.line(self.surface, settings.red, (x, y), (x + dirx, y + diry))

        # velocity vector
        vx, vy = (int(v * settings.SCALE) for v in self.velocity)
        self.pygame.draw.line(self.surface, settings.green, (x, y), (x + vx, y + vy))

