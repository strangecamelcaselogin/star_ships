from math import sin, cos, pi

from game_object import GameObject


class Bullet(GameObject):
    def __init__(self, pygame, surface, radius, mass, position, inst_velocity, color):
        super().__init__(pygame, surface, radius, 0, mass, position, color)
        self.previous_position = position - inst_velocity
