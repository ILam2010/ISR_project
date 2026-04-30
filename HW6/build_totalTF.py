import dill
import re
from collections import defaultdict

# LOAD REAL CRANFIELD DOCS
def load_docs(path):
    docs = {}
    doc_id = None
    text = []

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if line.startswith(".I"):
                if doc_id is not None:
                    docs[doc_id] = " ".join(text)
                doc_id = line.split()[1]
                text = []

            elif line.startswith(".W"):
                continue
            else:
                text.append(line)

        if doc_id:
            docs[doc_id] = " ".join(text)

    return docs


docs = load_docs("cran.all.1400")

totalTF = defaultdict(lambda: defaultdict(int))

for docID, text in docs.items():
    tokens = re.findall(r'\w+', text.lower())

    for t in tokens:
        totalTF[docID][t] += 1

with open("totalTF.p", "wb") as f:
    dill.dump(dict(totalTF), f)

print("OK: totalTF created with", len(totalTF), "docs")
