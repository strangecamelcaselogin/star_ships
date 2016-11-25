from random import randint
from time import time
from math import pi

import numpy as np
from numpy.linalg import norm

import pygame

from settings_storage import settings
from ship import Ship


class Environment:
    def __init__(self, settings_filename):
        settings.load(settings_filename)

        pygame.init()
        pygame.key.set_repeat(250, int(1000 / settings.FPS))

        self.surface = pygame.display.set_mode(settings.DISPLAY_RES)
        self.clock = pygame.time.Clock()
        self.text = pygame.font.SysFont("monospace", 15)

        WIDHT, HIGH = settings.DISPLAY_RES

        #pygame, surface, angle, mass, position, forces
        self.ship = Ship(pygame, self.surface, 10, 0 * pi, 100, (WIDHT/2, HIGH/2), ((0., 0.),))

    def load_map(self):
        pass

    def pause(self):
        WIDHT, HIGH = settings.DISPLAY_RES
        pause_label = self.text.render("PAUSED", 1, settings.black)
        self.surface.blit(pause_label, (WIDHT/2 - 30, HIGH/2 - 10))

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

    def run(self):
        dforce_norm = 0

        stop = False
        while not stop:
            # EVENTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        stop = True

                    if event.key == pygame.K_p:
                        self.pause()

                    if event.key == pygame.K_w:
                        dforce_norm = 1 * settings.DFORCE_NORM

                    if event.key == pygame.K_s:
                        dforce_norm += -1 * settings.DFORCE_NORM

                    if event.key == pygame.K_q:
                        self.ship.set_angle(0.01 * pi)

                    if event.key == pygame.K_e:
                        self.ship.set_angle(-0.01 * pi)

            # RENDER
            self.surface.fill(settings.white)
            self.ship.render()

            label = self.text.render('Ft:{}, a:{}, v:{}, ang:{}, d_vec:{}'
                                     .format(np.round(norm(self.ship.total_force), decimals=1),
                                             np.round(norm(self.ship.acceleration), decimals=1),
                                             np.round(norm(self.ship.velocity), decimals=1),
                                             np.round(self.ship.angle / pi, decimals=1),
                                             np.round(norm(self.ship.direction), decimals=1)),
                                     1, settings.black)

            self.surface.blit(label, (10, 10))

            # UPDATE
            gravity = (0, 0)  # np.array((0, self.ship.mass * 9.81))
            
            self.ship.update((self.ship.direction * dforce_norm, gravity))
            dforce_norm = 0

            pygame.display.update()

            self.clock.tick(settings.FPS)
            pygame.display.set_caption('FPS: {}'.format(round(self.clock.get_fps())))

        pygame.quit()


if __name__ == '__main__':
    env = Environment(settings_filename='test_settings')
    env.run()
