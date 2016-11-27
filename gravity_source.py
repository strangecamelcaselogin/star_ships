import numpy as np
from numpy.linalg import norm

from settings_storage import settings
from game_object import GameObject


class GravitySource(GameObject):
    def __init__(self, pygame, surface, radius, mass, position, color, G, inf_threshold):
        super().__init__(pygame, surface, radius, 0, mass, position, color)
        self.G = G
        self.inf_threshold = inf_threshold

    def get_gravity_force(self, object):
        direction = self.position - object.position
        distance = norm(direction) / settings.SCALE
        direction = direction / distance if norm(distance) != 0 else np.array((0., 0.))

        gravity_norm = self.G * (object.mass * self.mass) / distance ** 2
        if gravity_norm > self.inf_threshold:
            gravity_norm = self.inf_threshold

        return direction * gravity_norm
