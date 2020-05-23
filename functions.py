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
from gt.parameters import DISTANCES, ANGLES
from math import ceil, floor
import statistics


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
     [12    x12   y12]]
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

def spectral_center(coords):
    #vector from electrode 1 to electrode 2
    v1=np.array([coords[1][1]-coords[0][1],coords[1][2]-coords[0][2]])
    #corresponding normal vector
    n1=np.array([v1[1], -v1[0]])
    #middle between electrode 1 and 2
    M1=np.array([(coords[0][1]+coords[1][1])/2,(coords[0][2]+coords[1][2])/2])

    #vector from electrode 2 to electrode 3
    v2=np.array([coords[2][1]-coords[1][1], coords[2][2]-coords[1][2]])
    # corresponding normal vector
    n2=np.array([v2[1], -v2[0]])
    # middle between electrode 1 and 2
    M2=np.array([coords[1][1] + 0.5 * v2[0], coords[1][2] + 0.5 * v2[1]])

    #we want to find where M1+s*n1=M2+r*n2 --> solve for s and r:
    r=(M1[1]*n1[0]+(M2[0]-M1[0])*n1[1]-M2[1]*n1[0])/(n2[1]*n1[0]-n2[0]*n1[1])
    s=(M2[0]-M1[0]+r*n2[0])/n1[0]
    center=M1+s*n1
    return (center)


def all_angles(image):
    coords=gt(image)
    coords.sort()  # electrodes are sometimes not in right order
    center=spectral_center(coords)
    center_to_electrode=coords[11][1]-center[0], coords[11][2]-center[1]
    angles=[0]
    for i in range(10,-1,-1):
        before_center_to_electrode=center_to_electrode
        center_to_electrode=coords[i][1]-center[0], coords[i][2]-center[1]
        new_angle=angles[-1]+angle(before_center_to_electrode, center_to_electrode)
        angles.append(new_angle)
    return angles


def distances_and_angles(all_electrodes):
    '''takes a list of all electrodes, of the form
    electrode nr    x coordinate    y coordinate    if something else comes too thereafter, I dont care
    just as in gt/labels.csv'''
    all_electrodes.sort() #at least in gt/labels.csv it is sometimes not sorted
    #start at outermost electrode
    electrode_nr=[]
    distances=[]
    angles=[]
    #as angles can only be calculated between 2 vectors, there will be one less angle than distances & 2 less than
    # electrodes
    v = np.array([all_electrodes[11][1] - all_electrodes[10][1], all_electrodes[11][2] - all_electrodes[10][2]])
    v_length=np.linalg.norm(v)
    distances.append(v_length)
    electrode_nr.append(11) #nr 11 corresponds to distance between electrode 12 and 11
    for i in range(len(all_electrodes)-2,0,-1):
        v2 = np.array([all_electrodes[i][1] - all_electrodes[i-1][1], all_electrodes[i][2] - all_electrodes[i-1][2]])
        v2_length = np.linalg.norm(v2)
        distances.append(v2_length)
        angles.append(angle(v,v2))
        v=v2
        electrode_nr.append(i)
    return(electrode_nr,distances, angles)
 #
def plot_distances_angles(all_electrodes):
    '''takes a list of all electrodes, of the form
        electrode nr    x coordinate    y coordinate    if something else comes too thereafter, I dont care
        just as in gt/labels.csv'''
    electrode_nr, distances, angles=distances_and_angles(all_electrodes)
    plt.subplot(121)
    plt.plot(electrode_nr, distances)
    plt.subplot(122)
    plt.plot(electrode_nr[:-1], angles)
    plt.show()


def plot_gt_distances_angles(images_list):
    '''takes a list of all gt images, returns the mean and std for the distances and angles between the electrodes
    & also plots this'''
    gt_distances = []
    gt_angles = []
    for image in images_list:
        all_electrodes = gt(str(image))
        all_electrodes.sort()  # electrodes are sometimes not in right order
        electrode_nr, distances, angles = distances_and_angles(all_electrodes)
        gt_angles.append(angles)
        gt_distances.append(distances)

    #calculate mean and std for the distances for every electrode
    mean_gt_dist=[]
    std_gt_dist=[]
    for i in range(len(distances)): #ie for each of the edges between the electrodes
        particular_electrode_gt_distances=[]
        for x in range(len(images_list)): #ie for each of the images
            particular_electrode_gt_distances.append(gt_distances[x][i])
        mean_gt_dist.append(statistics.mean(particular_electrode_gt_distances))
        std_gt_dist.append(statistics.stdev(particular_electrode_gt_distances))

    #same for the angle
    mean_gt_angles = []
    std_gt_angles = []
    for i in range(len(angles)):  # ie for each of the angles between the edges connecting the electrodes
        particular_electrode_gt_angles = []
        for x in range(len(images_list)):  # ie for each of the images
            particular_electrode_gt_angles.append(gt_angles[x][i])
        mean_gt_angles.append(statistics.mean(particular_electrode_gt_angles))
        std_gt_angles.append(statistics.stdev(particular_electrode_gt_angles))

    plt.subplot(121)
    plt.xlabel('electrode nr.')
    plt.ylabel('mean distance')
    plt.title('dist between electrodes')
    plt.plot(electrode_nr, mean_gt_dist) #this plot actually shows the distance between the electrode on the x axis
    #and the electrode thereafter
    plt.xticks(range(min(electrode_nr), max(electrode_nr)+1, 1))
    plt.subplot(122)
    plt.xlabel('electrode nr.')
    plt.ylabel('mean angle')
    plt.title('angles between electrode edges')
    plt.plot(electrode_nr[:-1], mean_gt_angles) #this plot shows the angle between the edge (electrode x-1--> x) and the
    #edge (electrode(x--> x+1), ie x only from 2 to 11 possible
    plt.xticks(range(min(electrode_nr[:-1]), max(electrode_nr[:-1]) + 1, 1))
    plt.suptitle('Mean of ground truth data')
    plt.show()

    return (mean_gt_dist, mean_gt_angles)


def image_names_gt():
    """
    get list of image names
    """
    out = []
    with open("gt/labels.csv", "r") as csvfile:
        labels = csv.reader(csvfile, delimiter=',')
        for row in labels:
            out.append(row[3][:4])
    out=list(set(out)) #keep only unique values in list
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

        plt.text(x, y + 40, s=int(n), fontsize=5, horizontalalignment='center', verticalalignment='center')

    plt.show()

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


