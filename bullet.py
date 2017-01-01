from settings_storage import settings
from game_object import GameObject


class Bullet(GameObject):
    def __init__(self, pygame, surface, radius, mass, position, inst_velocity, color, ttl):
        super().__init__(pygame, surface, radius, 0, mass, position, color)
        self.previous_position = position - inst_velocity
        self.ttl = ttl * settings.FPS

    def update(self, dt):
        super().update(dt)

        if self.ttl > 0:
            self.ttl -= 1
        else:
            self.health = 0
