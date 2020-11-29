from PIL import Image
import numpy as np
from skimage.morphology import binary_erosion, binary_dilation
from skimage.morphology import disk, diamond

# SKELETONIZATION AND RESTORING

def skeletonize_n_restore(img, str_elem_name='disk', str_elem_size=3):
    if str_elem_name == 'disk':
        str_elem = disk(str_elem_size)
    elif str_elem_name == 'diamond':
        str_elem = diamond(str_elem_size)

    img = img.convert('1')
    img = np.array(img)
    img = np.invert(img)
    # skeletonize
    s_list, res, n_total = get_skeleton(img, str_elem)
    skeletonized_img = Image.fromarray(res.astype('uint8'))
    # restore
    res = get_restored(res, s_list, str_elem)
    res = np.invert(res)
    restored_img = Image.fromarray(res.astype('uint8'))

    return skeletonized_img, restored_img, n_total


def get_skeleton(img, str_elem):
    # step 1
    n = 0
    y1 = img.copy()
    s_list = []
    while True:
        # step 2
        y2 = binary_erosion(y1, str_elem)
        # step 3
        if np.all(y2 <= 0):
            total_n = n
            s_list.append(y1)
            break
        # step 4
        y3 = binary_dilation(y2, str_elem)
        # step 5
        s_list.append(np.bitwise_xor(y1, y3))
        # step 6
        n += 1
        y1 = y2
        res = np.zeros((len(img[:, 1]), len(img[1, :])))

        for s in s_list:
            res += s

    return s_list, res, total_n


def get_restored(img, s_list, str_elem):
    # step 1
    res = np.zeros(img.shape)
    for i in range(len(s_list)):
        # step 2
        res = np.logical_or(res, s_list[len(s_list) - 1 - i])
        # step 3
        res = binary_dilation(res, str_elem)
    return res
