import time
import string
import os
import dill
import urllib3

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
from collections import defaultdict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =========================
# ELASTICSEARCH (OPTIONAL STORAGE)
# =========================
from elasticsearch import Elasticsearch

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "1pmpURwe_KTV*f0UZdXR"),
    verify_certs=False
)

# =========================
# START TIMER
# =========================
start_time = time.time()

# =========================
# STOPWORDS
# =========================
stopWords = set(stopwords.words('english'))

# =========================
# PATH SETUP
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICKLE_DIR = os.path.join(BASE_DIR, "Pickles")
os.makedirs(PICKLE_DIR, exist_ok=True)

# =========================
# PREPROCESS FUNCTION
# =========================
def preprocess(text):
    text = text.translate(str.maketrans('', '', string.punctuation))

    tokens = []
    for word in text.split():
        word = word.lower()
        if word not in stopWords:
            tokens.append(word)

    return tokens

# =========================
# PARSE CRANFIELD DOCUMENTS
# =========================
def parse_documents(file_path):
    docs = {}
    current_id = None
    current_text = []
    in_text = False

    with open(file_path, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith(".I"):
                if current_id is not None:
                    docs[current_id] = " ".join(current_text)

                current_id = int(line.split()[1])
                current_text = []
                in_text = False

            elif line.startswith(".W"):
                in_text = True

            elif line.startswith(".T") or line.startswith(".A") or line.startswith(".B"):
                in_text = False

            elif in_text:
                current_text.append(line)

        if current_id is not None:
            docs[current_id] = " ".join(current_text)

    return docs

# =========================
# LOAD DATA
# =========================
path = "cran.all.1400"
docs = parse_documents(path)

print("Total Documents:", len(docs))

# =========================
# INDEX STRUCTURES
# =========================
inverted_index = defaultdict(lambda: defaultdict(list))
doc_lengths = {}

# =========================
# INDEXING LOOP
# =========================
i = 0

for doc_id, text in docs.items():

    tokens = preprocess(text)
    doc_lengths[doc_id] = len(tokens)

    # DEBUG (optional)
    # print(doc_id, tokens[:5])

    # BUILD INVERTED INDEX
    for pos, term in enumerate(tokens):
        inverted_index[term][doc_id].append(pos)

    # STORE IN ELASTICSEARCH (optional but useful)
    es.index(
        index="cranfield",
        id=doc_id,
        document={
            "body_text": " ".join(tokens),
            "doc_len": len(tokens)
        }
    )

    i += 1
    if i % 50 == 0:
        print(f"Indexed {i} documents")

# =========================
# SAVE PICKLE FILES
# =========================
with open(os.path.join(PICKLE_DIR, "inverted_index.p"), "wb") as f:
    dill.dump(dict(inverted_index), f)

with open(os.path.join(PICKLE_DIR, "doc_lengths.p"), "wb") as f:
    dill.dump(doc_lengths, f)

# =========================
# DONE
# =========================
elapsed = time.time() - start_time
print(f"\nDone indexing in {elapsed:.2f} seconds")
