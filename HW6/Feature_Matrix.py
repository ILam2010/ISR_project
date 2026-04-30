import csv
import dill
from collections import defaultdict, OrderedDict

featureMatrix = OrderedDict()
relevance = defaultdict(dict)


# -------------------------
# LOAD RELEVANCE (cranqrel)
# -------------------------
def load_qrel(file):
    with open(file, "r") as f:
        for line in f:
            parts = line.strip().split()

            # must have exactly 3 columns
            if len(parts) != 3:
                continue

            qid = parts[0]
            docid = parts[1]
            rel = int(parts[2])

            relevance[qid][docid] = rel



# -------------------------
# ADD FEATURES
# -------------------------
def add_feature(model_scores, model_name):
    for qid in model_scores:
        for docid, score in model_scores[qid].items():

            label = relevance[qid].get(docid, 0)
            key = f"{qid}-{docid}"

            if key not in featureMatrix:
                featureMatrix[key] = {}

            featureMatrix[key][model_name] = (score, label)


# -------------------------
# WRITE CSV
# -------------------------
def write_csv():
    with open("staticFeatureMatrix.csv", "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(["QID-DocID", "BM25", "TFIDF", "LAPLACE", "JM", "Label"])

        for k, v in featureMatrix.items():

            bm25 = v.get("BM25", (0, 0))[0]
            tfidf = v.get("TFIDF", (0, 0))[0]
            laplace = v.get("LAPLACE", (0, 0))[0]
            jm = v.get("JM", (0, 0))[0]

            label = list(v.values())[0][1]

            writer.writerow([k, bm25, tfidf, laplace, jm, label])


# -------------------------
# MAIN (TEST DATA TEMP ONLY)
# -------------------------
if __name__ == "__main__":

    print("Building feature matrix...")

    load_qrel("cranqrel")

    # 🔥 TEMP: replace later with real ranking outputs
    bm25 = {
        "1": {"184": 1.2, "29": 0.8},
        "2": {"31": 0.5}
    }

    tfidf = bm25
    laplace = bm25
    jm = bm25

    add_feature(bm25, "BM25")
    add_feature(tfidf, "TFIDF")
    add_feature(laplace, "LAPLACE")
    add_feature(jm, "JM")

    write_csv()

    print("CSV created successfully")
