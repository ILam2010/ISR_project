import re
import os
import dill

# ----------------------------
# Regex tokenizer rule
# ----------------------------
TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*")

# ----------------------------
# Load stopwords (optional)
# ----------------------------
def load_stopwords(path):
    stopwords = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                stopwords.add(line.strip().lower())
    except FileNotFoundError:
        print(f"Warning: Stopword file not found at {path}. Continuing without stopwords.")
    return stopwords


# ----------------------------
# Tokenizer function
# ----------------------------
def tokenize(text):
    text = text.lower()
    return TOKEN_PATTERN.findall(text)


# ----------------------------
# Main tokenizer
# ----------------------------
def process_collection(doc_folder, stopword_file=None):

    stopwords = load_stopwords(stopword_file) if stopword_file else set()

    term_map = {}
    doc_map = {}
    term_id_counter = 0
    doc_id_counter = 0

    output = []

    # 🔴 FIX: check if folder exists before listing
    if not os.path.exists(doc_folder):
        raise FileNotFoundError(f"Document folder not found: {doc_folder}")

    for filename in sorted(os.listdir(doc_folder)):

        doc_path = os.path.join(doc_folder, filename)

        # skip non-files (important if any hidden files exist)
        if not os.path.isfile(doc_path):
            continue

        with open(doc_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        doc_id = doc_id_counter
        doc_map[filename] = doc_id
        doc_id_counter += 1

        tokens = tokenize(text)
        position = 1

        for token in tokens:

            if token in stopwords:
                continue

            if token not in term_map:
                term_map[token] = term_id_counter
                term_id_counter += 1

            term_id = term_map[token]

            output.append((term_id, doc_id, position))
            position += 1

    # Save outputs
    with open("termMap.p", "wb") as f:
        dill.dump(term_map, f)

    with open("docMap.p", "wb") as f:
        dill.dump(doc_map, f)

    with open("token_stream.p", "wb") as f:
        dill.dump(output, f)

    print("Tokenization complete!")
    print("Total tokens:", len(output))
    print("Vocabulary size:", len(term_map))


# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    
    doc_folder = r"C:\Users\User\Information-Retrieval\collection"
    stopword_file = r"C:\Users\User\Information-Retrieval\HW2\stoplist.txt"

    process_collection(
        doc_folder=doc_folder,
        stopword_file=stopword_file
    )
