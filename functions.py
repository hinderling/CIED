from glob import glob
from os.path import basename
from PIL import Image
import numpy as np
from skimage import exposure
from skimage.filters.rank import enhance_contrast
from matplotlib import pyplot as plt
from skimage.morphology import disk, binary_opening, skeletonize
from skimage.filters.rank import mean_bilateral
from math import ceil, sqrt
from skimage.morphology import disk, binary_dilation


def open(path):
    """
    Will return two lists of images as np arrays
    path is usually "DATA"
    """
    folders = glob(f"{path}/*")
    allpost = []
    allpre = []
    for folder in folders:
        allpost.append(np.asarray(Image.open(f"{folder}/{basename(folder)}post.png").convert("L")))
        allpre.append(np.asarray(Image.open(f"{folder}/{basename(folder)}pre.png").convert("L")))

    return allpost, allpre

def preprocess(image):
    """
    apply adaptive histgram equalization, sharpening filter may not be needed

    Pixel values are now floats between 0 and 1
    """
    image = exposure.equalize_adapthist(image)
    return image


def show(image, title = None):

    plt.imshow(image)

    plt.title(title)
    plt.show()



def showhist(image):
    plt.subplot(121)
    plt.imshow(image, cmap=plt.get_cmap('gray'))
    plt.subplot(122)
    plt.hist(image.flatten(), 256, range=(0, 1))
    plt.show()

def binary_filter(image, threshold = False, percentage = 0.6, size = 15):
    """
    :param image:
    :param threshold: set threshold manually
    :param percentage: get brightest percentage of image
    :return:
    """
    if not threshold:
        ord_img = np.sort(image.flatten())
        value = ceil(len(ord_img) * percentage)
        if value < len(ord_img):
            threshold = ord_img[value]
        else:
            print("threshold too high")
            threshold = 0.5
    binary = image > threshold
    binary = binary_opening(binary,selem=disk(size))
    return binary

def distance(p1,p2):
    distance = sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))
    return distance

def angles(blobs):
    """
    most inefficient piece of code ever
    :param blobs:
    :return:
    """
    angles = np.zeros((len(blobs), 2))
    for i, blob1 in enumerate(blobs):
        angles[i][0] = int(i)
        vectors = []
        all_angles = []
        for n, blob2 in enumerate(blobs):
            if i !=  n:
                y1, x1, r = blob1
                y2, x2, r = blob2
                y = y2-y1
                x = x2-x1
                v1 = (x,y)
                for v2 in vectors:
                    all_angles.append(angle(v1, v2))
                vectors.append(v1)
        angles[i][1] = max(all_angles)
    angles = angles[angles[:, 1].argsort()][:len(angles)]
    return angles

def angle(v1,v2):
    unit_vector_1 = v1 / np.linalg.norm(v1)
    unit_vector_2 = v2 / np.linalg.norm(v2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    angle = np.arccos(dot_product)
    return angle