import pygame

from environment import Environment


if __name__ == '__main__':
    # TODO колизии и их разрешение
    env = Environment(pygame, settings_filename='test_settings', debug=True)
    env.run()
