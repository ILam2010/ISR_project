from elasticsearch import Elasticsearch
import os

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "1pmpURwe_KTV*f0UZdXR"),
    verify_certs=False,
    ssl_show_warn=False
)

INDEX = "hw7_index"

def parse_cranfield(path):
    docs = {}
    doc_id = None
    text = []
    in_text = False

    with open(path, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith(".I"):
                if doc_id:
                    docs[doc_id] = " ".join(text)
                doc_id = line.split()[1]
                text = []
                in_text = False

            elif line.startswith(".W"):
                in_text = True

            elif line.startswith(".T") or line.startswith(".A") or line.startswith(".B"):
                in_text = False

            elif in_text:
                text.append(line)

        if doc_id:
            docs[doc_id] = " ".join(text)

    return docs


def index_docs():
    docs = parse_cranfield(r"C:\Users\User\Information-Retrieval\cran.all.1400")


    for doc_id, text in docs.items():
        es.index(
            index=INDEX,
            id=doc_id,
            document={
                "text": text,
                "label": "doc"
            }
        )
        print(f"Indexed {doc_id}")


if __name__ == "__main__":
    index_docs()
