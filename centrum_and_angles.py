from functions import *
import statistics

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

#print(all_angles('ID03'))
#print(np.diff(all_angles('ID03')))

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
            if row[3] not in out:
                out.append(row[3][:4])
    return out

#to plot ground truth data
print(plot_gt_distances_angles(image_names_gt()))
#plot_distances_angles([[1,20,20], [2,15,15], [3,0,15], [4, 0,10],[5,0,5],[6,0,0],[7,-5,0],[8,-5,-5],[9,-5,-10],[10,-5,-15], [11,-5,-20],[12,-5,-21]])