from stemming.porter2 import stem
from bs4 import BeautifulSoup
import dill


# ----------------------------
# Unpickler
# ----------------------------
def unpickler(file):
    with open(file, 'rb') as f:
        return dill.load(f)


# ----------------------------
# Parse catalog file
# ----------------------------
def parseCatalog(file):
    catalog = {}
    with open(file, 'r') as catalogFile:
        for line in catalogFile:
            content = line.strip().split(',')
            catalog[content[0]] = content[1:]
    return catalog


# ----------------------------
# Load structures
# ----------------------------
docInfo = unpickler('Files/Stemmed/Pickles/docInfo.p')
catalog = parseCatalog('Files/Stemmed/catalogFile.txt')
termMap = unpickler('Files/Stemmed/Pickles/termMap.p')
docMap = unpickler('Files/Stemmed/Pickles/docMap.p')


# ----------------------------
# Files
# ----------------------------
inFile = open("in.0.50.txt", "r")
indexFile = open("Files/Stemmed/invertedFile0.txt", "r")
outFile = open("Files/out.0.stop.stem.txt", "a+")

# ----------------------------
# Processing
# ----------------------------
for line in inFile:
    key = stem(line.strip())
    keyId = termMap.get(key)

    if keyId is None:
        outFile.write(line)
        continue

    keyId = str(keyId)

    if keyId in catalog:
        offset = int(catalog[keyId][0])
        length = int(catalog[keyId][1])

        indexFile.seek(offset)
        termLine = indexFile.read(length)

        parts = termLine.split(':')[0].split(',')

        df = parts[1]
        ttf = parts[2]

        outFile.write(f"{line.strip()} {df} {ttf}\n")
    else:
        outFile.write(line)


# ----------------------------
# Close files
# ----------------------------
outFile.close()
inFile.close()
indexFile.close()
