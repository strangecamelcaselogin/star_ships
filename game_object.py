from math import sin, cos, pi

import numpy as np

from settings_storage import settings


class GameObject:
    def __init__(self, pygame, surface, radius, angle, mass, position, forces):
        self.pygame = pygame
        self.surface = surface

        self.radius = radius
        self.angle = angle
        self.mass = mass

        self.direction = np.array((cos(self.angle), -sin(self.angle)))
        self.inertia_norm = (self.mass * self.radius ** 2) / 4

        self.position = np.array(position)
        self.acceleration = np.array((0., 0.))
        self.velocity = np.array((0., 0.))

        self.total_force = sum(np.array(force) for force in forces)

    def update(self, forces):

        self.direction = np.array((cos(self.angle), -sin(self.angle)))
        self.total_force = sum(forces)
        self.acceleration = self.total_force / self.mass

        self.velocity += self.acceleration / settings.FPS
        self.position += self.velocity / settings.FPS * settings.SCALE