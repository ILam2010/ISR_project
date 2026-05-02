import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

def main():

    # load dataset
    df = pd.read_csv("feature_matrix.csv")

    print("Columns:", df.columns)

    # -------------------------
    # FEATURES + LABEL
    # -------------------------
    X = df.drop(columns=["DocID", "Label"])
    y = df["Label"]

    # encode labels (VERY IMPORTANT)
    le = LabelEncoder()
    y = le.fit_transform(y)

    # split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # model
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # prediction
    preds = model.predict(X_test)

    # accuracy
    print("Accuracy:", accuracy_score(y_test, preds) * 100)

main()
