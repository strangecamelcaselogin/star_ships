from math import sqrt

import numpy as np


def v2norm(vector):
    # Длина вектора
    return sqrt(vector[0] * vector[0] + vector[1] * vector[1])


def v2sqr_norm(vector):
    # Квадрат длины вектора ( для ускорения вычислений )
    return vector[0] * vector[0] + vector[1] * vector[1]


def v2unit(vector):
    # Единичный вектор
    v_norm = v2norm(vector)
    return vector / v_norm if v_norm != 0 else np.array((0., 0.))


def v2normal(vector):
    # Нормаль к вектору
    return v2unit(np.array((vector[1], -vector[0])))


def v2reflect(vector, normal):
    # Вектор-отражение исходного от нормали
    return -vector + 2 * np.dot(vector, normal) * normal
