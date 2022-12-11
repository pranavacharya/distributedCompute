from collections import defaultdict

def aggregator(dictonaries):
    mega_dictionary = defaultdict(lambda: 0)  
    for dicto in dictonaries:
        for key, val in dicto.items():
            mega_dictionary[key] += val
    return mega_dictionary


print(aggregator([{'a': 1, 'b': 2}, {'a': 1, 'b': 2}, {'a': 1, 'b': 2}]))