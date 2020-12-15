from PIL import Image
import numpy as np
from skimage.morphology import binary_erosion, binary_dilation
from scipy.ndimage.morphology import binary_erosion as binary_erosion_2
from skimage.morphology import disk, diamond


# SKELETONIZATION AND RESTORING

class MorphologicalSkeleton:

    @staticmethod
    def skeletonize_n_restore(img, str_elem_name='disk', str_elem_size=3):
        if str_elem_name == 'disk':
            str_elem = disk(str_elem_size)
        elif str_elem_name == 'diamond':
            str_elem = diamond(str_elem_size)

        # preprocess
        img = img.copy()
        img = img.convert('1')
        img = np.array(img)
        img = np.invert(img)
        # skeletonize
        s_list, res, total_n = MorphologicalSkeleton.get_skeleton(img, str_elem)
        skeletonized_img = Image.fromarray(res.astype('uint8'))
        # restore
        res = MorphologicalSkeleton.get_restored(res, s_list, str_elem, total_n)
        res = np.invert(res)
        restored_img = Image.fromarray(res.astype('uint8'))

        return skeletonized_img, restored_img, total_n

    @staticmethod
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

    @staticmethod
    def get_restored(img, s_list, str_elem, total_n):
        n = total_n
        # step 1
        res = np.zeros(img.shape)
        while True:
            # step 2
            res = np.logical_or(res, s_list[n])
            if n == 0:
                break
            # step 3
            res = binary_dilation(res, str_elem)
            # step 4
            n -= 1
        return res


# SKELETONIZATION WITH THINNING

class Skeleton:
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

    @staticmethod
    def skeletonize(img):
        # preprocess
        img = img.copy()
        img = img.convert('1')
        img = np.array(img)
        img = np.invert(img)
        # skeletonize
        total_n = 0
        while True:
            prev_img = img.copy()
            img = Skeleton.iterate(img, Skeleton.t1)
            img = Skeleton.iterate(img, Skeleton.t5)
            total_n += 1
            if (prev_img == img).all():
                break
        skeletonized_img = Image.fromarray(img.astype('uint8'))
        return skeletonized_img, total_n

    @staticmethod
    def iterate(img, t):
        for i in range(0, 4):
            img = Skeleton.thinning_operation(img, t)
            t[0] = np.rot90(t[0])
            t[1] = np.rot90(t[1])
        return img

    @staticmethod
    def cross_operation(x, t):
        return np.logical_and(binary_erosion(x, t[0]), binary_erosion(np.logical_not(x), t[1]))

    @staticmethod
    def thinning_operation(x, t):
        return np.logical_and(x, np.logical_not(Skeleton.cross_operation(x, t)))


# GETTING CONVEX HULL

class ConvexHull:
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

    @staticmethod
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
            img = ConvexHull.iterate(img, ConvexHull.t1)
            img = ConvexHull.iterate(img, ConvexHull.t5)
            total_n += 1
            if (prev_img == img).all():
                break
        hull_img = Image.fromarray(img.astype('uint8'))
        return hull_img, total_n

    @staticmethod
    def iterate(img, t):
        for i in range(0, 4):
            img = ConvexHull.thickening_operation(img, t)
            t[0] = np.rot90(t[0])
        return img

    @staticmethod
    def cross_operation(x, t):
        return np.logical_and(binary_erosion_2(x, t[0]), binary_erosion_2(np.logical_not(x), t[1]))

    @staticmethod
    def thickening_operation(x, t):
        return np.logical_or(x, ConvexHull.cross_operation(x, t))
