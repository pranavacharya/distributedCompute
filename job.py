import sys
input = sys.argv[1]

def word_count(str):
    counts = dict()
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts

with open(input, 'r') as f:
    txt = f.read()
    word = word_count(txt)
    print(word)
