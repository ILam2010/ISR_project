import time
from bs4 import BeautifulSoup
import os
import re
import regex
from collections import defaultdict
import dill

# =========================
# DATA STRUCTURES
# =========================

class TermVector:
    def __init__(self, tf, pos):
        self.tf = tf
        self.pos = pos

# =========================
# TOKENIZER
# =========================

def tokenizer(text):
    tokens = []
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    for i, word in enumerate(words, 1):
        tokens.append((word, i))

    return tokens

# =========================
# CLEAN DOCUMENTS
# =========================

def cleanUpDocs(file):
    page = file.read()
    soup = BeautifulSoup(f"<root>{page}</root>", 'xml')
    return soup.find_all('DOC')

def getText(doc):
    text = " ".join(t.get_text() for t in doc.find_all('TEXT'))
    return cleanText(text)

def cleanText(text):
    text = regex.sub(r"[^\P{P}\-.,%]+", "", text)
    text = text.replace("-", " ")
    text = re.sub(r'\.\.+', ' ', text)
    return text

def getDocLen(text):
    return len(text.split())

# =========================
# BUILD TERM DICTIONARY
# =========================

def constructDict(tokens, docID):
    termDict = defaultdict(dict)

    for word, pos in tokens:
        if word in stopWords:
            continue

        if docID not in termDict[word]:
            termDict[word][docID] = [1, [pos]]
        else:
            termDict[word][docID][0] += 1
            termDict[word][docID][1].append(pos)

    return termDict

# =========================
# STATISTICS
# =========================

def calcTTF(termDict, term):
    return sum(termDict[term][doc][0] for doc in termDict[term])

def calcDF(termDict, term):
    return len(termDict[term])

# =========================
# WRITE INVERTED FILE
# =========================

def writeIndex(termDict, fileNo):
    filename = f"Files/Unstemmed/invertedFile{fileNo}.txt"

    with open(filename, "a") as f:
        for term in termDict:
            df = calcDF(termDict, term)
            ttf = calcTTF(termDict, term)

            line = f"{term},{df},{ttf}:"

            for docid in termDict[term]:
                tf, pos = termDict[term][docid]
                pos_str = ",".join(map(str, pos))
                line += f"{docid},{tf},{pos_str};"

            line = line.rstrip(";") + "\n"
            f.write(line)

    return fileNo + 1

# =========================
# MERGE DICTIONARIES
# =========================

def mergeDicts(dictList):
    merged = defaultdict(dict)

    for d in dictList:
        for term in d:
            for docid in d[term]:
                if docid not in merged[term]:
                    merged[term][docid] = d[term][docid]
                else:
                    merged[term][docid][0] += d[term][docid][0]
                    merged[term][docid][1].extend(d[term][docid][1])

    return merged

# =========================
# MAIN INDEXING
# =========================

def getTokens():
    path = "AP_DATA/docs/"   # ✔ FIX THIS PATH if needed
    tokens = []
    docInfo = {}
    fileNo = 0
    count = 0

    for filename in os.listdir(path):
        if filename == "readme":
            continue

        print(f"Processing {filename}")

        with open(os.path.join(path, filename), 'r', encoding='utf-8', errors='ignore') as file:
            docs = cleanUpDocs(file)

            for doc in docs:
                docID = doc.find('DOCNO').get_text().strip()

                text = getText(doc)
                docInfo[docID] = getDocLen(text)

                token_list = tokenizer(text)
                termDict = constructDict(token_list, docID)

                tokens.append(termDict)
                count += 1

                if count == 1000:
                    merged = mergeDicts(tokens)
                    fileNo = writeIndex(merged, fileNo)
                    tokens = []
                    count = 0

    if tokens:
        merged = mergeDicts(tokens)
        writeIndex(merged, fileNo)

    pickler('Files/Unstemmed/Pickles/docInfo.p', docInfo)

# =========================
# PICKLER
# =========================

def pickler(path, obj):
    with open(path, 'wb') as f:
        dill.dump(obj, f)

# =========================
# STOPWORDS
# =========================

with open("stoplist.txt", "r") as f:
    stopWords = set(w.strip() for w in f)

# =========================
# MAIN
# =========================

def main():
    start = time.time()

    getTokens()

    elapsed = time.time() - start

    h = int(elapsed // 3600)
    m = int((elapsed % 3600) // 60)
    s = int(elapsed % 60)

    print(f"{h}:{m}:{s}")

if __name__ == "__main__":
    main()
