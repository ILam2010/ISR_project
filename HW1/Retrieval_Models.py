from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import math
from operator import itemgetter
from collections import defaultdict
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# CONNECT
# =========================
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "1pmpURwe_KTV*f0UZdXR"),
    verify_certs=False
)

INDEX = "cranfield"

# =========================
# LOAD GLOBAL STATS
# =========================

def compute_stats():
    total_len = 0
    vocab = set()
    D = 0

    for hit in es.search(index="cranfield", query={"match_all": {}}, size=10000)["hits"]["hits"]:
        source = hit["_source"]

        text = source["body_text"]
        doc_len = source["doc_len"]

        total_len += doc_len
        vocab.update(text.split())
        D += 1

    avgDocLen = total_len / D
    V = len(vocab)

    return D, avgDocLen, V




D, avgDocLen, V = compute_stats()

print("Documents:", D)
print("Avg Doc Length:", avgDocLen)
print("Vocabulary Size:", V)

# =========================
# QUERY PROCESSOR
# =========================
def queryNums():
    queries = []
    query = ""

    with open(r"C:\Users\User\Information-Retrieval\cran.qry", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith(".I"):
                if query:
                    queries.append(query)
                    query = ""
            elif line.startswith(".W"):
                continue
            else:
                query += " " + line

        if query:
            queries.append(query)

    return queries


# =========================
# GET DOCS FOR TERM
# =========================
def getDocs(term):
    s = Search().using(es).index(INDEX).query("match", body_text=term)
    return [hit.meta.id for hit in s.scan()]


# =========================
# TERM VECTOR BUILDER
# =========================
def build_term_vector(query):
    termVector = defaultdict(lambda: defaultdict(lambda: [0, 0]))

    terms = query.lower().split()

    for term in terms:
        docs = getDocs(term)

        for docid in docs:
            res = es.termvectors(
                index=INDEX,
                id=docid,
                fields=["body_text"],
                term_statistics=False
            )

            try:
                tf = res["term_vectors"]["body_text"]["terms"][term]["term_freq"]
            except:
                tf = 0

            doc_len = es.get(index=INDEX, id=docid)["_source"]["doc_len"]

            termVector[docid][term] = [tf, doc_len]

    return termVector


# =========================
# OKAPI TF
# =========================
def okapi_tf(termVector, qNo):
    scores = []

    for docid in termVector:
        score = 0

        for term in termVector[docid]:
            tf, docLen = termVector[docid][term]

            score += tf / (tf + 0.5 + 1.5 * (docLen / avgDocLen))

        scores.append((docid, score))

    scores.sort(key=itemgetter(1), reverse=True)

    return scores[:100]


# =========================
# TF-IDF
# =========================
def tfidf(termVector, docFreq, qNo):
    df = dict(docFreq)
    scores = []

    for docid in termVector:
        score = 0

        for term in termVector[docid]:
            tf, docLen = termVector[docid][term]
            df_t = df.get(term, 1)

            tf_norm = tf / (tf + 0.5 + 1.5 * (docLen / avgDocLen))
            idf = math.log10(D / df_t)

            score += tf_norm * idf

        scores.append((docid, score))

    scores.sort(key=itemgetter(1), reverse=True)

    return scores[:100]


# =========================
# BM25
# =========================
def bm25(termVector, docFreq):
    k1, k2, b = 1.2, 1.2, 0.75
    df = dict(docFreq)
    scores = []

    for docid in termVector:
        score = 0

        for term in termVector[docid]:
            tf, docLen = termVector[docid][term]
            df_t = df.get(term, 1)

            idf = math.log((D + 0.5) / (df_t + 0.5))

            part1 = (tf * (k1 + 1)) / (tf + k1 * ((1 - b) + b * (docLen / avgDocLen)))
            part2 = (tf * (k2 + 1)) / (tf + k2)

            score += idf * part1 * part2

        scores.append((docid, score))

    scores.sort(key=itemgetter(1), reverse=True)

    return scores[:100]

def save_results(filename, qNo, results):
    with open(filename, "w") as f:

        for rank, (docid, score) in enumerate(results[:100], 1):
            f.write(f"{qNo} Q0 {docid} {rank} {float(score)} Exp\n")



# =========================
# MAIN LOOP
# =========================
queries = queryNums()
for qNo, query in enumerate(queries, 1):

    termVector = build_term_vector(query)

    okapi_results = okapi_tf(termVector, qNo)
    tfidf_results = tfidf(termVector, [], qNo)
    bm25_results = bm25(termVector, [])

    save_results("OKAPI_results.txt", qNo, okapi_results)
    save_results("TFIDF_results.txt", qNo, tfidf_results)
    save_results("BM25_results.txt", qNo, bm25_results)

    print(f"Query {qNo} done")

