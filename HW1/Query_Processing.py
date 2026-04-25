from __future__ import division
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from collections import defaultdict
import os
import string
import dill
import urllib3
from nltk.corpus import stopwords

# ----------------------------
# SETUP PATHS
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICKLES_DIR = os.path.join(BASE_DIR, "Pickles")
os.makedirs(PICKLES_DIR, exist_ok=True)

# ----------------------------
# SSL WARNING DISABLE (safe for assignment)
# ----------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------
# CONNECT TO ELASTICSEARCH
# ----------------------------
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "1pmpURwe_KTV*f0UZdXR"),
    verify_certs=False
)

index = "cranfield"

# ----------------------------
# STOPWORDS (NLTK - consistent IR practice)
# ----------------------------
stopWords = set(stopwords.words('english'))

# ----------------------------
# QUERY PROCESSOR (CLEANING)
# ----------------------------
def queryProcessor(query):
    query = query.translate(str.maketrans('', '', string.punctuation))

    tokens = []
    for word in query.split():
        word = word.lower()
        if word not in stopWords:
            tokens.append(word)

    return " ".join(tokens)

# ----------------------------
# GET DOCUMENT IDS FOR A TERM
# ----------------------------
def getDocInfo(term):
    s = Search(using=es, index=index).query("match", body_text=term)
    return [hit.meta.id for hit in s.scan()]

# ----------------------------
# MAIN PROCESSING FUNCTION
# ----------------------------
def getParameters(query, qNo):
    docFreq = []
    termVector = defaultdict(lambda: defaultdict(list))

    keywords = queryProcessor(query)

    for term in keywords.split():

        docInfo = getDocInfo(term)
        docFreq.append([term, len(docInfo)])

        for docid in docInfo:
            try:
                tv = es.termvectors(
                    index=index,
                    id=docid,
                    fields=["body_text"],
                    term_statistics=True
                )

                terms = tv["term_vectors"]["body_text"]["terms"]

                tf = terms[term]["term_freq"] if term in terms else 0

                termVector[docid][term].append(tf)

            except Exception:
                continue

    # save intermediate files
    with open(os.path.join(PICKLES_DIR, f'docFreq{qNo}.p'), 'wb') as f:
        dill.dump(docFreq, f)

    with open(os.path.join(PICKLES_DIR, f'termvector{qNo}.p'), 'wb') as f:
        dill.dump(termVector, f)

    return termVector

# ----------------------------
# READ QUERIES
# ----------------------------
def queryMaker():
    QUERY_PATH = r"C:\Users\User\Information-Retrieval\cran.qry"
    queries = []

    with open(QUERY_PATH, "r", encoding="utf-8") as f:
        query = ""

        for line in f:
            line = line.strip()

            if line.startswith(".I"):
                if query:
                    queries.append(query)
                    query = ""
            elif not line.startswith(".W"):
                query += " " + line

        if query:
            queries.append(query)

    return queries

# ----------------------------
# MAIN EXECUTION
# ----------------------------
queries = queryMaker()

for qNo, query in enumerate(queries, start=1):
    getParameters(query, qNo)
    print(f"Created termVector for Query {qNo}")

print("DONE")
