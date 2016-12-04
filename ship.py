from random import randint
from math import pi

import numpy as np

from settings_storage import settings
from game_object import GameObject


class Ship(GameObject):
    def __init__(self, pygame, surface, radius, angle, mass, position, color):
        super().__init__(pygame, surface, radius, angle, mass, position, color)

    def turn(self, delta, dt):
        self.angle += delta * dt
        self.angle %= 2 * pi
