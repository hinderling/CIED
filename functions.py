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
import csv
import math


def load(path):
    """
    Will return two lists of images as np arrays
    path is usually "DATA"
    """
    folders = glob(f"{path}/*")
    allpost = []
    allpre = []
    basenames = []
    for folder in folders:
        allpost.append(np.asarray(Image.open(f"{folder}/{basename(folder)}post.png").convert("L")))
        allpre.append(np.asarray(Image.open(f"{folder}/{basename(folder)}pre.png").convert("L")))
        basenames.append(basename(folder))

    return allpost, allpre, basenames


def preprocess(image):
    """
    apply adaptive histgram equalization, sharpening filter may not be needed

    Pixel values are now floats between 0 and 1
    """
    image = exposure.equalize_adapthist(image)
    return image


def show(image, title=None):
    plt.imshow(image)

    plt.title(title)
    plt.show()


def showhist(image):
    plt.subplot(121)
    plt.imshow(image, cmap=plt.get_cmap('gray'))
    plt.subplot(122)
    plt.hist(image.flatten(), 256, range=(0, 1))
    plt.show()


def binary_filter(image, threshold=False, percentage=0.6, size=15):
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
    binary = binary_opening(binary, selem=disk(size))
    return binary


def distance(p1, p2):
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
            if i != n:
                y1, x1, r = blob1
                y2, x2, r = blob2
                y = y2 - y1
                x = x2 - x1
                v1 = (x, y)
                for v2 in vectors:
                    all_angles.append(angle(v1, v2))
                vectors.append(v1)
        angles[i][1] = max(all_angles)
    angles = angles[angles[:, 1].argsort()][:len(angles)]
    return angles


def angle(v1, v2):
    unit_vector_1 = v1 / np.linalg.norm(v1)
    unit_vector_2 = v2 / np.linalg.norm(v2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    b_angle = np.arccos(dot_product)
    d_angle = b_angle / (2 * math.pi) * 360 #convert to degrees
    return d_angle


def gt(filename):
    """
    get matrix of coordinates of corresponding image
    :param filename: name of corresponding image
    :return: matrix of the format:
    [[1     x1     y1]
     [2     x2     y2]
     [      ...      ]
     [12    x12   y12]
    First row corresponds to the number of the
    electrode starting in the center
    """
    name = f"{filename}post.png"
    out = []
    with open("gt/labels.csv", "r") as csvfile:
        labels = csv.reader(csvfile, delimiter=',')
        for row in labels:
            if row[3] == name:
                out.append(list(map(int, row[0:3])))
    return out


def plot_coordinates(image, coords, title=None):
    """
    :param image: numpy array
    :param title: title to be displayed
    :param coords:

    matrix of the format:
    [[1     x1     y1]
     [2     x2     y2]
     [      ...      ]
     [12    x12   y12]
    :return: None
    """
    fig, ax = plt.subplots(1, 1, figsize=(9, 3), sharex=True, sharey=True)
    ax.set_title(title)
    ax.imshow(image)

    for n, x, y in coords:
        c = plt.Circle((x, y), 20, color='red', linewidth=2, fill=False)
        ax.add_patch(c)

        plt.text(x, y + 40, s=n, fontsize=5, horizontalalignment='center', verticalalignment='center')

    plt.show()
