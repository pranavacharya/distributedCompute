from collections import defaultdict
import json

def aggregator(id, file_list):
    dictonaries = []
    for file in file_list:
        with open("./server_op/" + str(id) + "-" + file) as f:
            data = f.read()
            js = json.loads(data)
            dictonaries.append(js)
    mega_dictionary = defaultdict(lambda: 0)  
    for dicto in dictonaries:
        for key, val in dicto.items():
            mega_dictionary[key] += val
    return mega_dictionary