from random import random
from time import time
from math import pi

import numpy as np
from v2math import v2is_same, v2norm, v2normal, v2reflect, v2unit

from settings_storage import settings
from ship import Ship
from asteroid import Asteroid
from gravity_source import GravitySource


class Environment:
    def __init__(self, pygame, settings_filename):
        settings.load(settings_filename)

        self.pygame = pygame
        self.pygame.init()

        self.clock = self.pygame.time.Clock()
        self.text = self.pygame.font.SysFont("monospace", 15)

        print(self.pygame.display.Info())

        if settings.FULLSCREEN:
            settings.DISPLAY_RES = self.pygame.display.list_modes()[0]  # Выбираем наибольшее доступное разрешение

        self.surface = self.pygame.display.set_mode(settings.DISPLAY_RES, self.pygame.FULLSCREEN)
        WIDHT, HIGH = settings.DISPLAY_RES

        ship_position = (random() * WIDHT, random() * HIGH)
        self.ship = Ship(self.pygame, self.surface, 10, pi / 2, settings.SHIP_MASS, ship_position, settings.blue)

        self.asteroids = []
        for i in range(settings.ASTEROIDS_CNT):
            initial_position = (random() * WIDHT, random() * HIGH)
            initial_velocity = np.array((random(), random()))
            self.asteroids.append(Asteroid(self.pygame, self.surface, 10, settings.ASTEROID_MASS,
                                           initial_position, initial_velocity, settings.white))

        # Черные дыры
        inf_threshold = 10 ** 7
        mass = 5.97 * 10 ** 16
        self.gravity_source = [GravitySource(self.pygame, self.surface, 25, mass, (WIDHT / 3 / settings.SCALE, HIGH / 2 / settings.SCALE), settings.black, settings.G, inf_threshold),
                               ]#GravitySource(self.pygame, self.surface, 25, mass, (2 * WIDHT / 3 / settings.SCALE, HIGH / 2 / settings.SCALE), settings.black, settings.G, inf_threshold)]

        #.convert() позволило увеличить fps с 50 до 270
        background_img = self.pygame.image.load(settings.BACKGROUND).convert()
        self.background = self.pygame.transform.scale(background_img, settings.DISPLAY_RES)

    def load_map(self):
        pass

    def render_hud(self):
        fps_label = self.text.render('FPS:{}'.format(round(self.clock.get_fps())), 1, settings.white)
        self.surface.blit(fps_label, (10, settings.DISPLAY_RES[1] - 20))

        data = self.text.render('|F_total|:{}, |F_engine|:{}, p:{}, |v|:{}, |a|:{}, ang:{}'
                                .format(np.round(v2norm(self.ship.total_force), decimals=1),
                                        self.ship.eng_force_norm,
                                        np.around(self.ship.position, decimals=1),
                                        np.round(v2norm(self.ship.velocity), decimals=1),
                                        np.round(v2norm(self.ship.acceleration), decimals=1),
                                        np.round(self.ship.angle / pi, decimals=1)),
                                1, settings.white)

        self.surface.blit(data, (10, 10))

    def pause(self, message):
        WIDHT, HIGH = settings.DISPLAY_RES
        pause_label = self.text.render(message, 1, settings.white)
        width = pause_label.get_width()
        height = pause_label.get_height()
        pause_rectangle = self.surface.blit(pause_label, (WIDHT/2 - width/2, HIGH/2 - height/2))

        stop = False
        while not stop:
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    self.pygame.quit()
                    quit()

                if event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_ESCAPE:
                        self.pygame.quit()
                        quit()

                    if event.key == self.pygame.K_p:
                        stop = True

            self.pygame.display.update(pause_rectangle)
            self.clock.tick(settings.FPS)

    def play_sound(self, filename):
        sound = self.pygame.mixer.Sound(filename)
        sound.play(loops=-1)

    def collision_detect(self, a, b):
        direction = a.position - b.position
        distance = v2norm(direction)
        radius_sum = a.radius + b.radius
        if distance <= radius_sum:
            return direction, distance, radius_sum

        return None

    def collision_resolve(self, a, b, contact):
        direction, distance, radius_sum = contact
        deep = radius_sum - distance
        k = a.mass / b.mass
        n = v2normal(direction)
        # Растолкнуть на deep в соотношении proportion

    def run(self):
        stop = False
        debug = False

        dt = 1 / settings.FPS

        while not stop:
            self.ship.eng_force_norm = 0

            # EVENTS AND KEYS
            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    stop = True

                if event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_ESCAPE:
                        stop = True

                    if event.key == self.pygame.K_p:
                        self.pause("PAUSED")

                    if event.key == self.pygame.K_b:
                        debug = not debug

            keys = self.pygame.key.get_pressed()

            if keys[self.pygame.K_w]:
                self.ship.eng_force_norm = settings.ENG_FORCE

            if keys[self.pygame.K_s]:
                self.ship.eng_force_norm = -settings.ENG_FORCE

            if keys[self.pygame.K_a]:
                self.ship.turn(settings.da * pi, dt)

            if keys[self.pygame.K_d]:
                self.ship.turn(-settings.da * pi, dt)


            # ADD FORCES
            self.ship.add_forces(self.ship.direction * self.ship.eng_force_norm)

            for g in self.gravity_source:
                self.ship.add_forces(g.get_gravity_force(self.ship))
                for a in self.asteroids:
                    a.add_forces(g.get_gravity_force(a))


            # COLLISIONS
            # ...

            # UPDATE
            self.ship.update(dt)
            for a in self.asteroids:
                a.update(dt)

            # RENDER
            # self.surface.fill(settings.white)
            self.surface.blit(self.background, (0, 0))

            self.render_hud()

            [g.render(width=0) for g in self.gravity_source]
            [a.render() for a in self.asteroids]
            self.ship.render(width=0)

            if debug:
                [a.render_debug() for a in self.asteroids]
                self.ship.render_debug()

            self.pygame.display.update()
            self.clock.tick(settings.FPS)

        self.pygame.quit()