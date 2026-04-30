from __future__ import division
import string
import re
import time
from Stemmed_Stopwords_Removed_Index import TermVector
from collections import OrderedDict
import dill

# =========================
# UNPICKLER
# =========================
def unpickler(file):
    with open(file, 'rb') as f:
        return dill.load(f)

# =========================
# PARSE CATALOG
# =========================
def parseCatalog(file):
    catalog = {}
    with open(file, 'r') as catalogFile:
        for line in catalogFile:
            content = line.strip().split(',')
            catalog[content[0]] = content[1:]
    return catalog

# =========================
# READ QUERIES
# =========================
def queryMaker():
    queries = []
    with open('ProximityQueryModel.txt', 'r') as f:
        for line in f:
            line = re.sub(r'[\-\.\"\s]+', ' ', line)
            line = re.sub(r'\d+', '', line)  # Python 3 fix
            queries.append(line.strip())
    return queries

# =========================
# STOPWORD REMOVAL
# =========================
def queryProcessor(query):
    # ⚠️ FIXED PATH (must be local)
    with open("stoplist.txt", 'r') as sfile:
        stopWords = set(w.strip() for w in sfile if w.strip())

    keywords = []

    for word in query.split():
        if word not in stopWords:
            keywords.append(word)

    cleaned = " ".join(keywords)

    # remove punctuation (Python 3 fix)
    cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))

    return cleaned.strip()

# =========================
# GET DOC INFO
# =========================
def getInfo(key, catalog, termMap, docMap):
    keyInfo = OrderedDict()
    invList = OrderedDict()
    docDict = OrderedDict()

    # ⚠️ CHECK term exists
    if key not in termMap:
        return {}, {}

    keyId = str(termMap[key])

    if keyId not in catalog:
        return {}, {}

    with open("Files/Unstemmed/invertedFile0.txt", 'r') as indexFile:
        offset = catalog[keyId][0]
        indexFile.seek(int(offset))
        line = indexFile.readline()

    df = line.split(':')[0].split(',')[1]
    ttf = line.split(':')[0].split(',')[2]

    keyInfo[key] = [df, ttf]

    remStr = line.split(':')[1].split(';')

    for item in remStr:
        if not item.strip():
            continue

        parts = item.split(',')

        docno = parts[0]
        docID = docMap.get(int(docno), docno)

        tf = int(parts[1])
        pos = [int(e) for e in parts[2:] if e]

        docDict[docID] = TermVector(tf, pos)

    invList[key] = docDict

    return invList, keyInfo

# =========================
# BUILD TERM VECTOR
# =========================
def getParameters(query, qNo):
    keywords = queryProcessor(query)

    termVector = OrderedDict()
    termStats = OrderedDict()

    for key in keywords.split():
        key = key.lower()

        invList, keyInfo = getInfo(key, catalog, termMap, docMap)

        termVector.update(invList)
        termStats.update(keyInfo)

    # save pickles
    with open(f'Files/Unstemmed/Pickles/termStats_Proximity{qNo}.p', 'wb') as f:
        dill.dump(termStats, f)

    with open(f'Files/Unstemmed/Pickles/termVector_Proximity{qNo}.p', 'wb') as f:
        dill.dump(termVector, f)

# =========================
# MAIN
# =========================
start_time = time.time()

docInfo = unpickler('Files/Unstemmed/Pickles/docInfo.p')
catalog = parseCatalog('Files/Unstemmed/catalogFile.txt')
termMap = unpickler('Files/Unstemmed/Pickles/termMap.p')
docMap = unpickler('Files/Unstemmed/Pickles/docMap.p')

queries = queryMaker()

qNo = 0
for query in queries:
    qNo += 1
    getParameters(query, qNo)
    print(f"Created {qNo} termVector")

# =========================
# TIME OUTPUT
# =========================
temp = time.time() - start_time

hours = int(temp // 3600)
temp %= 3600
minutes = int(temp // 60)
seconds = int(temp % 60)

print(f"{hours}:{minutes}:{seconds}")
