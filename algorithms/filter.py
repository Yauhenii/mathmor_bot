from PIL import Image
from PIL import ImageOps
import numpy as np


# FILTER

def filter_grayscale_image(img, f_size):
    # preprocessing
    img = img.copy()
    img = ImageOps.grayscale(img)
    img = np.array(img)
    # filtration
    filtered_img = filter_image(img, f_size)
    # postprocessing
    filtered_img = Image.fromarray(filtered_img.astype('uint8'))
    return filtered_img


def filter_binary_image(img, f_size):
    # preprocess
    img = img.copy()
    img = img.convert('1')
    img = np.array(img)
    img = np.invert(img)
    # filtration
    filtered_img = filter_image(img, f_size)
    # postprocessing
    filtered_img = Image.fromarray(filtered_img.astype('uint8'))
    filtered_img = ImageOps.invert(filtered_img)
    return filtered_img


def filter_image(img, f_size):
    # filter
    width = img.shape[0]
    height = img.shape[1]

    scaled_img = np.zeros(shape=(width + 2 * f_size - 2, height + 2 * f_size - 2))

    for i in range(width):
        for j in range(height):
            scaled_img[i + f_size - 1][j + f_size - 1] = img[i][j]

    filtered_img = np.zeros(shape=(width, height))
    f = f_size // 2

    for i in range(f, width + f - 1):
        for j in range(f, height + f - 1):
            s = []
            s = sorted(scaled_img[i - f: i + f + 1, j - f: j + f + 1].flatten(), reverse=True)
            filtered_img[i - f][j - f] = s[f_size - 1]

    return filtered_img
