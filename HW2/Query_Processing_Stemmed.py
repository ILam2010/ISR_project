from __future__ import division
import string
import re
import time
from nltk.stem import PorterStemmer
from collections import OrderedDict
import dill

stemmer = PorterStemmer()

# =========================
# UNPICKLER
# =========================
def unpickler(file):
    with open(file, 'rb') as f:
        return dill.load(f)

# =========================
# READ QUERIES
# =========================
def queryMaker():
    with open('QueryUpdated.txt', 'r', encoding='utf-8') as f:
        queries = []
        for line in f:
            line = re.sub(r'[\-\.\"\s]+', ' ', line)
            line = re.sub(r'\d+', '', line)
            queries.append(line.strip())
    return queries

# =========================
# STOPWORD REMOVAL
# =========================
def queryProcessor(query):
    with open("Files/Stemmed/stoplist.txt", "r", encoding='utf-8') as f:
        stopWords = set([line.strip() for line in f])

    keywords = []

    for word in query.lower().split():
        if word not in stopWords and word not in string.punctuation:
            keywords.append(word)

    return " ".join(keywords)

# =========================
# GET DOC INFO
# =========================
def getInfo(key, catalog, termMap, docMap):
    keyInfo = OrderedDict()
    invList = OrderedDict()
    docDict = OrderedDict()

    indexFile = open("Files/Stemmed/invertedFile0.txt", 'r', encoding='utf-8')

    offset = catalog.get(key, [None])[0]
    if offset is None:
        return {}, {}

    indexFile.seek(int(offset))
    line = indexFile.readline()

    parts = line.split(':')

    df = parts[0].split(',')[1]
    ttf = parts[0].split(',')[2]

    keyInfo[key] = [df, ttf]

    remStr = parts[1].split(';')

    for item in remStr:
        if item.strip() == "":
            continue

        values = item.split(',')

        docno = values[0]
        docID = docMap.get(int(docno))
        tf = int(values[1])
        pos = list(map(int, values[2:]))

        docDict[docID] = (tf, pos)

    invList[key] = docDict

    indexFile.close()
    return invList, keyInfo

# =========================
# BUILD TERM VECTOR
# =========================
def getParameters(query, qNo):
    keywords = queryProcessor(query)

    termVector = OrderedDict()
    termStats = OrderedDict()

    for key in keywords.split():

        # ✔ FIXED STEMMING
        key = stemmer.stem(key.lower())

        invList, keyInfo = getInfo(key, catalog, termMap, docMap)

        termVector.update(invList)
        termStats.update(keyInfo)

    # save pickles
    with open(f'Files/Stemmed/Pickles/termStats{qNo}.p', 'wb') as f:
        dill.dump(termStats, f)

    with open(f'Files/Stemmed/Pickles/termVector{qNo}.p', 'wb') as f:
        dill.dump(termVector, f)

# =========================
# MAIN
# =========================
start_time = time.time()

docInfo = unpickler('Files/Stemmed/Pickles/docInfo.p')
catalog = unpickler('Files/Stemmed/Pickles/catalog.p')
termMap = unpickler('Files/Stemmed/Pickles/termMap.p')
docMap = unpickler('Files/Stemmed/Pickles/docMap.p')

queries = queryMaker()

for qNo, query in enumerate(queries, 1):
    getParameters(query, qNo)
    print(f"Created {qNo} termVector")

# =========================
# TIME OUTPUT
# =========================
temp = time.time() - start_time

hours = temp // 3600
temp = temp - 3600 * hours
minutes = temp // 60
seconds = temp - 60 * minutes

print('%d:%d:%d' % (hours, minutes, seconds))
