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
import csv

########################################################################################################################
# PARAMETERS

# path to input folder containing cases in the folowing structure
# FOLDER
#   - {CASE_2}
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

for image, name in zip(all_post, base_names):
    # START OF DELETE THIS ####################### START OF DELETE THIS ####################### START OF DELETE THIS ###
    #
    # FIND POINTS
    #
    # coordinates =
    # [[1     x1     y1]
    # [2     x2     y2]
    # [      ...      ]
    # [12    x12   y12]]
    # First row corresponds to the number of the electrode starting in the center
    #
    # preliminary
    coordinates = gt(name)
    #
    # END OF DELETE THIS ######################### END OF DELETE THIS ######################### END OF DELETE THIS #####

    # START OF DELETE THIS ####################### START OF DELETE THIS ####################### START OF DELETE THIS ###
    #
    # CALCULATE RESULTS
    #
    # angles = [t1,t2, ... , tn]
    # same order as in coordinates array
    #
    # center = (x,y)
    #
    # preliminary
    angles = [69] * 12
    center = (420, 69)
    #
    # END OF DELETE THIS ######################### END OF DELETE THIS ######################### END OF DELETE THIS #####

    # STORING DATA TO EXPORT TO CSV
    coordinates_all.append(coordinates)
    angles_all.append(angles)
    center_all.append(center)
    names_all.append(name)

save_csv(angles_all, center_all, names_all, coordinates_all)

