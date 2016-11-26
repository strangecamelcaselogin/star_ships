from settings_storage import settings
from game_object import GameObject


class Asteroid(GameObject):
    def __init__(self, pygame, surface, radius, mass, position, velocity, color):
        super().__init__(pygame, surface, radius, 0, mass, position)
        self.velocity = velocity
        self.color = color

    def render(self):
        x, y = (int(round(v)) for v in self.position)
        self.pygame.draw.circle(self.surface, self.color, (x, y), self.radius, 1)

        vx, vy = (int(v * settings.SCALE) for v in self.velocity)
        self.pygame.draw.line(self.surface, settings.green, (x, y), (x + vx, y + vy))