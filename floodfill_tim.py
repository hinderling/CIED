from functions import *
from skimage.morphology import flood
from matplotlib import pyplot as plt
from scipy import ndimage
allpost, allpre, basenames = load("DATA")


for image, name in zip(allpre,basenames):
    # load ground truth
    ground_truth = gt(name)



    x,y = ground_truth[0][1:3]
    mask = flood(image, (y,x),connectivity=5, tolerance=5)
    for n,x,y in ground_truth[1:]:
        mask_temp = flood(image, (y, x),connectivity=5, tolerance=5)
        mask = np.logical_or (mask_temp,mask)


    fig, ax = plt.subplots(1, 1, figsize=(9, 3), sharex=True, sharey=True)
    title = 'Laplacian of Gaussian'
    ax.set_title(title)
    ax.imshow(mask)
    for n,x,y in ground_truth:
        c = plt.Circle((x, y), 20, color='red', linewidth=2, fill=False)
        ax.add_patch(c)

    plt.show()