from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans

# ---------------- DATA ----------------
DOC_TEXT = []
DOC_IDS = []

K = 25       
TOPICS = 30  


# ---------------- LOAD CRANFIELD ----------------
def load_docs(path):
    global DOC_TEXT, DOC_IDS

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()

    docs = data.split(".I ")[1:]

    for doc in docs:
        lines = doc.split("\n")

        doc_id = lines[0].strip()
        text_parts = []
        capture = False

        for line in lines:
            line = line.strip()

            if line.startswith(".W"):
                capture = True
                continue

            if line.startswith(".I") or line.startswith(".T") or line.startswith(".A") or line.startswith(".B"):
                continue

            if capture and line:
                text_parts.append(line)

        text = " ".join(text_parts).strip()

        if len(text) > 5:
            DOC_IDS.append(doc_id)
            DOC_TEXT.append(text)


# ---------------- LDA ----------------
def run_lda(X):
    lda = LatentDirichletAllocation(
        n_components=TOPICS,
        max_iter=10,
        learning_method="online",
        random_state=42
    )
    return lda.fit_transform(X)


# ---------------- KMEANS ----------------
def run_kmeans(X_topics):
    km = KMeans(n_clusters=K, random_state=42, n_init=10)
    return km.fit_predict(X_topics)


# ---------------- MAIN ----------------
def main():
    load_docs("C:/Users/User/Information-Retrieval/cran.all.1400")

    print("Documents loaded:", len(DOC_TEXT))

    vectorizer = CountVectorizer(
        stop_words="english",
        max_features=8000,
        min_df=2
    )

    X = vectorizer.fit_transform(DOC_TEXT)

    # LDA
    X_topics = run_lda(X)

    # KMeans
    labels = run_kmeans(X_topics)

    # cluster grouping
    clusters = {}

    for i, label in enumerate(labels):
        clusters.setdefault(label, []).append(DOC_IDS[i])

    # print results
    for c in clusters:
        print(f"\nCluster {c}: {len(clusters[c])} docs")


if __name__ == "__main__":
    main()
