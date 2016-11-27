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
        self.inertia_norm = (self.mass * self.radius ** 2) / 4

        self.position = np.array(position)
        self.acceleration = np.array((0., 0.))
        self.velocity = np.array((0., 0.))
        self.total_force = np.array((0., 0.))

        self.color = color

    def add_forces(self, forces):
        self.total_force += sum(forces)

    def update(self):
        self.direction = np.array((cos(self.angle), -sin(self.angle)))

        self.acceleration = self.total_force / self.mass
        self.velocity += self.acceleration / settings.FPS
        self.position += (self.velocity * settings.SCALE ) / settings.FPS

        self.total_force = np.array((0., 0.))  # Очень важно обнулить аккумулятор сил.

    def render(self, width=1):
        x, y = (int(round(v)) for v in self.position)
        self.pygame.draw.circle(self.surface, self.color, (x, y), self.radius, width)

    def render_debug(self):
        # angle direction
        x, y = (int(round(v)) for v in self.position)
        dirx, diry = (int(v * self.radius) for v in self.direction)
        self.pygame.draw.line(self.surface, settings.red, (x, y), (x + dirx, y + diry))

        # velocity vector
        vx, vy = (int(v * settings.SCALE) for v in self.velocity)
        self.pygame.draw.line(self.surface, settings.green, (x, y), (x + vx, y + vy))