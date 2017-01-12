import math
import cv2 as cv
from scipy import signal
import numpy as np
from settings_storage import settings


class SpaceMap:
    def __init__(self, pygame, resolution, map_path, debug=False):
        self.pygame = pygame

        # map_path = './map/map_3.png'  # debug only

        scaled_img = self.pygame.image.load(map_path)
        scaled_img = self.pygame.transform.scale(scaled_img, resolution)

        self.map_image = scaled_img
        self.binmap = self.load_binmap(scaled_img.copy())

        # create gradient and tile
        scharr = np.array([[-1 - 1j, 0 - 2j, +1 - 1j],
                           [-2 + 0j, 0 + 0j, +2 + 0j],
                           [-1 + 1j, 0 + 2j, +1 + 1j]])  # ядро свертки

        self.grad = signal.convolve2d(self.binmap, scharr, boundary='symm',
                                      mode='same')  # градиенты по иксу(реальная) и игреку(мнимое)
        # в grad комплексные числа
        # для реальной части обращаться по real
        # для мнимой части обращаться по imag

        # получаем все контуры на изображении
        im2, self.__contours, hierarchy = cv.findContours(self.binmap.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

        if debug:
            cv.imshow('bin map image', self.binmap)
            cv.waitKey(0)

            gradient = np.absolute(self.grad)
            cv.imshow('gradient', gradient)
            cv.waitKey(0)

            image_with_count = self.binmap.copy()
            cv.drawContours(image_with_count, self.__contours, -1, [120])
            cv.imshow('contours', image_with_count)
            cv.waitKey(0)

            cv.destroyAllWindows()

        width, height = settings.DISPLAY_RES #self.binmap.shape[:2]
        self.numbers_tile_in_x = math.ceil(width / settings.TILE_SIZE)  # количество столбцов в матрице тайлов
        self.numbers_tile_in_y = math.ceil(height / settings.TILE_SIZE)  # количество строк в матрице тайлов

        self.point_cntr_in_tile = [[] for _ in range(
            (self.numbers_tile_in_x * self.numbers_tile_in_y))]  # список точек контура на каждый тайл

        self.init_tiles()

    def init_tiles(self):
        # создаем тайлы

        # идем по всем точкам из контура и распределяем их по тайлам
        for contour in self.__contours:
            for point in contour:
                # for i in range(len(c[0])): # для будущей обработки нескольких контуров
                # c[0][0] - координата точки контура по иксу
                # с[0][1] - координата точки контура по игреку

                x_tile = int(point[0][0] // settings.TILE_SIZE)  # номер столбца в матрице тайлов, в котором находится точка контура
                y_tile = int(point[0][1] // settings.TILE_SIZE)  # номер строки в матрице тайлов, в котором находится точка контура

                number = y_tile * self.numbers_tile_in_x + x_tile  # номер самого тайла
                self.point_cntr_in_tile[number].append(point[0])  # добавляем в соотвествующий список точку

    @staticmethod
    def __debug(data2d, filename):
        with open(filename, 'w') as f:
            for line in data2d:
                for sym in line:
                    print(sym, file=f, end=' ')
                print(file=f)

    def load_binmap(self, img):
        pxarray = self.pygame.PixelArray(img).transpose()  # Поворот на 90 градусов

        num_px = np.array(pxarray, dtype=np.uint8)

        for i in range(len(pxarray)):
            for j in range(len(pxarray[i])):
                if pxarray[i][j] == 0:
                    num_px[i][j] = 255
                else:
                    num_px[i][j] = 0

        return num_px
