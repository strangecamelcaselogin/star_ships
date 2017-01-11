from PIL import Image
import math
import cv2 as cv
from scipy import signal
import numpy as np
from settings_storage import settings


class SpaceMap:
    def __init__(self, pygame, resolution, map_path):
        self.pygame = pygame

        map_path = './map/test3.png'  # TODO !!!

        scaled_img = self.pygame.image.load(map_path)
        scaled_img = self.pygame.transform.scale(scaled_img, resolution)

        self.map_image = scaled_img.copy()

        self.binmap = self.load_binmap(scaled_img)

        # create gradient and tile
        scharr = np.array([[-1 - 1j, 0 - 2j, +1 - 1j],
                           [-2 + 0j, 0 + 0j, +2 + 0j],
                           [-1 + 1j, 0 + 2j, +1 + 1j]])  # ядро свертки

        self.grad = signal.convolve2d(self.binmap, scharr, boundary='symm',
                                      mode='same')  # градиенты по иксу(реальная) и игреку(мнимое)
        # в grad комплексные числа
        # для реальной части обращаться по real
        # для мнимой части обращаться по imag

        self.gradient = np.absolute(self.grad)
        # cv.imshow('image', self.gradient)
        # cv.waitKey(0)
        # cv.destroyAllWindows()

        im2, self.contours, hierarchy = cv.findContours(self.binmap, cv.RETR_TREE,
                                                        cv.CHAIN_APPROX_NONE)  # получаем все контуры на изображении

        image_with_count = self.binmap.copy()
        cv.drawContours(image_with_count, self.contours, -1, [120])
        cv.imshow('image', image_with_count)
        cv.waitKey(0)
        cv.destroyAllWindows()

        height, width = self.binmap.shape[:2]
        self.numbers_tile_in_x = math.ceil(width / settings.TILE_SIZE)  # количество столбцов в матрице тайлов
        self.numbers_tile_in_y = math.ceil(height / settings.TILE_SIZE)  # количество строк в матрице тайлов

        self.tile = np.zeros((self.numbers_tile_in_x, self.numbers_tile_in_y), dtype=list)  # координаты левого верхнего
        # и правого нижнего углов тайла

        print(len(self.contours[0]))

        self.point_cntr_in_tile = [[] for i in range(
            (self.numbers_tile_in_x * self.numbers_tile_in_y))]  # список точек контура на каждый тайл

        self.create_tile()
        # self.draw_line_segment()

    def create_tile(self):
        # создаем тайлы

        delta = settings.TILE_SIZE  # высота тайла

        tile_x = [delta * i for i in range(self.numbers_tile_in_x + 1)]
        tile_y = [delta * i for i in range(self.numbers_tile_in_y + 1)]

        # заполняем матрицу координат углов тайлов (будет нужна для отрисовки)
        for i in range(self.numbers_tile_in_y):
            for j in range(self.numbers_tile_in_x):
                left_top = [tile_x[j], tile_y[i]]
                right_down = [tile_x[j + 1], tile_y[i + 1]]
                self.tile[j][i] = [left_top, right_down]

        # идем по всем точкам из контура и распределяем их по тайлам
        for c in self.contours[0]:
            # for i in range(len(c[0])): # для будущей обработки нескольких контуров
            # c[0][0] - координата точки контура по иксу
            # с[0][1] - координата точки контура по игреку

            x_tile = int(c[0][0] // delta)  # номер столбца в матрице тайлов, в котором находится точка контура
            y_tile = int(c[0][1] // delta)  # номер строки в матрице тайлов, в котором находится точка контура

            number = y_tile * self.numbers_tile_in_x + x_tile  # номер самого тайла
            self.point_cntr_in_tile[number].append(c[0])  # добавляем в соотвествующий список точку

    def draw_line_segment(self):
        # рисуем сетку

        height, width = self.binmap.shape[:2]
        delta = settings.TILE_SIZE

        for i in range(1, self.numbers_tile_in_x, 1):
            start = (i * delta, 0)
            finish = (i * delta, height)
            cv.line(self.binmap, start, finish, (100), 1)

        for i in range(1, self.numbers_tile_in_y, 1):
            start = (0, i * delta)
            finish = (width, i * delta)
            cv.line(self.binmap, start, finish, (100), 1)

        cv.imshow('segment', self.binmap)
        cv.waitKey(0)
        cv.destroyAllWindows()

    @staticmethod
    def debug(data2d, filename):
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

        # self.debug(num_px, 'num_px.txt')
        # self.debug(pxarray, 'pxarray.txt')

        return num_px
