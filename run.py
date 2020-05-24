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

# path to input folder containing cases in the folowing structure
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
for image, name in zip(all_post, base_names):
    
    # FIND Electrodes and store them in a matrix of this format:
    #
    # coordinates =
    # [[1     x1     y1]
    # [2     x2     y2]
    # [      ...      ]
    # [12    x12   y12]]
    # First row corresponds to the number of the electrode starting in the center
    
    coordinates = find_electrodes(image)


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

