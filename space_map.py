from PIL import Image
import cv2 as cv
import math
from scipy import signal
import numpy as np


class SpaceMap:
    def __init__(self, pygame, resolution, map_path):
        self.pygame = pygame

        map_path = './map/test3.png'  # TODO !!!

        scaled_img = self.pygame.image.load(map_path)
        scaled_img = self.pygame.transform.scale(scaled_img, resolution)

        self.map_image = scaled_img.copy()

        # scaled_img = scaled_img.convert()  # Убрать альфа канал

        # self.binmap = self.load_binmap(scaled_img)

        # create gradient and tile

        self.binmap = self.load_binmap(scaled_img)  # cv.imread('./map/map2.png')
        # self.image = cv.cvtColor(self.image, cv.COLOR_BGR2image)
        # print(self.image[100], type(self.image[100][200]))

        scharr = np.array([[-1 - 1j, 0 - 2j, +1 - 1j],
                           [-2 + 0j, 0 + 0j, +2 + 0j],
                           [-1 + 1j, 0 + 2j, +1 + 1j]])  # ядро свертки

        self.grad = signal.convolve2d(self.binmap, scharr, boundary='symm',
                                      mode='same')  # градиенты по иксу(реальная) и игреку(мнимое)
        # в grad комплексные числа
        # для реальной части обращаться по real
        # для мнимой части обращаться по imag

        self.gradient = np.absolute(self.grad)
        cv.imshow('image', self.gradient)
        cv.waitKey(0)
        cv.destroyAllWindows()

        im2, self.contours, hierarchy = cv.findContours(self.binmap, cv.RETR_TREE,
                                                        cv.CHAIN_APPROX_SIMPLE)  # получаем все контуры на изображении

        # image_with_count = self.image.copy()
        # cv.drawContours(image_with_count, self.contours, -1, [120])
        # cv.imshow('image', image_with_count)
        # cv.waitKey(0)
        # cv.destroyAllWindows()

        # TODO ---
        self.numbers_tile_in_x = 5  # количество столбцов в матрице тайлов
        self.numbers_tile_in_y = 5  # количество строк в матрице тайлов
        self.tile = np.zeros((self.numbers_tile_in_x, self.numbers_tile_in_y), dtype=list)  # координаты левого верхнего
        # и правого нижнего углов тайла

        self.point_cntr_in_tile = [[] for i in range(
            (self.numbers_tile_in_x * self.numbers_tile_in_y))]  # список точек контура на каждый тайл
        self.create_tile()

    def create_tile(self):
        # создаем тайлы

        # quantity = self.numbers_tile_in_x * self.numbers_tile_in_y
        height, width = self.binmap.shape[:2]
        delta_h = height / self.numbers_tile_in_y  # высота тайла
        delta_w = width / self.numbers_tile_in_x  # длина тайла

        tile_x = [0]  # координаты тайлов по иксу
        for i in range(1, self.numbers_tile_in_x + 1, 1):
            tile_x.append(tile_x[i - 1] + delta_w)

        tile_y = [0]  # координаты тайлов по игреку
        for i in range(1, self.numbers_tile_in_y + 1, 1):
            tile_y.append(tile_y[i - 1] + delta_h)

        # заполняем матрицу координат углов тайлов (будет нужна для отрисовки)
        for i in range(self.numbers_tile_in_y):
            for j in range(self.numbers_tile_in_x):
                left_top = [tile_x[j], tile_y[i]]
                right_down = [tile_x[j + 1], tile_y[i + 1]]
                self.tile[i][j] = [left_top, right_down]

        # идем по всем точкам из контура и распределяем их по тайлам
        for c in self.contours[0]:
            # for i in range(len(c[0])):
            # c[0][0] - координата точки контура по иксу
            # с[0][1] - координата точки контура по игреку
            x_tile = int(c[0][0] // delta_w)  # номер столбца в матрице тайлов, в котором находится точка контура
            y_tile = int(c[0][1] // delta_h)  # номер строки в матрице тайлов, в котором находится точка контура
            number = y_tile * self.numbers_tile_in_x + x_tile  # номер самого тайла
            self.point_cntr_in_tile[number].append(c[0])  # добавляем в соотвествующий список точку

            # print(self.point_cntr_in_tile)

    def check_number_tile(self, x, y):
        # проверяем, в каком тайле находится объект
        # передаем координаты центра объекта

        height, width = self.binmap.shape[:2]
        delta_h = height / self.numbers_tile_in_y
        delta_w = width / self.numbers_tile_in_x

        x_tile = int(x // delta_w)
        y_tile = int(y // delta_h)

        number = y_tile * self.numbers_tile_in_x + x_tile
        # print(number)
        point_contour = self.point_cntr_in_tile[number]

        return point_contour  # возвращаем список точек контура в тайле, в котором находится объект

    def draw_line_segment(self):
        # рисуем сетку

        height, width = self.binmap.shape[:2]
        delta_h = int(height / self.numbers_tile_in_y)
        delta_w = int(width / self.numbers_tile_in_x)
        for i in range(1, self.numbers_tile_in_x, 1):
            start = (i * delta_w, 0)
            finish = (i * delta_w, height)
            cv.line(self.binmap, start, finish, (0, 255, 0), 1)

        for i in range(1, self.numbers_tile_in_y, 1):
            start = (0, i * delta_h)
            finish = (width, i * delta_h)
            cv.line(self.binmap, start, finish, (0, 255, 0), 1)

        cv.imshow('image', self.binmap)
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

        # TODO BUGS
        num_px = np.array(pxarray, dtype=np.uint8)

        self.debug(num_px, 'num_px.txt')
        self.debug(pxarray, 'pxarray.txt')

        #np.place(num_px, num_px == 0, [255])  # заменять на пошаговую  обработку
        #np.place(num_px, ((num_px > 256) or (num_px < 0)), [0])

        return num_px
