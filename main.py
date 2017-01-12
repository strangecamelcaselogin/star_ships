import pygame

from environment import Environment


if __name__ == '__main__':
    env = Environment(pygame, settings_filename='test_settings', debug=True)
    env.run()
