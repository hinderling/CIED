from functions import *
from math import sqrt
from skimage.feature import blob_log
from skimage.color import rgb2gray
import matplotlib.pyplot as plt
import sys

allpost, allpre,basenames = load("DATA")

for name, image in enumerate(allpost):

    image_gray = rgb2gray(image)

    #preprocessing: contrast stretching
    p2, p98 = np.percentile(image_gray, (2, 98))
    image_gray = exposure.rescale_intensity(image_gray, in_range=(p2, p98))

    mask = binary_filter(image_gray, percentage=0.90, size=10)


    #blob detection
    blobs_log = blob_log(image_gray, min_sigma = 15, max_sigma=20, num_sigma=3, threshold=.12)

    # comp approximated radii in the 3rd col
    blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)

    masked_blobs = []
    for blob in blobs_log:
        y, x, r = blob
        if mask[int(y)][int(x)]:
            masked_blobs.append(blob)
    blobs_log = masked_blobs


    while len(blobs_log) > 12:
        distances = np.zeros((len(blobs_log), 2))
        for i, blob in enumerate(blobs_log):
            distances[i][0] = int(i)
            y1,x1,r = blob
            for n in range (i,len(blobs_log)):
                y2,x2, r = blobs_log[n]
                # draw.line((x1, y1, x2, y2), fill=128)
                dist = distance((x1,y1),(x2,y2))

                distances[i][1] += dist
                distances[n][1] += dist
        distances = distances[distances[:, 1].argsort()][:len(distances)]
        last = int(distances[len(distances)-1][0])
        blobs_log = np.delete(blobs_log,last, axis=0)


    angles_vec = angles(blobs_log)

    start = int(angles_vec[0][0])

    fig, ax = plt.subplots(1, 1, figsize=(9, 3), sharex=True, sharey=True)
    blobs = blobs_log
    title = 'Laplacian of Gaussian'
    ax.set_title(title)
    ax.imshow(image_gray)
    for i, blob in enumerate(blobs_log):
        y, x, r = blob
        if i == start:
            c = plt.Circle((x, y), r, color='green', linewidth=2, fill=False)
        else:
            c = plt.Circle((x, y), r, color='red', linewidth=2, fill=False)
        ax.add_patch(c)

    plt.show()
