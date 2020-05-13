from functions import *
allpost, allpre = open("DATA")





for img in (allpost):

    # img = allpost[2]
    #
    img = preprocess(img)

    # showhist(img)

    img = binary_filter(img)

    show(img)