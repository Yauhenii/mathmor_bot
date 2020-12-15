from PIL import Image
import numpy as np
from scipy.ndimage.morphology import binary_erosion


# GETTING CONVEX HULL


t1 = np.array([[[True, True, True],
                [False, False, True],
                [False, False, False]],

               [[False, False, False],
                [False, True, False],
                [False, False, False]]])

t5 = np.array([[[True, True, True],
                [True, False, False],
                [False, False, False]],

               [[False, False, False],
                [False, True, False],
                [False, False, False]]])


def get_convex_hull(img):
    # preprocess
    img = img.copy()
    img = img.convert('1')
    img = np.array(img)
    img = np.logical_not(img)
    # getting convex hull
    total_n = 0
    while True:
        prev_img = img.copy()
        img = iterate(img, t1)
        img = iterate(img, t5)
        total_n += 1
        if (prev_img == img).all():
            break
    hull_img = Image.fromarray(img.astype('uint8'))
    return hull_img, total_n


def iterate(img, t):
    for i in range(0, 4):
        img = thickening_operation(img, t)
        t[0] = np.rot90(t[0])
    return img


def cross_operation(x, t):
    return np.logical_and(binary_erosion(x, t[0]), binary_erosion(np.logical_not(x), t[1]))


def thickening_operation(x, t):
    return np.logical_or(x, cross_operation(x, t))
