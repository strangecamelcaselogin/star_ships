from time import time
from math import pi

from settings_storage import settings
from game_object import GameObject
from bullet import Bullet


class Ship(GameObject):
    def __init__(self, pygame, surface, radius, angle, mass, position, color, img_path):
        super().__init__(pygame, surface, radius, angle, mass, position, color)
        self.eng_force_norm = 0
        self.time_last_shot = 0
        self.__prerare_img___(img_path)

    def __prerare_img___(self, img_path):
        ship_img = self.pygame.image.load(img_path)
        self.img = self.pygame.transform.scale(ship_img, (self.radius * 2, self.radius * 2))
        # pxarray = self.pygame.PixelArray(ship_img.copy()).transpose()
        # ship_img = pxarray.surface

    def turn(self, delta, dt):
        self.angle += delta * dt
        self.angle %= 2 * pi

    def render(self, width=1):
        # super().render(width)
        img = self.pygame.transform.rotate(self.img, self.angle * 180 / pi - 85)
        w, h = img.get_size()
        self.surface.blit(img, (self.x - w//2, self.y - h//2))
        # Добавим направление взгляда
        dirx, diry = (int(d * self.radius) for d in self.direction)
        self.pygame.draw.line(self.surface, settings.red, (self.x, self.y), (self.x + dirx, self.y + diry))

    def shot(self):
        t = time()
        if t - self.time_last_shot > settings.COOLDOWN:
            self.time_last_shot = t
            inst_velocity = self.direction * settings.BULLET_VELOCITY / settings.FPS
            return Bullet(self.pygame, self.surface, settings.BULLET_RADIUS, settings.BULLET_MASS, self.position,
                          inst_velocity, settings.yellow)

        return None
