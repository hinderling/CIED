from functions import *
from PIL import Image
allpost, allpre = open("DATA")





for i,img in enumerate(allpost):
    img = preprocess(img)

    img = binary_filter(img, percentage=0.95)

    img = Image.fromarray(img)
    img.save(f'unet/{i}.png')