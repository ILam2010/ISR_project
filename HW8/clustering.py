from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
import numpy as np
import os

DOC_TEXT = []
DOC_IDS = []

K = 25
TOPICS = 50


# ---------------- LOAD ----------------
def load_docs(path="C:/Users/User/Information-Retrieval/cran.all.1400"):
    global DOC_TEXT, DOC_IDS

    DOC_TEXT = []
    DOC_IDS = []

    with open(path, encoding="utf-8", errors="ignore") as f:
        data = f.read()

    # Cranfield format parsing (safe fallback)
    docs = data.split(".I ")

    for doc in docs[1:]:
        parts = doc.split(".W")
        docno = parts[0].strip().split()[0]
        text = parts[1] if len(parts) > 1 else ""

        DOC_IDS.append(docno)
        DOC_TEXT.append(text.strip())


# ---------------- LDA ----------------
def run_lda(X):
    lda = LatentDirichletAllocation(
        n_components=TOPICS,
        max_iter=10,
        learning_method="online",
        random_state=42
    )
    return lda.fit_transform(X)


# ---------------- MAIN ----------------
def main():
    load_docs()

    vectorizer = CountVectorizer(stop_words="english", max_features=8000)
    X = vectorizer.fit_transform(DOC_TEXT)

    X_topics = run_lda(X)

    km = KMeans(n_clusters=K, random_state=42, n_init=10)
    labels = km.fit_predict(X_topics)

    clusters = {}

    for i, label in enumerate(labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(DOC_IDS[i])

    # create output folder
    os.makedirs("output", exist_ok=True)

    # save results
    with open("output/clusters.txt", "w") as f:
        for c in clusters:
            f.write(f"\nCluster {c}: {len(clusters[c])} docs\n")
            f.write(",".join(clusters[c]) + "\n")

    print("DONE: clustering completed")


if __name__ == "__main__":
    main()
