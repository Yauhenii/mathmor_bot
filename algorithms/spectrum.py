import io
from PIL import Image
from PIL import ImageOps
import skimage.morphology as morphology
from skimage.morphology import disk, diamond
import numpy as np
from matplotlib import pyplot


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
    area_function = (lambda im: np.sum(im))
    helper_function = (lambda a, b: a - b)
    spectrum_list = get_spectrum(img, str_elem, area_function, helper_function)
    # postprocessing
    return spectrum_list


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
    area_function = (lambda im: np.count_nonzero(im))
    helper_function = (lambda a, b: np.logical_and(a, np.logical_not(b)))
    spectrum_list = get_spectrum(img, str_elem, area_function, helper_function)
    # postprocessing
    return spectrum_list


def get_spectrum(image, str_elem, area_function, helper_function):
    positive = []
    negative = []
    previous = str_elem
    positive.append(area_function(helper_function(image, morphology.opening(image, str_elem))))
    previous_opening = None
    previous_closing = None

    while True:
        if previous_opening is None:
            previous_opening = morphology.opening(image, previous)
        if previous_closing is None:
            previous_closing = morphology.closing(image, previous)

        size = len(previous) + len(str_elem) - 1
        next_element = np.zeros((size, size), dtype=np.bool)
        i = len(str_elem) // 2
        next_element[i: -i, i: -i] = previous

        current = morphology.dilation(next_element, str_elem)
        opening = morphology.opening(image, current)
        closing = morphology.closing(image, current)

        positive.append(area_function(helper_function(previous_opening, opening)))
        negative.append(area_function(helper_function(closing, previous_closing)))

        if np.array_equal(closing, previous_closing) and np.array_equal(opening, previous_opening):
            break

        previous = current
        previous_opening = opening
        previous_closing = closing

    values = negative[::-1] + positive
    return values
