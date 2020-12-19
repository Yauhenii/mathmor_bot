from PIL import ImageOps
from PIL import Image


# UTILS

def invert_image(img):
    img = ImageOps.invert(img)
    return img


def to_grayscale(img):
    img = ImageOps.grayscale(img)
    return img


def to_binary(img, threshold=128):
    img = img.convert('L').point(lambda x: 255 if x > threshold else 0, mode='1')
    return img
