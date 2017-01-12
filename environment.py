from time import time
from random import random
from math import pi

import numpy as np

from v2math import v2norm, v2sqr_norm, v2norm, v2unit
from settings_storage import settings
from ship import Ship
from asteroid import Asteroid
from gravity_source import GravitySource
from space_map import SpaceMap


class Environment:
    def __init__(self, pygame, settings_filename, debug=False):
        settings.load(settings_filename)

        self.debug = debug
        self.stop_gravity = False
        self.stop = False

        self.dt = 1 / settings.FPS

        self.pygame = pygame
        self.pygame.init()

        self.clock = self.pygame.time.Clock()
        self.text = self.pygame.font.SysFont(settings.FONT_NAME, settings.FONT_SIZE)

        if settings.FULLSCREEN:
            # Выбираем наибольшее доступное разрешение
            settings.DISPLAY_RES = self.pygame.display.list_modes()[0]
            self.surface = self.pygame.display.set_mode(settings.DISPLAY_RES, self.pygame.FULLSCREEN)
        else:
            self.surface = self.pygame.display.set_mode(settings.DISPLAY_RES)

        self.map = SpaceMap(self.pygame, settings.DISPLAY_RES, settings.MAP_IMG, debug=settings.MAP_DEBUG)

        background_img = self.pygame.image.load(settings.BACKGROUND)
        background_img = self.pygame.transform.scale(background_img, settings.DISPLAY_RES)
        background_img.blit(self.map.map_image, (0, 0))  # Накладываем карту на картинку

        # convert() приводит pixelformat к такому же как и у surface, добавляет производительности
        self.background_image = background_img.convert()

        self.ships = []
        self.bullets = []
        self.asteroids = []
        self.gravity_sources = []

        self.init_objects()

    def init_objects(self):
        width, height = settings.DISPLAY_RES
        ship_0_position = (random() * width, random() * height)
        ship_1_position = (random() * width, random() * height)
        self.ships += [
            Ship(self.pygame, self.surface, settings.SHIP_RADIUS, 0 * pi, settings.SHIP_MASS, ship_0_position,
                 settings.blue, settings.SHIP_HEALTH, settings.SHIP_0_IMG)]

        self.ships += [
            Ship(self.pygame, self.surface, settings.SHIP_RADIUS, 0 * pi, settings.SHIP_MASS, ship_1_position,
                 settings.blue, settings.SHIP_HEALTH, settings.SHIP_1_IMG)]

        # Asteroids
        self.asteroids = []

        #for i in range(settings.ASTEROIDS_CNT):
        #    initial_position = (random() * width, random() * height)
        #    initial_velocity = np.array((0., 0.))  # np.array((random() * 3, random() * 3))
        #    self.asteroids.append(Asteroid(self.pygame, self.surface, settings.ASTEROID_RADIUS, settings.ASTEROID_MASS,
        #                                   initial_position, initial_velocity, settings.white,
        #                                   settings.ASTEROID_HEALTH))

        # Gravity sources
        # TODO: to script
        inf_threshold = 10 ** 7  # max gravity force
        mass = 5.97 * 10 ** 16
        self.gravity_sources = []
        #    GravitySource(self.pygame, self.surface, 25, mass,
        #                  (width / 3 / settings.SCALE, height / 2 / settings.SCALE),
        #                  settings.black, settings.G, inf_threshold),
        #    GravitySource(self.pygame, self.surface, 25, mass,
        #                  (2 * width / 3 / settings.SCALE, height / 2 / settings.SCALE), settings.black, settings.G,
        #                  inf_threshold)]

    def handle_events(self):
        # Check pygame events
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.stop = True

            if event.type == self.pygame.KEYDOWN:
                if event.key == self.pygame.K_ESCAPE:
                    self.stop = True

                if event.key == self.pygame.K_p:
                    self.pause("PAUSED | ESCAPE - EXIT")

                if event.key == self.pygame.K_b:
                    self.debug = not self.debug

                if event.key == self.pygame.K_g:
                    self.stop_gravity = not self.stop_gravity

        # Check raw keys values for ship 0
        keys = self.pygame.key.get_pressed()

        if keys[self.pygame.K_w]:
            self.ships[0].eng_force_norm = settings.ENG_FORCE

        if keys[self.pygame.K_s]:
            self.ships[0].eng_force_norm = -settings.ENG_FORCE

        if keys[self.pygame.K_a]:
            self.ships[0].turn(settings.da * pi, self.dt)

        if keys[self.pygame.K_d]:
            self.ships[0].turn(-settings.da * pi, self.dt)

        if keys[self.pygame.K_SPACE]:
            bullet = self.ships[0].shot(self.dt)
            if bullet is not None:
                self.bullets.append(bullet)

        # Check raw keys values for ship 1
        if keys[self.pygame.K_UP]:
            self.ships[1].eng_force_norm = settings.ENG_FORCE

        if keys[self.pygame.K_DOWN]:
            self.ships[1].eng_force_norm = -settings.ENG_FORCE

        if keys[self.pygame.K_LEFT]:
            self.ships[1].turn(settings.da * pi, self.dt)

        if keys[self.pygame.K_RIGHT]:
            self.ships[1].turn(-settings.da * pi, self.dt)

        if keys[self.pygame.K_RETURN]:
            bullet = self.ships[1].shot(self.dt)
            if bullet is not None:
                self.bullets.append(bullet)

    def apply_forces(self):
        # Ship engine force
        for ship in self.ships:
            ship.add_forces(ship.direction * ship.eng_force_norm)

        # Add gravity
        if not self.stop_gravity:
            for g in self.gravity_sources:
                for ship in self.ships:
                    ship.add_forces(g.get_gravity_force(ship))
                for ast in self.asteroids:
                    ast.add_forces(g.get_gravity_force(ast))

                for b in self.bullets:
                    b.add_forces(g.get_gravity_force(b))

    def update(self):
        # Update positions
        for ship in self.ships:
            ship.update(self.dt)

        for ast in self.asteroids:
            ast.update(self.dt)

        for b in self.bullets:
            b.update(self.dt)

    def handle_collisions(self, iterations=1):
        """
        Detect and resolve collisions
        """
        for count in range(iterations):
            # Object to object
            self.object_collisions(self.ships[0], self.ships[1])

            for ast in self.asteroids:
                self.object_collisions(self.ships[0], ast)
                self.object_collisions(self.ships[1], ast)

                for ast2 in self.asteroids:
                    if ast is not ast2:
                        self.object_collisions(ast, ast2)

                for b in self.bullets:
                    contact = self.object_collisions(ast, b)
                    if contact:
                        ast.make_damage(b.cnt_damage)
                        b.health = 0

            # Ship to bullets
            for ship in self.ships:
                for b in self.bullets:
                    contact = self.object_collisions(ship, b)
                    if contact:
                        ship.make_damage(b.cnt_damage)
                        b.health = 0

            # Object to map
            for ast in self.asteroids:
                self.map_collision(ast)

            self.map_collision(self.ships[0])
            self.map_collision(self.ships[1])

    @staticmethod
    def object_collisions(a, b):
        direction = a.position - b.position
        distance = v2norm(direction)
        radius_sum = a.radius + b.radius
        if distance <= radius_sum:
            if distance != 0:
                factor = (distance - radius_sum) / distance
            else:
                factor = -10

            k = a.mass / (a.mass + b.mass)
            # v2unit(direction)
            a.position -= (1 - k) * factor * direction
            b.position += k * factor * direction

            return True

        return False

    @staticmethod
    def screen_border_collisions(a):
        if a.x - a.radius < 0:
            a.position[0] = a.radius

        elif a.x + a.radius > settings.DISPLAY_RES[0]:
            a.position[0] = settings.DISPLAY_RES[0] - a.radius

        if a.y - a.radius < 0:
            a.position[1] = a.radius

        elif a.y + a.radius > settings.DISPLAY_RES[1]:
            a.position[1] = settings.DISPLAY_RES[1] - a.radius

    def map_collision(self, a):
        number = a.get_tile(self.map)

        if number is not None:

            point_contour = self.map.point_cntr_in_tile[number]

            collide = False
            min_delta = a.radius
            min_point = None

            for point in point_contour[1:]:
                direction = a.position - point
                distance = v2norm(direction)  # TODO sqr_norm
                if distance < min_delta:
                    if not collide:
                        collide = True

                    min_delta = distance
                    min_point = point

            if collide:
                x, y = min_point[0], min_point[1]
                grad_x = self.map.grad[y][x].real
                grad_y = self.map.grad[y][x].imag
                normal = v2unit(np.array([grad_x, grad_y]))

                factor = (min_delta - a.radius) / min_delta
                a.position += normal * factor

    def render(self):
        # self.surface.fill(settings.white)
        self.surface.blit(self.background_image, (0, 0))

        [g.render(width=0) for g in self.gravity_sources]
        [a.render() for a in self.asteroids]
        [b.render() for b in self.bullets]
        [s.render(width=0) for s in self.ships]

        if self.debug:
            [a.render_debug() for a in self.asteroids]
            [s.render_debug() for s in self.ships]
            self.render_net()

    def render_hud(self, cycle_time):
        hud_color = settings[settings.HUD_COLOR]

        cycle_percent = cycle_time / self.dt * 100
        fps_label = self.text.render('FPS:{}, cycle_time:{}%'.format(round(self.clock.get_fps()), round(cycle_percent)),
                                     1, settings.white)

        data_0 = self.text.render('ship_1: health:{}'.format(self.ships[0].health), 1, hud_color)

        data_1 = self.text.render('ship_2: health:{}'.format(self.ships[1].health), 1, hud_color)

        self.surface.blit(data_0, (10, 10))
        self.surface.blit(data_1, (10, 30))
        self.surface.blit(fps_label, (10, settings.DISPLAY_RES[1] - 20))

    def render_net(self):
        width, height = settings.DISPLAY_RES  # self.binmap.shape[:2]
        delta = settings.TILE_SIZE

        for i in range(1, self.map.numbers_tile_in_x):
            start = (i * delta, 0)
            finish = (i * delta, height)
            self.pygame.draw.line(self.surface, settings.gray, start, finish)

        for i in range(1, self.map.numbers_tile_in_y):
            start = (0, i * delta)
            finish = (width, i * delta)
            self.pygame.draw.line(self.surface, settings.gray, start, finish)

    @staticmethod
    def screen_border_filter(game_object):
        x, y = game_object.position
        return x < 0 or y < 0 or x > settings.DISPLAY_RES[0] or y > settings.DISPLAY_RES[1]

    @staticmethod
    def health_filter(game_object):
        if game_object.health == 0:
            return True

    @staticmethod
    def check_kill(check_list):
        for elem in check_list[:]:
            if Environment.health_filter(elem):  # elem.health == 0:  # screen_border_filter(elem):
                check_list.remove(elem)

    def play_sound(self, filename):
        sound = self.pygame.mixer.Sound(filename)
        sound.play(loops=-1)

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

                    stop = True

            self.clock.tick(settings.FPS)

    def run(self):
        while not self.stop:
            load_timer = time()

            for ship in self.ships:
                ship.reset_forces()

            for a in self.asteroids:
                a.reset_forces()

            for b in self.bullets:
                b.reset_forces()

            self.handle_events()  # Events and keys

            self.check_kill(self.bullets)  # remove died objects
            self.check_kill(self.asteroids)

            self.apply_forces()  # Add Forces
            self.update()  # Update all objects
            self.handle_collisions(iterations=1)

            load_timer = time() - load_timer

            self.render()  # Render all objects
            self.render_hud(load_timer)  # Render HUD

            # Update frame
            self.pygame.display.update()
            self.clock.tick(settings.FPS)

            for i, ship in enumerate(self.ships):
                if ship.health == 0:
                    self.pause('PLAYER {} WIN'.format(i + 1))
                    self.stop = True

        self.pygame.quit()
