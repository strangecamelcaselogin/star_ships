import numpy as np
from v2math import v2norm, v2unit

from settings_storage import settings
from game_object import GameObject


class GravitySource(GameObject):
    def __init__(self, pygame, surface, radius, mass, position, color, G, inf_threshold):
        super().__init__(pygame, surface, radius, 0, mass, position, color)
        self.G = G
        self.inf_threshold = inf_threshold

    def get_gravity_force(self, game_object):
        # F_g = G * (m1 * m2) / d**2

        direction = self.position - game_object.position
        distance = v2norm(direction)
        direction_unit = v2unit(direction)

        gravity_norm = self.G * (game_object.mass * self.mass) / distance ** 2
        if gravity_norm > self.inf_threshold:
            gravity_norm = self.inf_threshold

        return direction_unit * gravity_norm
