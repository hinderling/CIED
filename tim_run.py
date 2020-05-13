from functions import *
allpost, allpre = open("DATA")





for img in (allpost):

    #
    img = preprocess(img)


    img = binary_filter(img, percentage=0.95)

    show(img)