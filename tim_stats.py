from functions import *
from statistics import stdev, mean

allpost, allpre, basenames = load("DATA")


all_distances=[]
all_angle_values=[]


for image, name in zip(allpost,basenames):
    # load ground truth
    ground_truth = gt(name)
    ground_truth.sort()
    ground_truth.reverse()
    distances = []
    angle_value = []

    # distances
    for i in range(11):
        p1 = ground_truth[i]
        p2 = ground_truth[i+1]

        c, x1, y1 = p1
        c, x2, y2 = p2

        distances.append(distance((x1,y1), (x2,y2)))

    all_distances.append(distances)

    # angles
    for i in range(10):
        c, x1,y1 = ground_truth[i]
        c, x2,y2 = ground_truth[i+1]
        c, x3,y3 = ground_truth[i+2]

        y_v1 = y2 - y1
        x_v1 = x2 - x1
        v1 = (x_v1, y_v1)

        y_v2 = y3 - y2
        x_v2 = x3 - x2
        v2 = (x_v2, y_v2)

        angle_value.append(angle(v1,v2))

    all_angle_values.append(angle_value)

result_distances = []
for i in range(11):
    values = []
    for d in all_distances:
        values.append(d[i])
    result_distances.append((min(values),max(values),mean(values)))

result_angles = []
for i in range(10):
    values = []
    for d in all_angle_values:
        values.append(d[i])
    result_angles.append((min(values),max(values),mean(values)))


print(result_distances)

print(result_angles)

from matplotlib import pyplot as plt
plt.imshow(image)
plt.show()
