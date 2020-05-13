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
        allpost.append(np.asarray(Image.open(f"{folder}/{basename(folder)}post.png")))
        allpre.append(np.asarray(Image.open(f"{folder}/{basename(folder)}post.png")))

    return allpost, allpre

def preprocess(image):
    """
    apply adaptive histgram equalization, sharpening filter may not be needed
    """
    image = exposure.equalize_adapthist(image)
    return image


def show(image):
    plt.imshow(image, cmap=plt.get_cmap('gray'))
    plt.show()