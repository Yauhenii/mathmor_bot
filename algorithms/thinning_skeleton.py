from PIL import Image
import numpy as np
from scipy.ndimage.morphology import binary_erosion


# SKELETONIZATION WITH THINNING


t1 = np.array([[[True, True, True],
                [False, True, False],
                [False, False, False]],

               [[False, False, False],
                [False, False, False],
                [True, True, True]]])

t5 = np.array([[[False, True, False],
                [False, True, True],
                [False, False, False]],

               [[False, False, False],
                [True, False, False],
                [True, True, False]]])


def skeletonize(img):
    # preprocessing
    img = img.copy()
    img = img.convert('1')
    img = np.array(img)
    img = np.invert(img)
    # skeletonize
    total_n = 0
    while True:
        prev_img = img.copy()
        img = iterate(img, t1)
        img = iterate(img, t5)
        total_n += 1
        if (prev_img == img).all():
            break
    # postprocessing
    skeletonized_img = Image.fromarray(img.astype('uint8'))
    return skeletonized_img, total_n


def iterate(img, t):
    for i in range(0, 4):
        img = thinning_operation(img, t)
        t[0] = np.rot90(t[0])
        t[1] = np.rot90(t[1])
    return img


def cross_operation(x, t):
    return np.logical_and(binary_erosion(x, t[0]), binary_erosion(np.logical_not(x), t[1]))


def thinning_operation(x, t):
    return np.logical_and(x, np.logical_not(cross_operation(x, t)))
