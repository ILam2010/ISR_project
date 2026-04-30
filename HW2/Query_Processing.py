import re
import string
import dill
import time
from collections import defaultdict

# =========================
# LOAD FILES
# =========================

def load(file):
    with open(file, "rb") as f:
        return dill.load(f)


print("Loading index files...")

inverted_index = load("inverted_index.p")
termMap = load("termMap.p")
docMap = load("docMap.p")

# stopwords
with open(r"C:\Users\User\Information-Retrieval\HW2\stoplist.txt", "r", encoding="utf-8") as f:
    stopwords = set([line.strip().lower() for line in f])

reverse_docMap = {v: k for k, v in docMap.items()}

print("Files loaded successfully!")


# =========================
# TOKENIZER
# =========================

def queryProcessor(query):
    query = query.lower()
    query = query.translate(str.maketrans('', '', string.punctuation))
    tokens = query.split()
    return [w for w in tokens if w not in stopwords]


# =========================
# BUILD TERM VECTOR FOR QUERY
# =========================

def build_query_vector(query_tokens):

    termVector = {}

    for token in query_tokens:

        if token not in termMap:
            continue

        term_id = termMap[token]

        if term_id not in inverted_index:
            continue

        postings = inverted_index[term_id]["postings"]

        termVector[token] = {}

        for p in postings:
            doc_id = p["doc_id"]
            tf = p["tf"]
            positions = p["positions"]

            termVector[token][doc_id] = (tf, positions)

    return termVector


# =========================
# SIMPLE VSM (baseline)
# =========================

def vsm(termVector):

    scores = defaultdict(int)

    for term in termVector:
        for doc in termVector[term]:
            tf, _ = termVector[term][doc]
            scores[doc] += tf

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# =========================
# QUERY SEARCH ENGINE
# =========================

def search(query):

    tokens = queryProcessor(query)

    termVector = build_query_vector(tokens)

    results = vsm(termVector)

    return results


# =========================
# MAIN
# =========================

start_time = time.time()

with open("cran.qry", "r", encoding="utf-8", errors="ignore") as f:
    queries = f.readlines()

qNo = 1

for q in queries:

    q = q.strip()

    # skip Cranfield headers
    if not q or q.startswith("."):
        continue

    results = search(q)

    print(f"\nQuery {qNo}: {q}")
    print("Top results:")

    for doc_id, score in results[:5]:
        doc_name = reverse_docMap.get(doc_id, str(doc_id))
        print(f"  {doc_name} -> {score}")

    qNo += 1


# =========================
# TIME
# =========================

temp = time.time() - start_time
print("\nExecution time:", round(temp, 2), "seconds")
