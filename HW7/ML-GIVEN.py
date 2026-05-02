from sklearn.dummy import DummyClassifier
import pandas as pd

def main():
    df = pd.read_csv("feature_matrix.csv")

    X = df[["Length", "Score"]]
    y = [1] * len(df)

    model = DummyClassifier(strategy="most_frequent")
    model.fit(X, y)

    print("Baseline model trained")


if __name__ == "__main__":
    main()
