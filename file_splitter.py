import sys
import os
from PIL import Image
import PIL 
import shutil

def file_split(file, ID):
    names_smallfile = []
    lines_per_file = 100
    smallfile = None
    with open(file) as bigfile:
        i = 1
        for lineno, line in enumerate(bigfile):
            if lineno % lines_per_file == 0:
                if smallfile:
                    smallfile.close()
                small_filename = '{}_{}'.format(ID, i)
                i += 1
                smallfile = open("./input/"+small_filename, "w")
                names_smallfile.append(small_filename)
            smallfile.write(line)
        if smallfile:
            smallfile.close()
    return names_smallfile

def folder_split(folder,ID):
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