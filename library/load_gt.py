from functions import *

allpost, basenames = load("DATA")



for image, name in zip(allpost,basenames):
    # load ground truth
    ground_truth = gt(name)

    # plot coordinates
    print(name)
    for electrode in ground_truth:
        print(electrode)
    print()
    print("test")