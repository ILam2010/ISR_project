import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np


def main():

    print("Loading feature matrix...")

    # Load dataset
    df = pd.read_csv("staticFeatureMatrix.csv")

    print("Rows:", len(df))

    # ----------------------------
    # SPLIT FEATURES / LABEL
    # ----------------------------
    X = df.iloc[:, 1:5].values   # BM25, TFIDF, LAPLACE, JM
    y = df.iloc[:, 5].values     # Label

    # IMPORTANT: keep doc IDs for TREC output
    qid_doc = df.iloc[:, 0].values   # QID-DocID column

    # ----------------------------
    # TRAIN / TEST SPLIT
    # ----------------------------
    X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
        X, y, qid_doc,
        test_size=0.3,
        random_state=42
    )

    # ----------------------------
    # MODEL
    # ----------------------------
    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    # ----------------------------
    # WRITE TREC OUTPUT
    # ----------------------------
    with open("trainingperformance.txt", "w") as f:
        for i in range(len(predictions)):

            qid_doc_split = id_test[i].split("-")

            if len(qid_doc_split) != 2:
                continue

            qid = qid_doc_split[0]
            docid = qid_doc_split[1]

            rank = i + 1
            score = predictions[i]

            # TREC format:
            f.write(f"{qid} Q0 {docid} {rank} {score} Exp\n")

    print("Output saved to: trainingperformance.txt")
    print("Training complete.")


if __name__ == "__main__":
    main()
