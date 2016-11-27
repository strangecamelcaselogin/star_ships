from random import randint
from math import pi

import numpy as np

from game_object import GameObject
from settings_storage import settings


class Ship(GameObject):
    def __init__(self, pygame, surface, radius, angle, mass, position, color):
        super().__init__(pygame, surface, radius, angle, mass, position, color)

    def set_angle(self, delta):
        self.angle += delta
        self.angle %= 2 * pi

