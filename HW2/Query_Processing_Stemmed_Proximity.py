import dill
import re
from collections import defaultdict

# ----------------------------
# Tokenizer
# ----------------------------
TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*")

def tokenize(text):
    return TOKEN_PATTERN.findall(text.lower())


# ----------------------------
# Load data
# ----------------------------
print("Loading index files...")

term_map = dill.load(open("termMap.p", "rb"))
doc_map = dill.load(open("docMap.p", "rb"))
inverted_index = dill.load(open("inverted_index.p", "rb"))

print("Files loaded successfully!")


# 🔥 FIX: create reverse map (IMPORTANT)
reverse_doc_map = {v: k for k, v in doc_map.items()}


# ----------------------------
# Query processor (TF-based ranking)
# ----------------------------
def process_query(query):

    tokens = tokenize(query)
    scores = defaultdict(int)

    for token in tokens:

        if token not in term_map:
            continue

        term_id = term_map[token]

        if term_id not in inverted_index:
            continue

        postings = inverted_index[term_id]["postings"]

        for p in postings:
            doc_id = p["doc_id"]
            tf = p["tf"]

            scores[doc_id] += tf   # TF scoring

    ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return ranked_docs


# ----------------------------
# Read cran.qry
# ----------------------------
query_file = "cran.qry"

print("\nProcessing queries...\n")

with open(query_file, "r", encoding="utf-8", errors="ignore") as f:
    queries = f.readlines()

query_id = 1

for q in queries:

    q = q.strip()

    # skip Cranfield headers like .I, .W
    if not q or q.startswith("."):
        continue

    print(f"Query {query_id}: {q}")

    results = process_query(q)

    print("Top results:")

    for doc_id, score in results[:5]:

        doc_name = reverse_doc_map.get(doc_id, str(doc_id))
        print(f"  {doc_name} -> score {score}")

    print("-" * 50)
    query_id += 1
