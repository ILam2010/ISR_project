from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")


# =========================
# ELASTICSEARCH CONNECTION
# =========================
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "1pmpURwe_KTV*f0UZdXR"),
    verify_certs=False
)

INDEX = "cranfield"

# =========================
# LOAD QRELS (GROUND TRUTH)
# =========================
def load_qrels(path):
    qrels = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()

            qid = parts[0]
            docid = parts[1]
            rel = int(parts[2])

            if qid not in qrels:
                qrels[qid] = {}

            # binary relevance
            qrels[qid][docid] = 1 if rel > 0 else 0

    return qrels


# =========================
# SIMPLE FEATURE EXTRACTION
# =========================
def get_features(doc_id, query):
    try:
        res = es.get(index=INDEX, id=doc_id)
        text = res["_source"]["body_text"]

        doc_len = len(text.split())
        score = len(set(query.split()) & set(text.split()))

        return doc_len, score

    except Exception:
        return 0, 0


# =========================
# BUILD FEATURE MATRIX
# =========================
def build_feature_matrix(qrels, queries):
    rows = []

    for qid, query in queries.items():

        if qid not in qrels:
            continue

        for docid in qrels[qid]:

            length, score = get_features(docid, query)

            rows.append([
                docid,
                length,
                score,
                qrels[qid][docid]
            ])

    df = pd.DataFrame(rows, columns=["DocID", "Length", "Score", "Label"])
    df.to_csv("feature_matrix.csv", index=False)

    print("Feature matrix created:", df.shape)


# =========================
# LOAD QUERIES
# =========================
def load_queries(path):
    queries = {}
    current_id = None
    current_text = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith(".I"):
                if current_id is not None:
                    queries[str(current_id)] = " ".join(current_text)

                current_id = line.split()[1]
                current_text = []

            elif not line.startswith(".W"):
                current_text.append(line)

        if current_id is not None:
            queries[str(current_id)] = " ".join(current_text)

    return queries


# =========================
# MAIN
# =========================
def main():
    qrels_path = r"C:\Users\User\Information-Retrieval\cranqrel"
   
    query_path = r"C:\Users\User\Information-Retrieval\cran.qry"

    qrels = load_qrels(qrels_path)
    queries = load_queries(query_path)

    build_feature_matrix(qrels, queries)


main()
