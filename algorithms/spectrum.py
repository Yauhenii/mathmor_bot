from PIL import ImageOps
from skimage.morphology import disk, diamond
from skimage.morphology import opening, closing, dilation
import numpy as np


# SPECTRUM

def get_spectrum_grayscale_image(img, str_elem_name, str_elem_size):
    if str_elem_name == 'disk':
        str_elem = disk(str_elem_size, dtype=np.bool)
    elif str_elem_name == 'diamond':
        str_elem = diamond(str_elem_size, dtype=np.bool)
    # preprocess
    img = img.copy()
    img = ImageOps.grayscale(img)
    img = ImageOps.invert(img)
    img = np.array(img)
    # get spectrum
    spectrum_list = get_spectrum(img, str_elem, grayscale_operation)
    # postprocessing
    return spectrum_list


def grayscale_operation(img1, img2):
    return np.sum(img1-img2)


def get_spectrum_binary_image(img, str_elem_name, str_elem_size):
    if str_elem_name == 'disk':
        str_elem = disk(str_elem_size)
    elif str_elem_name == 'diamond':
        str_elem = diamond(str_elem_size)
    # preprocess
    img = img.copy()
    img = img.convert('1')
    img = np.array(img)
    img = np.invert(img)
    # get spectrum
    spectrum_list = get_spectrum(img, str_elem, binary_operation)
    # postprocessing
    return spectrum_list


def binary_operation(img1, img2):
    return np.count_nonzero(np.logical_and(img1, np.logical_not(img2)))


def get_spectrum(img, str_elem, operation):
    p_list = []
    n_list = []
    p_list.append(operation(img, opening(img, str_elem)))
    previous_str_elem = str_elem
    previous_opening = None
    previous_closing = None

    while True:
        if previous_opening is None:
            previous_opening = opening(img, previous_str_elem)
        if previous_closing is None:
            previous_closing = closing(img, previous_str_elem)

        size = len(previous_str_elem) + len(str_elem) - 1
        next_elem = np.zeros((size, size), dtype=np.bool)
        sub = len(str_elem) // 2
        next_elem[sub: -sub, sub: -sub] = previous_str_elem

        current_str_elem = dilation(next_elem, str_elem)
        current_opening = opening(img, current_str_elem)
        current_closing = closing(img, current_str_elem)

        p_list.append(operation(previous_opening, current_opening))
        n_list.append(operation(current_closing, previous_closing))

        if np.array_equal(current_opening, previous_opening) and np.array_equal(current_closing, previous_closing):
            break

        previous_str_elem = current_str_elem
        previous_opening = current_opening
        previous_closing = current_closing

    spectrum_list = n_list[::-1] + p_list
    return spectrum_list
