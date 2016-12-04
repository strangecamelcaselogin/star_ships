from math import sqrt
import numpy as np


def v2is_same(vector1, vector2):
    if vector1[0] == vector2[0] and vector1[1] == vector2[1]:
        return True

    return False


def v2norm(vector):
    return sqrt(vector[0] * vector[0] + vector[1] * vector[1])


def v2unit(vector):
    v_norm = v2norm(vector)
    return vector / v_norm if v_norm != 0 else np.array((0., 0.))


def v2normal(vector):
    # turn to 90 degrees
    return v2unit(np.array((vector[1], -vector[0])))


def v2reflect(vector, normal):
    return -vector + 2 * np.dot(vector, normal) * normal


