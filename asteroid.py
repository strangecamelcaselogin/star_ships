from settings_storage import settings
from game_object import GameObject


class Asteroid(GameObject):
    def __init__(self, pygame, surface, radius, mass, position, color):
        super().__init__(pygame, surface, radius, 0, mass, position)
        self.color = color

    def render(self):
        x, y = (int(round(v)) for v in self.position)
        self.pygame.draw.circle(self.surface, self.color, (x, y), self.radius, 1)