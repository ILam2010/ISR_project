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
    queries = []
    with open('QueryUpdated.txt', 'r', encoding='utf-8') as f:
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
        stopWords = set(line.strip() for line in f)

    keywords = []

    for word in query.lower().split():
        if word not in stopWords:
            keywords.append(word)

    # remove punctuation AFTER joining
    cleaned = " ".join(keywords)
    cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))

    return cleaned.strip()

# =========================
# GET DOC INFO
# =========================
def getInfo(key, catalog, termMap, docMap):
    keyInfo = OrderedDict()
    invList = OrderedDict()
    docDict = OrderedDict()

    # 🔴 IMPORTANT: use termMap → catalog expects TERM ID, not term string
    if key not in termMap:
        return {}, {}

    keyId = str(termMap[key])

    if keyId not in catalog:
        return {}, {}

    with open("Files/Stemmed/invertedFile0.txt", 'r', encoding='utf-8') as indexFile:
        offset = catalog[keyId][0]
        indexFile.seek(int(offset))
        line = indexFile.readline()

    parts = line.split(':')

    df = parts[0].split(',')[1]
    ttf = parts[0].split(',')[2]

    keyInfo[key] = [df, ttf]

    remStr = parts[1].split(';')

    for item in remStr:
        if not item.strip():
            continue

        values = item.split(',')

        docno = values[0]
        docID = docMap.get(int(docno), docno)

        tf = int(values[1])
        pos = [int(p) for p in values[2:] if p]

        docDict[docID] = (tf, pos)

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

# 🔴 FIX: catalog should NOT be unpickled (it's a text file in most setups)
catalog = {}
with open('Files/Stemmed/catalogFile.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(',')
        catalog[parts[0]] = parts[1:]

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

hours = int(temp // 3600)
temp %= 3600
minutes = int(temp // 60)
seconds = int(temp % 60)

print(f"{hours}:{minutes}:{seconds}")
