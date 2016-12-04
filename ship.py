from random import randint
from math import pi

import numpy as np

from settings_storage import settings
from game_object import GameObject


class Ship(GameObject):
    def __init__(self, pygame, surface, radius, angle, mass, position, color):
        super().__init__(pygame, surface, radius, angle, mass, position, color)
        self.eng_force_norm = 0

    def turn(self, delta, dt):
        self.angle += delta * dt
        self.angle %= 2 * pi

    def render(self, width=1):
        super().render(width)
        x, y = (int(round(p * settings.SCALE)) for p in self.position)

        # angle direction
        dirx, diry = (int(d * self.radius) for d in self.direction)
        self.pygame.draw.line(self.surface, settings.red, (x, y), (x + dirx, y + diry))
