from math import pi

from settings_storage import settings
from game_object import GameObject
from bullet import Bullet


class Ship(GameObject):
    def __init__(self, pygame, surface, radius, angle, mass, position, color, health, img_path):
        super().__init__(pygame, surface, radius, angle, mass, position, color, health)
        self.eng_force_norm = 0

        self.cool_down = int((settings.FPS * 60) / settings.FIRE_RATE)
        self.cd_counter = 0
        self.bullet_velocity = settings.BULLET_VELOCITY
        self.bullet_mass = settings.BULLET_MASS
        self.bullet_radius = settings.BULLET_RADIUS
        self.bullet_ttl = settings.BULLET_TTL
        self.bullet_damage = settings.BULLET_DAMAGE

        self.__prepare_img___(img_path)

    def __prepare_img___(self, img_path):
        ship_img = self.pygame.image.load(img_path)
        self.img = self.pygame.transform.scale(ship_img, (self.radius * 2, self.radius * 2))
        # pxarray = self.pygame.PixelArray(ship_img.copy()).transpose()
        # ship_img = pxarray.surface

    def turn(self, delta, dt):
        self.angle += delta * dt
        self.angle %= 2 * pi

    def update(self, dt):
        super().update(dt)
        if self.cd_counter > 0:
            self.cd_counter -= 1

    def render(self, width=1):
        # super().render(width)
        img = self.pygame.transform.rotate(self.img, self.angle * 180 / pi - 90)
        w, h = img.get_size()
        self.surface.blit(img, (self.x - w // 2, self.y - h // 2))

        # Добавим направление взгляда
        dirx, diry = (int(d * self.radius) for d in self.direction)
        self.pygame.draw.line(self.surface, settings.red, (self.x, self.y), (self.x + dirx, self.y + diry))

    def shot(self):
        if self.cd_counter == 0:
            self.cd_counter = self.cool_down
            inst_velocity = self.direction * self.bullet_velocity / settings.FPS + self.inst_velocity
            # for avoid collisions with ship
            inst_position = self.position + self.direction * (self.radius + self.bullet_radius)
            return Bullet(self.pygame, self.surface, self.bullet_radius, self.bullet_mass, inst_position,
                          inst_velocity, settings.yellow, self.bullet_ttl, self.bullet_damage)
