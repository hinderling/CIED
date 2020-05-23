from functions import *

allpost, allpre, basenames = load("DATA")


for image, name in zip(allpost,basenames):
    # load ground truth
    ground_truth = gt(name)

    # plot coordinates
    plot_coordinates(image,ground_truth,f'Ground Truth {name}')