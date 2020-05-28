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
from math import ceil, floor
import statistics

def preprocess(image):
    """
    apply adaptive histgram equalization, sharpening filter may not be needed

    Pixel values are now floats between 0 and 1
    """
    image = exposure.equalize_adapthist(image)
    return image

def show(image, title=None):
    """
    Show image
    :param image: numpy image
    :param title: Title
    :return: None
    """
    plt.imshow(image)
    plt.title(title)
    plt.show()
    return None


def showhist(image):
    """
    Display histogram for image
    :param image: numpy image
    :return: None
    """
    plt.subplot(121)
    plt.imshow(image, cmap=plt.get_cmap('gray'))
    plt.subplot(122)
    plt.hist(image.flatten(), 256, range=(0, 1))
    plt.show()
    return None


def binary_filter(image, threshold=False, percentage=0.6, size=15):
    """
    :param image:
    :param threshold: set threshold manually
    :param percentage: get brightest percentage of image
    :return: biary mask
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

def order(blobs, tolerance = 0, blob = True):
    """
    :param blobs: Result from blob detection
    :return:
        matrix of the format:
    [[1     x1     y1]
     [2     x2     y2]
     [      ...      ]
     [12    x12   y12]
    """
    chain = []
    options = []

    if blob:

        angles_vec = angles(blobs)
        start = int(angles_vec[0][0])
        for i, blob in enumerate(blobs):
            y, x, r = blob
            if i == start:
                chain.append((x, y))
            else:
                options.append((x, y))
    else:

        for i, element in enumerate(blobs):
            c,x,y = element
            if i == 11:
                chain.append((x, y))
            # elif i == 10:
            else:
                options.append((x, y))

    all_chains = []
    all_options = []
    # find second point(s)
    edge = 0
    # ground truth
    min_dist = DISTANCES[edge][0]
    max_dist = DISTANCES[edge][1]
    mean_dist = DISTANCES[edge][1]

    for option in options:



        last = chain[-1]
        l = distance(last, option)


        if floor(min_dist)-(mean_dist*tolerance/100) < l < ceil(max_dist)+(mean_dist*tolerance/100):
            temp_chain = chain.copy()
            temp_chain.append(option)
            temp_options = options.copy()
            temp_options.remove(option)
            all_chains.append(temp_chain)
            all_options.append(temp_options)

    if len(all_chains) == 0:
        print("Order of points could not be determined")
        numbers = [x + 1 for x in range(len(chain))]
        chain = np.column_stack([numbers, chain])
        return chain
    # else:
    #     chain = all_chains[0]
    # numbers = [x + 1 for x in range(len(chain))]
    # chain = np.column_stack([numbers, chain])
    # return chain


    # find 3rd - 12th points
    while all_chains:
        options = all_options.pop()
        chain = all_chains.pop()
        edge = len(chain)-1
        # ground truth
        min_dist = DISTANCES[edge][0]
        max_dist = DISTANCES[edge][1]
        mean_dist = DISTANCES[edge][2]
        min_angle = DISTANCES[edge - 1][0]
        max_angle = DISTANCES[edge - 1][1]
        mean_angle = DISTANCES[edge - 1][2]

        # comparing angles
        x1, y1 = chain[-2]
        x2, y2 = chain[-1]

        for option in options:
            x3, y3 = option

            y_v1 = y2 - y1
            x_v1 = x2 - x1
            v1 = (x_v1, y_v1)

            y_v2 = y3 - y2
            x_v2 = x3 - x2
            v2 = (x_v2, y_v2)

            a = angle(v1, v2)

            l = distance((x2, y2), option)

            if floor(min_dist)-(mean_dist*tolerance/100) < l < ceil(max_dist)+(mean_dist*tolerance/100) \
                    and floor(min_angle)-(mean_angle*tolerance/100) < a < ceil(max_angle)+(mean_angle*tolerance/100):
                temp_chain = chain.copy()
                temp_options = options.copy()
                temp_chain.append(option)
                temp_options.remove(option)
                all_chains.append(temp_chain)
                all_options.append(temp_options)
                if len(temp_chain) == 12:
                    print("success")
                    chain = temp_chain
                    numbers = [x + 1 for x in range(len(chain))]
                    chain = np.column_stack([numbers, chain])
                    return chain
        print(len(all_chains))


    print("Order of points could not be determined")
    numbers = [x+1 for x in range(len(chain))]
    chain = np.column_stack([numbers, chain])
    return chain


