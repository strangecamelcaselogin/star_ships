from random import random
from time import time
from math import pi

import numpy as np
from numpy.linalg import norm

import pygame

from settings_storage import settings
from ship import Ship
from asteroid import Asteroid
from gravity_source import GravitySource


class Environment:
    def __init__(self, settings_filename):
        settings.load(settings_filename)

        pygame.init()
        self.pygame = pygame

        # print(pygame.display.Info())
        if settings.FULLSCREEN:
            available_res = pygame.display.list_modes()
            settings.DISPLAY_RES = available_res[0]
            self.surface = pygame.display.set_mode(settings.DISPLAY_RES, pygame.FULLSCREEN)

        else:
            self.surface = pygame.display.set_mode(settings.DISPLAY_RES)

        self.clock = pygame.time.Clock()
        self.text = pygame.font.SysFont("monospace", 15)

        WIDHT, HIGH = settings.DISPLAY_RES
        self.ship = Ship(self.pygame, self.surface, 10, pi/2, settings.SHIP_MASS, (random() * WIDHT, random() * HIGH))

        self.asteroids = []
        for i in range(settings.ASTEROIDS_CNT):
            velocity = np.array((random(), random()))
            self.asteroids.append(
                Asteroid(self.pygame, self.surface, 10, settings.ASTEROID_MASS, (random() * WIDHT, random() * HIGH), velocity, settings.white))

        G = 6.67 * 10 ** (-11)
        inf_threshold = 10 ** 5
        mass = 5 * 10 ** 15
        self.gravity_source = [GravitySource(self.pygame, self.surface, 10, mass, (WIDHT / 2, HIGH / 2),
                                             settings.yellow, G, inf_threshold)]

        background = self.pygame.image.load(settings.BACKGROUND)
        self.background = pygame.transform.scale(background, settings.DISPLAY_RES)

    def load_map(self):
        pass

    def pause(self, message):
        WIDHT, HIGH = settings.DISPLAY_RES
        pause_label = self.text.render(message, 1, settings.white)
        width = pause_label.get_width()
        height = pause_label.get_height()
        self.surface.blit(pause_label, (WIDHT/2 - width/2, HIGH/2 - height/2))

        stop = False
        while not stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()

                    if event.key == pygame.K_p:
                        stop = True

            pygame.display.update()
            self.clock.tick(settings.FPS)

    def run(self):
        #engine_sound = pygame.mixer.Sound("sounds/thrust.wav")
        #engine_sound.play(loops=-1)
        #engine_sound.set_volume(0)

        stop = False
        while not stop:
            dforce_norm = 0

            # RENDER
            self.surface.blit(self.background, (0, 0))  # self.surface.fill(settings.white)
            self.ship.render()
            [g.render() for g in self.gravity_source]
            [a.render() for a in self.asteroids]


            # EVENTS AND KEYS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.pause("PAUSED")

                    if event.key == pygame.K_ESCAPE:
                        stop = True

            keys = pygame.key.get_pressed()

            if keys[pygame.K_w]:
                dforce_norm = 1 * settings.DFORCE_NORM

            if keys[pygame.K_s]:
                dforce_norm += -1 * settings.DFORCE_NORM

            if keys[pygame.K_a]: self.ship.set_angle(settings.da * pi)

            if keys[pygame.K_d]: self.ship.set_angle(-settings.da * pi)


            # ADD FORCES
            for g in self.gravity_source:
                self.ship.add_forces((self.ship.direction * dforce_norm, g.get_gravity_force(self.ship)))
                for a in self.asteroids:
                    a.add_forces((g.get_gravity_force(a),))


            # DEBUG
            label = self.text.render('Ft:{}, p:{}, v:{}, a:{}, ang:{}'
                                     .format(np.round(norm(self.ship.total_force), decimals=1),
                                             np.around(self.ship.position),
                                             np.round(norm(self.ship.velocity), decimals=1),
                                             np.round(norm(self.ship.acceleration), decimals=1),
                                             np.round(self.ship.angle / pi, decimals=1)),
                                     1, settings.white)

            self.surface.blit(label, (10, 10))


            # UPDATE
            self.ship.update()
            for a in self.asteroids:
                a.update()

            pygame.display.update()

            self.clock.tick(settings.FPS)
            pygame.display.set_caption('FPS: {}'.format(round(self.clock.get_fps())))

        pygame.quit()


if __name__ == '__main__':
    env = Environment(settings_filename='test_settings')
    env.run()
