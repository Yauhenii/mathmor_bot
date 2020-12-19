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
    temp_width = width + 2 * f_size - 2
    temp_height = height + 2 * f_size - 2

    temp_img = np.zeros((temp_width, temp_height))
    for i in range(width):
        for j in range(height):
            temp_img[i + f_size - 1][j + f_size - 1] = img[i][j]

    filtered_img = np.zeros((width, height))
    for i in range(width):
        for j in range(height):
            array = temp_img[i: i + f_size + 1, j: j + f_size + 1].flatten()
            array = np.sort(array)
            array = array[::-1]
            filtered_img[i][j] = array[f_size - 1]

    return filtered_img
