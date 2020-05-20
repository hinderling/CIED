from functions import *

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

print(all_angles('ID03'))
print(np.diff(all_angles('ID03')))