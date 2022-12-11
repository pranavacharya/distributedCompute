import sys
# big_file = sys.argv[1]

def file_split(file):
    names_smallfile = []
    lines_per_file = 100
    smallfile = None
    with open(file) as bigfile:
        for lineno, line in enumerate(bigfile):
            if lineno % lines_per_file == 0:
                if smallfile:
                    smallfile.close()
                small_filename = 'small_file_{}.txt'.format(lineno + lines_per_file)
                smallfile = open("./input/"+small_filename, "w")
                names_smallfile.append(small_filename)
            smallfile.write(line)
        if smallfile:
            smallfile.close()
    return names_smallfile

# print(file_split(big_file))