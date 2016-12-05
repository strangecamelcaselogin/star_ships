from math import pi

from settings_storage import settings
from game_object import GameObject
from bullet import Bullet


class Ship(GameObject):
    def __init__(self, pygame, surface, radius, angle, mass, position, color):
        super().__init__(pygame, surface, radius, angle, mass, position, color)
        self.eng_force_norm = 0

    def turn(self, delta, dt):
        self.angle += delta * dt
        self.angle %= 2 * pi

    def render(self, width=1):
        super().render(width)

        # Направление взгляда
        dirx, diry = (int(d * self.radius) for d in self.direction)
        self.pygame.draw.line(self.surface, settings.red, (self.x, self.y), (self.x + dirx, self.y + diry))

    def shot(self):
        # TODO cool down
        inst_velocity = self.direction * settings.BULLET_VELOCITY / settings.FPS

        return Bullet(self.pygame, self.surface, 5, 100, self.position, inst_velocity, settings.yellow)
