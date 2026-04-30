from collections import defaultdict
import math

# -----------------------------
# 1. Load Cranfield documents (NON-XML)
# -----------------------------
def load_docs(path):
    docs = {}
    current_doc = None
    text_lines = []
    in_text = False

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if line.startswith(".I"):   # ✅ FIXED HERE
                if current_doc is not None:
                    docs[current_doc] = " ".join(text_lines)

                current_doc = line.split()[1]
                text_lines = []
                in_text = False

            elif line.startswith(".W"):
                in_text = True

            elif line.startswith("."):
                in_text = False

            elif in_text:
                text_lines.append(line)

        # save last document
        if current_doc is not None:
            docs[current_doc] = " ".join(text_lines)

    print(f"DEBUG: Loaded {len(docs)} documents")

    return docs



# -----------------------------
# 2. Build TF-IDF vectors
# -----------------------------
def build_tfidf(docs):
    tf = {}
    df = defaultdict(int)

    # Term Frequency
    for doc_id, text in docs.items():
        words = text.lower().split()
        tf[doc_id] = defaultdict(int)

        for w in words:
            tf[doc_id][w] += 1

        for w in set(words):
            df[w] += 1

    N = len(docs)

    # TF-IDF
    tfidf = {}
    for doc_id in docs:
        tfidf[doc_id] = {}

        for w in tf[doc_id]:
            idf = math.log(N / (1 + df[w]))
            tfidf[doc_id][w] = tf[doc_id][w] * idf

    return tfidf


# -----------------------------
# 3. Cosine similarity
# -----------------------------
def cosine(v1, v2):
    common = set(v1) & set(v2)
    dot = sum(v1[t] * v2[t] for t in common)

    n1 = math.sqrt(sum(x * x for x in v1.values()))
    n2 = math.sqrt(sum(x * x for x in v2.values()))

    if n1 == 0 or n2 == 0:
        return 0

    return dot / (n1 * n2)


# -----------------------------
# 4. Build graph (Top-K links)
# -----------------------------
def build_graph(vectors, K=5):
    graph = defaultdict(list)

    for d1 in vectors:
        sims = []

        for d2 in vectors:
            if d1 == d2:
                continue

            s = cosine(vectors[d1], vectors[d2])
            sims.append((d2, s))

        sims.sort(key=lambda x: x[1], reverse=True)

        graph[d1] = [doc for doc, _ in sims[:K]]

    return graph


# -----------------------------
# 5. Save linkgraph.txt
# -----------------------------
def save_graph(graph, filename="linkgraph.txt"):
    with open(filename, "w") as f:
        for doc, links in graph.items():
            line = doc + " " + " ".join(links)
            f.write(line + "\n")


# -----------------------------
# 6. Main
# -----------------------------
if __name__ == "__main__":
    print("Loading documents...")
    docs = load_docs("cran.all.1400") 
    
    print("Sample doc:", list(docs.items())[:1])


    # 🔥 START SMALL FIRST (then remove this line later)
    docs = dict(list(docs.items())[:100])

    print(f"Loaded {len(docs)} documents")

    print("Building TF-IDF...")
    vectors = build_tfidf(docs)

    print("Building graph...")
    graph = build_graph(vectors, K=5)

    print("Saving linkgraph.txt...")
    save_graph(graph)

    print(" Done! linkgraph.txt created.")
