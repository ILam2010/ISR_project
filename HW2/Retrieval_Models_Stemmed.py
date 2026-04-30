from __future__ import division
import math
from operator import itemgetter
from collections import defaultdict
import string
import dill

# =========================
# UTIL FUNCTIONS
# =========================

def unpickler(file):
    with open(file, 'rb') as f:
        return dill.load(f)

def parseCatalog(file):
    catalog = {}
    with open(file, 'r') as catalogFile:
        for line in catalogFile:
            content = line.strip().split(',')
            catalog[content[0]] = content[1:]
    return catalog

# =========================
# RESTRUCTURE TERM VECTOR
# =========================

def restructureTV(termVector):
    dictDocID = defaultdict(lambda: defaultdict(list))

    for term in termVector:
        for docid in termVector[term]:
            tf = termVector[term][docid][0]
            pos = termVector[term][docid][1]
            dictDocID[docid][term] = [tf, pos]

    return dictDocID

# =========================
# OKAPI TF
# =========================

def Total_okapiTF(qNo, termVector, termStats, docInfo):
    docScore = []
    dictDocID = restructureTV(termVector)

    for docid in dictDocID:
        score = 0
        for term in dictDocID[docid]:
            tfwd = dictDocID[docid][term][0]
            docLen = int(docInfo.get(docid, 1))

            score += tfwd / (tfwd + 0.5 + (1.5 * (docLen / avgDocLen)))

        docScore.append((docid, score))

    docScore.sort(key=itemgetter(1), reverse=True)

    with open('Files/Stemmed/OkapiTF_Results_File.txt', 'a') as f:
        for rank, (docid, score) in enumerate(docScore[:1000], 1):
            f.write(f"{qNo} Q0 {docid} {rank} {score} Exp\n")

# =========================
# BM25 (FIXED)
# =========================

def Okapi_BM25(qNo, termVector, termStats, docInfo):
    k1 = 1.2
    k2 = 100
    b = 0.75

    docScore = []
    dictDocID = restructureTV(termVector)

    for docid in dictDocID:
        score = 0

        for term in dictDocID[docid]:
            tfwd = dictDocID[docid][term][0]
            docLen = int(docInfo.get(docid, 1))

            df = int(termStats.get(term, [1])[0])

            # FIXED IDF
            idf = math.log((D - df + 0.5) / (df + 0.5) + 1)

            tf_component = ((k1 + 1) * tfwd) / (
                tfwd + k1 * (1 - b + b * (docLen / avgDocLen))
            )

            query_tf = 1
            query_component = ((k2 + 1) * query_tf) / (k2 + query_tf)

            score += idf * tf_component * query_component

        docScore.append((docid, score))

    docScore.sort(key=itemgetter(1), reverse=True)

    with open('Files/Stemmed/OkapiBM25_Results_File.txt', 'a') as f:
        for rank, (docid, score) in enumerate(docScore[:1000], 1):
            f.write(f"{qNo} Q0 {docid} {rank} {score} Exp\n")

    return docScore

# =========================
# LAPLACE SMOOTHING
# =========================

def UnigramLM_Laplace(qNo, termVector, termStats, docInfo):
    dictDocID = restructureTV(termVector)

    vocab = set(termVector.keys())

    docScore = {}

    for docid in dictDocID:
        score = 0
        docLen = int(docInfo.get(docid, 1))

        for term in vocab:
            tfwd = dictDocID[docid].get(term, [0])[0]
            prob = (tfwd + 1) / (docLen + V)
            score += math.log(prob)

        docScore[docid] = score

    ranked = sorted(docScore.items(), key=itemgetter(1), reverse=True)

    with open('Files/Stemmed/UnigramLMLaplace_Results_File.txt', 'a') as f:
        for rank, (docid, score) in enumerate(ranked[:1000], 1):
            f.write(f"{qNo} Q0 {docid} {rank} {score} Exp\n")

# =========================
# PROXIMITY
# =========================

def rangeOfWindow(pos):
    minROW = float("inf")
    keyPos = {k: pos[k][0] for k in pos}

    while len(keyPos) == len(pos):
        row = max(keyPos.values()) - min(keyPos.values())
        minKey = min(keyPos, key=keyPos.get)

        idx = pos[minKey].index(keyPos[minKey])

        if idx < len(pos[minKey]) - 1:
            keyPos[minKey] = pos[minKey][idx + 1]
        else:
            del keyPos[minKey]

        minROW = min(minROW, row)

    return minROW


def proximity(qNo, termVector, termStats, docInfo):
    dictDocID = restructureTV(termVector)
    docScore = []

    c = 1500

    for docid in dictDocID:
        pos = {}
        docLen = int(docInfo.get(docid, 1))

        for term in dictDocID[docid]:
            pos[term] = dictDocID[docid][term][1]

        if len(pos) < 2:
            continue

        row = rangeOfWindow(pos)

        score = (c - row) * len(pos) / (docLen + V)

        docScore.append((docid, score))

    docScore.sort(key=itemgetter(1), reverse=True)

    with open('Files/Stemmed/Results/Proximity_Results_File.txt', 'a') as f:
        for rank, (docid, score) in enumerate(docScore[:1000], 1):
            f.write(f"{qNo} Q0 {docid} {rank} {score} Exp\n")

# =========================
# QUERY NUMBERS
# =========================

def queryNums():
    queries = []
    with open('QueryUpdated.txt', 'r') as f:
        for line in f:
            qid = re.sub(r'[^\w\s]', '', line.split()[0])
            queries.append(qid)
    return queries

# =========================
# MAIN
# =========================

import re

termMap = unpickler('Files/Stemmed/Pickles/termMap.p')
catalog = parseCatalog('Files/Stemmed/catalogFile.txt')
docInfo = unpickler('Files/Stemmed/Pickles/docInfo.p')

avgDocLen = sum(docInfo.values()) / len(docInfo)
V = len(catalog)
D = len(docInfo)

qNums = queryNums()

for i, qNo in enumerate(qNums, 1):
    termStats = unpickler(f'Files/Stemmed/Pickles/termStats_Proximity{i}.p')
    termVector = unpickler(f'Files/Stemmed/Pickles/termVector_Proximity{i}.p')

    print(f"Running Query {i}")

    # Choose ONE or more:
    # Total_okapiTF(qNo, termVector, termStats, docInfo)
    Okapi_BM25(qNo, termVector, termStats, docInfo)
    # UnigramLM_Laplace(qNo, termVector, termStats, docInfo)
    proximity(qNo, termVector, termStats, docInfo)

print("Done!")
