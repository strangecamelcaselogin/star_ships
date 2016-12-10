# from time import time
from random import random
from math import pi

import numpy as np
from v2math import v2norm  # , v2normal, v2reflect, v2unit

from settings_storage import settings
from ship import Ship
from asteroid import Asteroid
from gravity_source import GravitySource


class Environment:
    def __init__(self, pygame, settings_filename, debug=True, stop_gravity=False):
        settings.load(settings_filename)

        self.debug = debug
        self.stop_gravity = stop_gravity

        self.stop = False
        self.dt = 1 / settings.FPS

        self.pygame = pygame
        self.pygame.init()

        self.clock = self.pygame.time.Clock()
        self.text = self.pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE)

        if settings.FULLSCREEN:
            settings.DISPLAY_RES = self.pygame.display.list_modes()[0]  # Выбираем наибольшее доступное разрешение
            self.surface = self.pygame.display.set_mode(settings.DISPLAY_RES, self.pygame.FULLSCREEN)
        else:
            self.surface = self.pygame.display.set_mode(settings.DISPLAY_RES)

        WIDHT, HIGH = settings.DISPLAY_RES

        background_img = self.pygame.image.load(settings.BACKGROUND).convert()  # use .convert()
        self.background_image = self.pygame.transform.scale(background_img, settings.DISPLAY_RES)

        ship_position = (random() * WIDHT, random() * HIGH)
        self.ship = Ship(self.pygame, self.surface, settings.SHIP_RADIUS, 0 * pi, settings.SHIP_MASS, ship_position,
                         settings.blue)

        self.bullets = []

        self.asteroids = []
        for i in range(settings.ASTEROIDS_CNT):
            initial_position = (random() * WIDHT, random() * HIGH)
            initial_velocity = np.array((0., 0.))  #np.array((random() * 3, random() * 3))  # inst speed #np.array((0., 0.))
            self.asteroids.append(Asteroid(self.pygame, self.surface, 10, settings.ASTEROID_MASS,
                                           initial_position, initial_velocity, settings.white))

        # Gravity sources
        inf_threshold = 10 ** 7  # max gravity force
        mass = 5.97 * 10 ** 16
        self.gravity_sources = [
            GravitySource(self.pygame, self.surface, 25, mass, (WIDHT / 3 / settings.SCALE, HIGH / 2 / settings.SCALE),
                          settings.black, settings.G, inf_threshold),
            GravitySource(self.pygame, self.surface, 25, mass,
                          (2 * WIDHT / 3 / settings.SCALE, HIGH / 2 / settings.SCALE), settings.black, settings.G,
                          inf_threshold)]

    def load_map(self):
        pass

    def pause(self, message):
        WIDHT, HIGH = settings.DISPLAY_RES
        pause_label = self.text.render(message, 1, settings.white)
        width = pause_label.get_width()
        height = pause_label.get_height()
        pause_rectangle = self.surface.blit(pause_label, (WIDHT / 2 - width / 2, HIGH / 2 - height / 2))
        self.pygame.display.update(pause_rectangle)

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

            self.clock.tick(settings.FPS)

    def play_sound(self, filename):
        sound = self.pygame.mixer.Sound(filename)
        sound.play(loops=-1)

    def events(self):
        # Check pygame events and raw keys values
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.stop = True

            if event.type == self.pygame.KEYDOWN:
                if event.key == self.pygame.K_ESCAPE:
                    self.stop = True

                if event.key == self.pygame.K_p:
                    self.pause("PAUSED")

                if event.key == self.pygame.K_b:
                    self.debug = not self.debug

                if event.key == self.pygame.K_g:
                    self.stop_gravity = not self.stop_gravity

        keys = self.pygame.key.get_pressed()

        if keys[self.pygame.K_w]:
            self.ship.eng_force_norm = settings.ENG_FORCE

        if keys[self.pygame.K_s]:
            self.ship.eng_force_norm = -settings.ENG_FORCE

        if keys[self.pygame.K_a]:
            self.ship.turn(settings.da * pi, self.dt)

        if keys[self.pygame.K_d]:
            self.ship.turn(-settings.da * pi, self.dt)

        if keys[self.pygame.K_SPACE]:
            bullet = self.ship.shot()
            if bullet is not None:
                self.bullets.append(bullet)

    def update(self):
        # Ship engine force
        self.ship.add_forces(self.ship.direction * self.ship.eng_force_norm)

        # Add gravity
        if not self.stop_gravity:
            for g in self.gravity_sources:
                self.ship.add_forces(g.get_gravity_force(self.ship))
                for a in self.asteroids:
                    a.add_forces(g.get_gravity_force(a))

                for b in self.bullets:
                    b.add_forces(g.get_gravity_force(b))

        # Test
        #f = np.array((-1000000., -1000000.))
        #for a in self.asteroids:
        #    a.add_forces(f)

        # Update positions
        self.ship.update(self.dt)
        for a in self.asteroids:
            a.update(self.dt)

        for g in self.gravity_sources:
            g.update(self.dt)

        for b in self.bullets:
            b.update(self.dt)

        # Detect and resolve collisions
        for count in range(1):
            for a in self.asteroids:
                ship_contact = self.collision_detect(self.ship, a)
                if ship_contact:
                    self.collision_resolve(self.ship, a, ship_contact)

                for b in self.asteroids:
                    if a is not b:
                        contact = self.collision_detect(a, b)
                        if contact:
                            self.collision_resolve(a, b, contact)

        self.border_collisions_check(self.ship)
        for a in self.asteroids:
            self.border_collisions_check(a)

    def render(self):
        # self.surface.fill(settings.white)
        self.surface.blit(self.background_image, (0, 0))

        self.render_hud()

        [g.render(width=0) for g in self.gravity_sources]
        [a.render() for a in self.asteroids]
        [b.render() for b in self.bullets]
        self.ship.render(width=0)

        if self.debug:
            [a.render_debug() for a in self.asteroids]
            self.ship.render_debug()

        # Update frame
        self.pygame.display.update()

    def render_hud(self):
        fps_label = self.text.render('FPS:{}'.format(round(self.clock.get_fps())), 1, settings.white)
        self.surface.blit(fps_label, (10, settings.DISPLAY_RES[1] - 20))

        data = self.text.render('|F_total|:{}, |F_engine|:{}, p:{}, |v|:{}, |a|:{}, ang:{}, b:{}'
                                .format(np.round(v2norm(self.ship.total_force), decimals=1),
                                        self.ship.eng_force_norm,
                                        np.around(self.ship.position, decimals=1),
                                        np.round(v2norm(self.ship.inst_velocity / self.dt), decimals=1),
                                        np.round(v2norm(self.ship.acceleration), decimals=1),
                                        np.round(self.ship.angle / pi, decimals=1),
                                        len(self.bullets)),
                                1, settings.white)

        self.surface.blit(data, (10, 10))

    @staticmethod
    def collision_detect(a, b):
        direction = a.position - b.position
        distance = v2norm(direction)
        radius_sum = a.radius + b.radius
        if distance <= radius_sum:
            factor = (distance - radius_sum) / distance
            return direction, factor

        return None

    @staticmethod
    def collision_resolve(a, b, contact):
        # Растолкнуть a и b на некоторую величину в соотношении k
        direction, factor = contact

        k = a.mass / (a.mass + b.mass)
        a.position -= (1 - k) * factor * direction
        b.position += k * factor * direction

    @staticmethod
    def border_collisions_check(a):
        if a.x - a.radius < 0:
            a.position[0] = a.radius

        elif a.x + a.radius > settings.DISPLAY_RES[0]:
            a.position[0] = settings.DISPLAY_RES[0] - a.radius

        if a.y - a.radius < 0:
            a.position[1] = a.radius

        elif a.y + a.radius > settings.DISPLAY_RES[1]:
            a.position[1] =  settings.DISPLAY_RES[1] - a.radius

    @staticmethod
    def check_kill(check_list):
        i = 0
        l = len(check_list)
        while l > 0 and i < l:  # !!!
            x, y = check_list[i].position
            if x < 0 or y < 0 or x > settings.DISPLAY_RES[0] or y > settings.DISPLAY_RES[1]:
                check_list.pop(i)

            else:
                i += 1

            l = len(check_list)

    def run(self):
        while not self.stop:
            self.ship.eng_force_norm = 0
            self.ship.reset_forces()
            for a in self.asteroids:
                a.reset_forces()

            for b in self.bullets:
                b.reset_forces()

            # Kill all bullets outside screen
            self.check_kill(self.bullets)

            # Events and keys
            self.events()

            # Add Forces, Update all objects, check collisions
            self.update()

            # Render all objects
            self.render()

            self.clock.tick(settings.FPS)

        self.pygame.quit()
# TODO width and high from settings to self