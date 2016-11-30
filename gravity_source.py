import numpy as np
from vec2math import vec2_norm, vec2_unit

from settings_storage import settings
from game_object import GameObject


class GravitySource(GameObject):
    def __init__(self, pygame, surface, radius, mass, position, color, G, inf_threshold):
        super().__init__(pygame, surface, radius, 0, mass, position, color)
        self.G = G
        self.inf_threshold = inf_threshold

    def get_gravity_force(self, game_object):
        direction = self.position - game_object.position
        distance = vec2_norm(direction)
        normed_direction = vec2_unit(direction)

        gravity_norm = self.G * (game_object.mass * self.mass) / distance ** 2
        if gravity_norm > self.inf_threshold:
            gravity_norm = self.inf_threshold

        return normed_direction * gravity_norm
