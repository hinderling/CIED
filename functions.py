from glob import glob
from os.path import basename
from PIL import Image
import numpy as np
from skimage import exposure
from skimage.filters.rank import enhance_contrast
from matplotlib import pyplot as plt
from skimage.morphology import disk
from skimage.filters.rank import mean_bilateral


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

def binary_filter(image):
    brightness = np.sum(image)/image.size
    threshold = brightness+0.3
    print(threshold)
    binary = image > threshold
    return binary