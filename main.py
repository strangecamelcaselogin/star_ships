import pygame

from environment import Environment


if __name__ == '__main__':
    # TODO слежение корабля за курсором мыши
    env = Environment(pygame, settings_filename='test_settings')
    env.run()
