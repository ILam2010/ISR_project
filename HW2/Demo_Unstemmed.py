import dill


# ----------------------------
# Unpickler
# ----------------------------
def unpickler(file):
    with open(file, 'rb') as f:
        return dill.load(f)


# ----------------------------
# Parse catalog
# ----------------------------
def parseCatalog(file):
    catalog = {}
    with open(file, 'r') as catalogFile:
        for line in catalogFile:
            content = line.strip().split(',')
            catalog[content[0]] = content[1:]
    return catalog


# ----------------------------
# Load data
# ----------------------------
docInfo = unpickler('Files/Unstemmed/Pickles/docInfo.p')
catalog = parseCatalog('Files/Unstemmed/catalogFile.txt')
termMap = unpickler('Files/Unstemmed/Pickles/termMap.p')
docMap = unpickler('Files/Unstemmed/Pickles/docMap.p')


# ----------------------------
# Files
# ----------------------------
with open("in.0.50.txt", "r") as inFile, \
     open("Files/Unstemmed/invertedFile0.txt", "r") as indexFile, \
     open("Files/out.0.no.stop.no.stem.txt", "a+") as outFile:

    for line in inFile:

        key = line.strip()
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

            outFile.write(f"{key} {df} {ttf}\n")

        else:
            outFile.write(line)
