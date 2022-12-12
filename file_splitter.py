import sys
import os
from PIL import Image
import PIL 
import shutil

def file_split(folder,ID):
    names_smallfile = []
    smallfile = None
    file_list=os.listdir("./input/"+folder)
    i = 1
    for f in file_list:
        small_filename = '{}_{}'.format(ID, i)
        i += 1
        shutil.copy2("./input/"+folder+"/"+f , "./input/"+small_filename)
        names_smallfile.append(small_filename)
    return names_smallfile