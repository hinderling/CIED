from glob import glob
from os.path import basename
from PIL import Image
import numpy as np
from skimage import exposure
from skimage.filters.rank import enhance_contrast
from matplotlib import pyplot as plt
from skimage.morphology import disk
from skimage.filters.rank import mean_bilateral
from math import ceil


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
        allpre.append(np.asarray(Image.open(f"{folder}/{basename(folder)}post.png").convert("L")))

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

def binary_filter(image, threshold = False, percentage = 0.75):
    """
    My binary filter
    :param image:
    :param threshold: set threshold manually
    :param percentage: get brightest percentage of image
    :return:
    """

    print(np.sort(image.flatten()))
    if not threshold:
        ord_img = np.sort(image.flatten())
        value = ceil(len(ord_img) * percentage)
        if value < len(ord_img):
            threshold = ord_img[value]
        else:
            print("threshold too high")
            threshold = 0.5
    binary = image > threshold
    return binary