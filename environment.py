from random import random
from time import time
from math import pi

import numpy as np
from vec2math import is_same, vec2_norm, vec2_normal, vec2_reflect, vec2_unit

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
            available_res = self.pygame.display.list_modes()
            settings.DISPLAY_RES = available_res[0]
            self.surface = self.pygame.display.set_mode(settings.DISPLAY_RES, self.pygame.FULLSCREEN)

        else:
            self.surface = self.pygame.display.set_mode(settings.DISPLAY_RES)

        WIDHT, HIGH = settings.DISPLAY_RES
        self.ship = Ship(self.pygame, self.surface, 10, pi / 2, settings.SHIP_MASS, (random() * WIDHT, random() * HIGH), settings.blue)

        self.asteroids = []
        for i in range(settings.ASTEROIDS_CNT):
            velocity = np.array((random(), random()))
            self.asteroids.append(
                Asteroid(self.pygame, self.surface, 10, settings.ASTEROID_MASS, (random() * WIDHT, random() * HIGH), velocity, settings.white))

        G = 6.67 * 10 ** (-11)  # Константа гравитационного взаимодействия
        inf_threshold = 10 ** 7
        mass = 5.97 * 10 ** 16
        self.gravity_source = [GravitySource(self.pygame, self.surface, 25, mass, (WIDHT / 3 / settings.SCALE, HIGH / 2 / settings.SCALE), settings.black, G, inf_threshold),
                               GravitySource(self.pygame, self.surface, 25, mass, (2 * WIDHT / 3 / settings.SCALE, HIGH / 2 / settings.SCALE), settings.black, G, inf_threshold)]

        #.convert() позволило увеличить fps с 50 до 270
        background = self.pygame.image.load(settings.BACKGROUND).convert()
        self.background = self.pygame.transform.scale(background, settings.DISPLAY_RES)

    def load_map(self):
        pass

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
        distance = vec2_norm(direction)
        radius_sum = a.radius + b.radius
        if distance <= radius_sum:
            return direction, distance, radius_sum

        return None

    def collision_resolve(self, a, b, contact):
        #a.velocity = np.array((0., 0.))
        #b.velocity = np.array((0., 0.))
        direction, distance, radius_sum = contact
        deep = radius_sum - distance
        proportion = a.mass / b.mass
        n = vec2_unit(vec2_normal(direction))
        a.velocity = vec2_reflect(a.velocity, n)
        b.velocity = vec2_reflect(b.velocity, n)

    def run(self):
        stop = False
        debug = False

        while not stop:
            dforce_norm = 0
            c_fps = self.clock.get_fps()
            dt = 1 / c_fps if c_fps != 0 else 1/settings.FPS

            # RENDER
            self.surface.blit(self.background, (0, 0))  # self.surface.fill(settings.white)

            [g.render(width=0) for g in self.gravity_source]
            [a.render() for a in self.asteroids]
            self.ship.render(width=0)

            if debug:
                [a.render_debug() for a in self.asteroids]
                self.ship.render_debug()


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
                dforce_norm = 1 * settings.DFORCE_NORM

            if keys[self.pygame.K_s]:
                dforce_norm = -1 * settings.DFORCE_NORM

            if keys[self.pygame.K_a]:
                self.ship.set_angle(settings.da * pi)

            if keys[self.pygame.K_d]:
                self.ship.set_angle(-settings.da * pi)


            # ADD FORCES
            for g in self.gravity_source:
                self.ship.add_forces((self.ship.direction * dforce_norm, g.get_gravity_force(self.ship)))
                for a in self.asteroids:
                    a.add_forces((g.get_gravity_force(a),))


            # COLLISIONS
            for a in self.asteroids:
                contact = self.collision_detect(self.ship, a)
                if contact:
                    self.collision_resolve(self.ship, a, contact)

                for b in self.asteroids:
                    if not is_same(a.position, b.position):
                        contact = self.collision_detect(a, b)
                        if contact:
                            print('hey', contact)
                            self.collision_resolve(b, a, contact)


            # DEBUG DATA
            data = self.text.render('FPS:{}, Ft:{}, p:{}, v:{}, a:{}, ang:{}, dst:{}, dforce_n: {}'
                                     .format(round(c_fps),
                                             np.round(vec2_norm(self.ship.total_force), decimals=1),
                                             np.around(self.ship.position, decimals=1),
                                             np.round(vec2_norm(self.ship.velocity), decimals=1),
                                             np.round(vec2_norm(self.ship.acceleration), decimals=1),
                                             np.round(self.ship.angle / pi, decimals=1),
                                             np.round(vec2_norm(self.gravity_source[0].position - self.ship.position)),
                                             dforce_norm),
                                     1, settings.white)

            self.surface.blit(data, (10, 10))


            # UPDATE
            self.ship.update(dt)
            for a in self.asteroids:
                a.update(dt)

            self.pygame.display.update()
            self.clock.tick(settings.FPS)

        self.pygame.quit()