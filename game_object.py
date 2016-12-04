from math import sin, cos, pi

import numpy as np

from settings_storage import settings


class GameObject:
    def __init__(self, pygame, surface, radius, angle, mass, position, color):
        self.pygame = pygame
        self.surface = surface

        self.radius = radius
        self.angle = angle
        self.mass = mass

        self.direction = np.array((cos(self.angle), -sin(self.angle)))
        self.previous_position = np.array(position)
        self.position = np.array(position)
        self.acceleration = np.array((0., 0.))
        self.velocity = np.array((0., 0.))
        self.total_force = np.array((0., 0.))

        self.color = color

    def add_forces(self, *forces):
        self.total_force += sum(forces)

    def update(self, dt):
        self.direction = np.array((cos(self.angle), -sin(self.angle)))

        self.acceleration = self.total_force / self.mass

        self.velocity = (self.position - self.previous_position) / dt  # не нужно
        t = self.position
        self.position = 2 * self.position - self.previous_position + self.acceleration * dt ** 2
        self.previous_position = t

        # Важно обнулить аккумулятор сил, чтобы силы не накапливались.
        self.total_force = np.array((0., 0.))

    def render(self, width=1):
        x, y = (int(round(p * settings.SCALE)) for p in self.position)
        self.pygame.draw.circle(self.surface, self.color, (x, y), self.radius, width)

    def render_debug(self):
        x, y = (int(round(p * settings.SCALE)) for p in self.position)

        # velocity vector
        vx, vy = (int(v * settings.SCALE) for v in self.velocity)
        self.pygame.draw.line(self.surface, settings.green, (x, y), (x + vx, y + vy))