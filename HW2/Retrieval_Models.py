import math
from collections import defaultdict
from operator import itemgetter

# =========================
# UTIL
# =========================

def restructureTV(termVector):
    dictDocID = defaultdict(dict)

    for term in termVector:
        for docid in termVector[term]:
            tf, pos = termVector[term][docid]
            dictDocID[docid][term] = (tf, pos)

    return dictDocID


# =========================
# BM25
# =========================

def bm25(termVector, termStats, docInfo, avgDocLen, V, D):

    k1 = 1.2
    k2 = 100
    b = 0.75

    dictDocID = restructureTV(termVector)
    scores = defaultdict(float)

    for docid in dictDocID:

        docLen = int(docInfo.get(docid, 1))

        for term in dictDocID[docid]:

            tf = dictDocID[docid][term][0]
            df = int(termStats.get(term, [1])[0])

            idf = math.log((D - df + 0.5) / (df + 0.5) + 1)

            tf_component = ((k1 + 1) * tf) / (
                tf + k1 * (1 - b + b * (docLen / avgDocLen))
            )

            scores[docid] += idf * tf_component

    return sorted(scores.items(), key=itemgetter(1), reverse=True)


# =========================
# VSM (TF-based)
# =========================

def vsm(termVector):

    dictDocID = restructureTV(termVector)
    scores = defaultdict(float)

    for docid in dictDocID:
        for term in dictDocID[docid]:
            tf = dictDocID[docid][term][0]
            scores[docid] += tf

    return sorted(scores.items(), key=itemgetter(1), reverse=True)


# =========================
# LM (Laplace)
# =========================

def lm_laplace(termVector, termStats, docInfo, V):

    dictDocID = restructureTV(termVector)
    scores = defaultdict(float)

    vocab = set()

    for t in termVector:
        vocab.add(t)

    for docid in dictDocID:

        docLen = int(docInfo.get(docid, 1))

        score = 0

        for term in vocab:
            tf = dictDocID[docid].get(term, (0, []))[0]
            prob = (tf + 1) / (docLen + V)
            score += math.log(prob)

        scores[docid] = score

    return sorted(scores.items(), key=itemgetter(1), reverse=True)


# =========================
# PROXIMITY
# =========================

def proximity(termVector, docInfo, V):

    dictDocID = restructureTV(termVector)
    scores = defaultdict(float)

    for docid in dictDocID:

        if len(dictDocID[docid]) < 2:
            continue

        positions = {t: dictDocID[docid][t][1] for t in dictDocID[docid]}

        all_pos = [p for plist in positions.values() for p in plist]
        if not all_pos:
            continue

        row = max(all_pos) - min(all_pos)

        docLen = int(docInfo.get(docid, 1))

        scores[docid] = (V - row) / docLen

    return sorted(scores.items(), key=itemgetter(1), reverse=True)
