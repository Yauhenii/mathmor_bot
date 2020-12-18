from PIL import Image
from PIL import ImageOps
import numpy as np


# FILTER

def filter_grayscale_image(img, f_size):
    # preprocess
    img = img.copy()
    img = ImageOps.grayscale(img)
    img = np.array(img)
    filtered_img = filter_image(img, f_size)
    return filtered_img


def filter_binary_image(img, f_size):
    # preprocess
    img = img.copy()
    img = img.convert('1')
    img = np.array(img)
    img = np.invert(img)
    filtered_img = filter_image(img, f_size)
    return filtered_img


def filter_image(img, f_size):
    # filter
    w = img.shape[0]
    h = img.shape[1]

    scaled_img = np.zeros(shape=(w + 2 * f_size - 2, h + 2 * f_size - 2))

    for i in range(w):
        for j in range(h):
            scaled_img[i + f_size - 1][j + f_size - 1] = img[i][j]

    filtered_img = np.zeros(shape=(w, h))
    f = f_size // 2

    for i in range(f, w + f - 1):
        for j in range(f, h + f - 1):
            s = []
            s = sorted(scaled_img[i - f: i + f + 1, j - f: j + f + 1].flatten(), reverse=True)
            filtered_img[i - f][j - f] = s[f_size - 1]

    filtered_img = Image.fromarray(filtered_img.astype('uint8'))
    return filtered_img
