from sklearn.feature_extraction.text import CountVectorizer

def load_docs():
    docs = []
    with open(r"C:\Users\User\Information-Retrieval\cran.all.1400", encoding="utf-8") as f:
        text = ""
        in_text = False
        for line in f:
            if line.startswith(".W"):
                in_text = True
                text = ""
            elif line.startswith(".I"):
                if text:
                    docs.append(text)
            elif in_text:
                text += line
        if text:
            docs.append(text)
    return docs


docs = load_docs()

vectorizer = CountVectorizer(stop_words="english")
X = vectorizer.fit_transform(docs)

print("Doc-Term Matrix Shape:", X.shape)
