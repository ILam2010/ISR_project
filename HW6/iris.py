import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, chi2

# Load dataset
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
names = ['sepal-length', 'sepal-width', 'petal-length', 'petal-width', 'class']

dataset = pd.read_csv(url, names=names)

# Split features and labels
array = dataset.values
X = array[:, 0:4].astype(float)   
y = array[:, 4]

# Feature selection (SelectKBest with Chi-Square)
X_new = SelectKBest(score_func=chi2, k=2).fit_transform(X, y)

print("Selected Features (top 2):")
print(X_new)
