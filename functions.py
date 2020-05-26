########################################################################################################################
# functions.py
# ISIP project 2020 - Cochlea
# Lucien Simon Hinderling, Dona Anna Maria Lerena, Tim Ogi
########################################################################################################################

#     #     #      #####   ###   #####       #     #     #     ######   #######  ###     #     #     #   #####
##   ##    # #    #     #   #   #     #      ##   ##    # #    #     #     #      #     # #    ##    #  #     #
# # # #   #   #   #         #   #            # # # #   #   #   #     #     #      #    #   #   # #   #  #
#  #  #  #     #  #  ####   #   #            #  #  #  #     #  ######      #      #   #     #  #  #  #   #####
#     #  #######  #     #   #   #            #     #  #######  #   #       #      #   #######  #   # #        #
#     #  #     #  #     #   #   #     #      #     #  #     #  #    #      #      #   #     #  #    ##  #     #
#     #  #     #   #####   ###   #####       #     #  #     #  #     #     #     ###  #     #  #     #   #####

########################################################################################################################
# imports
from glob import glob
from os.path import basename
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
from math import ceil, sqrt
import csv
import math
import statistics
from scipy import stats

def load(path, postonly = True):
    """
    Will return two lists of images as np arrays
    path is usually "DATA"
    path: path to folder
    """
    folders = glob(f"{path}/*")
    allpost = []
    allpre = []
    basenames = []
    for folder in folders:
        allpost.append(np.asarray(Image.open(f"{folder}/{basename(folder)}post.png").convert("L")))
        allpre.append(np.asarray(Image.open(f"{folder}/{basename(folder)}pre.png").convert("L")))
        basenames.append(basename(folder))

    if postonly:
        return allpost, basenames
    return allpost, allpre, basenames


def distance(p1, p2):
    """
    Caclulcates distance between two point
    :param p1: (x,y)
    :param p2: (x,y)
    :return: distance
    """
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
    """
    Caclulates angle between two vectors
    :param v1: vector 1
    :param v2: vector 2
    :return: angle
    """
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


def all_angles(coords):
    '''takes a list of all electrodes, of the form
        [electrode nr    x coordinate    y coordinate    if something else comes too thereafter, I dont care]
        just as in gt/labels.csv and returns the spectral center as well as the circular angles'''
    coords.sort()  # electrodes are sometimes not in right order
    center=spectral_center(coords)
    center_to_electrode=coords[11][1]-center[0], coords[11][2]-center[1]
    angles=[0]
    for i in range(10,-1,-1):
        before_center_to_electrode=center_to_electrode
        center_to_electrode=coords[i][1]-center[0], coords[i][2]-center[1]
        new_angle=angles[-1]+angle(before_center_to_electrode, center_to_electrode)
        angles.append(new_angle)
    return center, angles


def distances_and_angles(all_electrodes):
    '''takes a list of all electrodes, of the form
    electrode nr    x coordinate    y coordinate    if something else comes too thereafter, I dont care
    just as in gt/labels.csv
    returns distances and angles starting at the outermost electrode (eg electrode with highest nr)'''
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

#
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


def gt_distances_angles1_and11(images_list):
    '''takes a list of all gt images, returns the distances and angles 1 and 12 of each image'''
    gt_distances = []
    gt_angle1 = []
    gt_angle11=[]
    for image in images_list:
        all_electrodes = gt(str(image))
        all_electrodes.sort()  # electrodes are sometimes not in right order
        electrode_nr, distances, angles = distances_and_angles(all_electrodes)
        gt_angle11.append(angles[0])
        gt_angle1.append(angles[9])
        gt_distances.append(distances)
    # gt_distances is a list of list; I would like to have a simple list instead
    gt_distances = [item for sublist in gt_distances for item in sublist]
    return (gt_distances, gt_angle1, gt_angle11)

def find_confidence(gt_list, plot_title, plot_show=True, confidence_level=0.99):
    '''returns the confidence interval at a confidence level of 0.99 (or whatever, if specified differently) of values
    in a list, assuming a normal distribution.
    If not specified differently, a plot is produced'''
    mean=statistics.mean(gt_list)
    CI_upper=mean+statistics.stdev(gt_list)*stats.norm.ppf((confidence_level+1)/2)
    CI_lower=mean-statistics.stdev(gt_list)*stats.norm.ppf((confidence_level+1)/2)

    if plot_show:
        #plot density histogramms
        #first for distances
        plt.title('{}'.format(plot_title))
        plt.hist(gt_list, bins = 20, density=True)
        # decide from where to where we should compute theoretical distribution
        lnspc = np.linspace(CI_lower, CI_upper, len(gt_list))
        m, s = stats.norm.fit(gt_list) # get mean and standard deviation
        pdf_g = stats.norm.pdf(lnspc, m, s) # now get theoretical values in our interval
        plt.plot(lnspc, pdf_g, label="t-distribution") # plot it
        plt.axvline(mean, color='k', linestyle='dashed', linewidth=1)
        plt.axvline(CI_upper, color='red')
        plt.axvline(CI_lower, color='red')
        plt.show()
    return(CI_lower, CI_upper)

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

def save_csv(angles_all, center_all, names_all, coordinates_all):
    """
    Saves results to csv
    :param angles_all: list of angles
    :param center_all: list of centers
    :param names_all: list of names
    :param coordinates_all: list of coordinates
    :return: None
    """
    lines = [[]] * 13

    for angles, center, name, cords in zip(angles_all, center_all, names_all, coordinates_all):
        lines[0] = lines[0]+[f'{name}_electrodes','x','y','angle','center_x','center_y','']

        print(lines[0])

        for i, (angle, cord) in enumerate(zip(angles, cords)):
            if i == 0:
                cx, cy = center
            else:
                cx, cy = ('','')
            lines[i+1] = lines[i+1] + [cord[0],cord[1],cord[2],angle,cx,cy, '']

    print(lines[0])
    with open('out.csv', 'w', newline='') as out:
        writer = csv.writer(out, delimiter=';')
        writer.writerows(lines)
    return None
