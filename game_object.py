from math import sin, cos, pi

import numpy as np

from settings_storage import settings
from v2math import v2unit


class GameObject:
    """
    Класс игрового объекта, реализует физику движения и отрисовку.
    """
    def __init__(self, pygame, surface, radius, angle, mass, position, color, health = 100):
        self.pygame = pygame
        self.surface = surface

        self.radius = radius
        self.angle = angle
        self.mass = mass

        self.direction = np.array((cos(self.angle), -sin(self.angle)))

        self.previous_position = np.array(position)
        self.position = np.array(position)
        self.x, self.y = (int(round(p * settings.SCALE)) for p in self.previous_position)

        self.acceleration = np.array((0., 0.))
        self.inst_velocity = np.array((0., 0.))
        self.total_force = np.array((0., 0.))

        self.color = color
        self.health = health

    def add_forces(self, *forces):
        self.total_force += sum(forces)  # Добавляем силы, действующие на объект

    def update(self, dt):
        """
        Euler:
        v_i+1 = v_i + a * dt
        p_i+1 = p_i + v_i+1 * dt

        Verlet:                   p_i+1 = p_i + p_i - p_(i-1) + a * dt * dt
        Time Corrected Verlet:    p_i+1 = p_i + (p_i - p_(i-1)) * (dt / prev_dt) + a * dt * dt
        """
        self.direction = np.array((cos(self.angle), -sin(self.angle)))

        self.acceleration = self.total_force / self.mass

        old_position = self.position
        self.inst_velocity = (self.position - self.previous_position)
        self.position = self.position + self.inst_velocity + self.acceleration * dt ** 2
        self.previous_position = old_position

        self.x, self.y = (int(round(p * settings.SCALE)) for p in self.previous_position)

    def reset_forces(self):
        """
        Important to reset self.total_force
        """
        self.total_force = np.array((0., 0.))

    def render(self, width=1):
        self.pygame.draw.circle(self.surface, self.color, (self.x, self.y), self.radius, width)

    def render_debug(self):
        # Velocity vector
        vx, vy = (int(v * settings.SCALE * settings.FPS) for v in self.inst_velocity)
        self.pygame.draw.line(self.surface, settings.green, (self.x, self.y), (self.x + vx, self.y + vy))

        # Total Force vector
        fx, fy = (int(f * self.radius) for f in v2unit(self.total_force))
        self.pygame.draw.line(self.surface, settings.yellow, (self.x, self.y), (self.x + fx, self.y + fy))

    def make_damage(self, cnt):
        if self.health - cnt > 0:
            self.health -= cnt

        else:
            self.health = 0

    def get_tile(self):
        pass
