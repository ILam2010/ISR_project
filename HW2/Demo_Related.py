import dill

def unpickler(file):
    with open(file, 'rb') as f:
        return dill.load(f)

docInfo = unpickler('Files/Stemmed/Pickles/docInfo.p')

print(len(docInfo))
