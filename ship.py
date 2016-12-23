from time import time
from math import pi

from settings_storage import settings
from game_object import GameObject
from bullet import Bullet


class Ship(GameObject):
    def __init__(self, pygame, surface, radius, angle, mass, position, color, img_path, cnt_angles):
        super().__init__(pygame, surface, radius, angle, mass, position, color)
        self.eng_force_norm = 0
        self.time_last_shot = 0
        self.CNT_ANGLES = cnt_angles
        self.__prerare_img___(img_path)

    def __prerare_img___(self, img_path):
        ship_img = self.pygame.image.load(img_path)
        # pxarray = self.pygame.PixelArray(ship_img.copy()).transpose()
        # print("img = ", pxarray)
        # ship_img = pxarray.surface
        # ship_img = self.pygame.transform.rotate().scale(ship_img, (self.radius * 2, self.radius * 2))
        self.imgs = []
        for i in range(self.CNT_ANGLES):
            angle = float(2*pi) * float(i) / float(self.CNT_ANGLES)
            img = self.pygame.transform.scale(ship_img, (self.radius * 2, self.radius * 2))
            img = self.pygame.transform.rotate(img, angle * 180 / pi - 85)
            self.imgs.append(img)

    def turn(self, delta, dt):
        self.angle += delta * dt
        self.angle %= 2 * pi
        # print(self.angle)

    def render(self, width=1):
        # super().render(width)
        img_num = int(float(self.CNT_ANGLES) * (self.angle) / (2*pi))
        if (img_num) >= self.CNT_ANGLES or img_num < 0:
            print(img_num)
            img_num = 0
        w, h = self.imgs[img_num].get_size()
        self.surface.blit(self.imgs[img_num], (self.x - w//2, self.y - h//2))
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
