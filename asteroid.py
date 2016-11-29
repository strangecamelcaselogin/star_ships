from settings_storage import settings
from game_object import GameObject


class Asteroid(GameObject):
    def __init__(self, pygame, surface, radius, mass, position, velocity, color):
        super().__init__(pygame, surface, radius, 0, mass, position, color)
        self.velocity = velocity
