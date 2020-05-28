########################################################################################################################
# run.py
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
# IMPORTS
from functions import *
from graph import *
import csv

########################################################################################################################
# PARAMETERS

# path to input folder containing cases in the following structure
# FOLDER
#   - {CASE_1}
#       - {CASE_1}post.png
#   - {CASE_2}
#       - {CASE_2}post.png

FOLDER = "DATA"

########################################################################################################################
# LOAD DATA
all_post, base_names = load(FOLDER)

# STORING DATA TO EXPORT TO CSV
angles_all = []
center_all = []
names_all = []
coordinates_all = []

differences = []

#find in what range distance and angles can be
dist_CI, dict, min_angle,max_angle = CI_gt_distances_angles(image_names_gt())

for image, name in zip(all_post, base_names):

    
    # FIND Electrodes and store them in a matrix of this format:
    #
    # coordinates =
    # [[1     x1     y1]
    # [2     x2     y2]
    # [      ...      ]
    # [12    x12   y12]]
    # First row corresponds to the number of the electrode starting in the center
    coordinates = find_electrodes(image, dist_CI, dict)
    print('coords',coordinates)
    print(name)
    truth=gt(str(name))
    truth.sort()
    print('difference',np.subtract(truth, coordinates))
    # Calculate the cochlea center and angular depth from electrode positions
    center, angles=all_angles(coordinates)



    # STORING DATA TO EXPORT TO CSV
    coordinates_all.append(coordinates)
    angles_all.append(angles)
    center_all.append(center)
    names_all.append(name)

save_csv(angles_all, center_all, names_all, coordinates_all)

#produce some plots for the report
plots=False
if plots==True:
    gt_distances, gt_angle1, gt_angle11=gt_distances_angles1_and11(image_names_gt())
    find_confidence(gt_distances, 'distances')
    find_confidence(gt_angle1, 'angles 1')
    find_confidence(gt_angle11,'angles_11')
    plot_gt_distances_angles(image_names_gt())
