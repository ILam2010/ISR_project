from stemming.porter2 import stem
import time
from bs4 import BeautifulSoup
import os
import re
import regex
from collections import defaultdict, OrderedDict
import dill

# =========================
# DATA STRUCTURES
# =========================

class TermVector:
    def __init__(self, tf, pos):
        self.tf = tf
        self.pos = pos

class Catalog:
    def __init__(self):
        self.terms = {}
        self.termMap = {}

    def addTerm(self, term, offset, length, fileName, termid):
        if term not in self.terms:
            self.terms[term] = {}
            self.termMap[term] = termid
        self.terms[term][fileName] = (offset, length)

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

def stemTxt(text):
    return " ".join(stem(w) for w in text.split())

def getDocLen(text):
    return len(text.split())

# =========================
# INDEX BUILDER
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

def calcTTF(termDict, term):
    return sum(termDict[term][doc][0] for doc in termDict[term])

def calcDF(termDict, term):
    return len(termDict[term])

def loadCatalog(termDict, invFileNo):
    filename = f"Files/Stemmed/invertedFile{invFileNo}.txt"

    with open(filename, "a") as invFile:
        for term in termDict:
            postings = termDict[term]

            offset = invFile.tell()
            df = calcDF(termDict, term)
            ttf = calcTTF(termDict, term)

            termid = catalog.termMap.get(term, len(catalog.termMap) + 1)
            catalog.termMap[term] = termid

            line = f"{termid},{df},{ttf}:"

            for docid in postings:
                tf, pos = postings[docid]
                pos_str = ",".join(map(str, pos))
                line += f"{docid},{tf},{pos_str};"

            line = line.rstrip(";") + "\n"

            invFile.write(line)
            catalog.addTerm(term, offset, len(line), filename, termid)

    return invFileNo + 1

# =========================
# MAIN INDEXING PIPELINE
# =========================

def getTokens():
    path = "AP_DATA/docs/"   # 🔥 FIXED PATH (make sure folder exists)
    tokens = []
    docInfo = {}
    invFile = 0
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

                text = stemTxt(text)
                token_list = tokenizer(text)

                termDict = constructDict(token_list, docID)

                tokens.append(termDict)
                count += 1

                if count == 1000:
                    invFile = loadCatalog(mergeDicts(tokens), invFile)
                    tokens = []
                    count = 0

    if tokens:
        invFile = loadCatalog(mergeDicts(tokens), invFile)

    # save metadata
    pickler('Files/Stemmed/Pickles/docInfo.p', docInfo)
    pickler('Files/Stemmed/Pickles/termMap.p', catalog.termMap)

# =========================
# MERGE PARTIAL INDEXES
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

catalog = Catalog()

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
