import dill
from collections import defaultdict

# ----------------------------
# Load token stream
# ----------------------------

def load_tokens(path):
    with open(path, "rb") as f:
        return dill.load(f)


# ----------------------------
# Build inverted index
# ----------------------------
def build_index(token_stream):

    index = defaultdict(lambda: defaultdict(list))
    tf = defaultdict(lambda: defaultdict(int))
    df = defaultdict(set)
    ttf = defaultdict(int)

    for term_id, doc_id, pos in token_stream:

        index[term_id][doc_id].append(pos)
        tf[term_id][doc_id] += 1
        df[term_id].add(doc_id)
        ttf[term_id] += 1

    return index, tf, df, ttf

# ----------------------------
# Write inverted index (BINARY FIX)
# ----------------------------
def save_inverted_index(index, tf, df, ttf, path):

    data = {}

    for term_id in index:

        postings = []

        sorted_docs = sorted(index[term_id], key=lambda d: -tf[term_id][d])

        for doc_id in sorted_docs:
            postings.append({
                "doc_id": doc_id,
                "tf": tf[term_id][doc_id],
                "positions": index[term_id][doc_id]
            })

        data[term_id] = {
            "df": len(df[term_id]),
            "ttf": ttf[term_id],
            "postings": postings
        }

    # SAVE AS PROPER PICKLE (IMPORTANT FIX)
    with open(path, "wb") as f:
        dill.dump(data, f)

    return data
def write_index(index, tf, df, ttf, output_file):

    catalog = {}
    offset = 0

    with open(output_file, "w", encoding="utf-8") as f:

        for term_id in sorted(index.keys()):

            postings = []

            # sort docs by TF descending
            docs = sorted(index[term_id], key=lambda d: -tf[term_id][d])

            for doc_id in docs:
                positions = index[term_id][doc_id]

                postings.append(
                    f"{doc_id},{tf[term_id][doc_id]},{','.join(map(str, positions))}"
                )

            line = f"{term_id}:{len(df[term_id])},{ttf[term_id]}|" + ";".join(postings) + "\n"

            length = len(line)

            f.write(line)

            catalog[term_id] = (offset, length)
            offset += length

    return catalog


# ----------------------------
# Save catalog
# ----------------------------
def save_catalog(catalog, path):
    with open(path, "wb") as f:
        dill.dump(catalog, f)


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":

    tokens = load_tokens("token_stream.p")

    print("Building index...")
    index, tf, df, ttf = build_index(tokens)

    print("Writing index...")
    catalog = write_index(index, tf, df, ttf, "invertedFile.txt")

    print("Saving catalog...")
    save_catalog(catalog, "catalog.p")

 
    
    with open("totalTF.p", "wb") as f:
        dill.dump(ttf, f)

    print("DONE ")

