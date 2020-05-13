from functions import *
from math import sqrt
from skimage import data
from skimage.feature import blob_dog, blob_log, blob_doh
from skimage.color import rgb2gray
import cv2 as cv

allpost, allpre = open("DATA")

import matplotlib.pyplot as plt

image = allpost[2] #select an image here

image_gray = rgb2gray(image)

#preprocessing: contrast stretching
p2, p98 = np.percentile(image_gray, (2, 98))
image_gray = exposure.rescale_intensity(image_gray, in_range=(p2, p98))

#blob detection
blobs_log = blob_log(image_gray, min_sigma = 15, max_sigma=20, num_sigma=3, threshold=.12)

# comp approximated radii in the 3rd col
blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)


#Filter the blobs according to some specifications: 
#e.g: remove points lying to close to border
b_size = 50
b = blobs
b = b[b[:,2].argsort()]
borders = np.asarray(b[:,0]<b_size) | np.asarray(b[:,0]>(746-b_size))  | np.asarray(b[:,1]<bsize) | np.asarray(b[:,1] > 1129-(b_size)) #image shape is (746, 1129)
blobs = b[~borders]


#display the blobs
fig, ax = plt.subplots(1, 1, figsize=(9, 3), sharex=True, sharey=True)
blobs = blobs_log
title = 'Laplacian of Gaussian'
ax.set_title(title)
ax.imshow(image_gray)
for blob in blobs:
    y, x, r = blob
    c = plt.Circle((x, y), r, color='red', linewidth=2, fill=False)
    ax.add_patch(c)
#ax.set_axis_off()
plt.show()

