from glob import glob
from os.path import basename
from PIL import Image
import numpy as np


def open(path):

    folders = glob(f"{path}/*")

    allpost = []
    allpre = []
    for folder in folders:
        allpost.append(np.asarray(Image.open(f"{folder}/{basename(folder)}post.png")))
        allpre.append(np.asarray(Image.open(f"{folder}/{basename(folder)}post.png")))


    return (allpost, allpre)
