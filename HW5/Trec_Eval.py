from collections import OrderedDict
import math

relevanceJudgements = {}

# =========================
# READ RUN FILE
# =========================
def retrieveQueryResults(rankList):
    queryResults = OrderedDict()

    with open(rankList, 'r') as f:
        for line in f:
            items = line.strip().split()

            queryID = items[0]
            documentID = items[2]

            if queryID in queryResults:
                queryResults[queryID].append(documentID)
            else:
                queryResults[queryID] = [documentID]

    return queryResults


# =========================
# READ QRELS (FIXED)
# =========================
def getRevelanceJudgements(qrel):
    with open(qrel, 'r') as f:
        for line in f:
            cols = line.strip().split()

            queryID = cols[0]
            documentID = cols[1]
            relevance = int(cols[2])   # ✔ FIXED

            # convert Cleverdon scale → binary relevance
            if relevance > 0:
                if queryID in relevanceJudgements:
                    relevanceJudgements[queryID].append(documentID)
                else:
                    relevanceJudgements[queryID] = [documentID]


# =========================
# GET RELEVANCE SCORE
# =========================
def getScoreForID(queryID, documents):
    relevantDocuments = relevanceJudgements.get(queryID, [])
    return [1 if doc in relevantDocuments else 0 for doc in documents]


# =========================
# SAFE DESIGNATE FUNCTION
# =========================
def designateVals(lst, val, rank):
    if rank in lst:
        lst[rank].append(val)
    else:
        lst[rank] = [val]
    return lst


# =========================
# PRINT MEANS
# =========================
def printMeanVals(lst, desc, kVals=[], qid=''):
    if not kVals:
        if len(lst) == 0:
            print(desc + ': 0.0000')
        else:
            print(desc + ': ' + str("{:.4f}".format(math.fsum(lst) / len(lst))))
    else:
        for k in kVals:
            if k in lst and len(lst[k]) > 0:
                val = math.fsum(lst[k]) / len(lst[k])
            else:
                val = 0.0

            if qid != '':
                print(desc + str(k) + ' for ' + qid + ': ' + str("{:.4f}".format(val)))
            else:
                print(desc + str(k) + ': ' + str("{:.4f}".format(val)))


# =========================
# MAIN METRICS
# =========================
def calculateMetrics(queryResults, option):
    kVals = [5, 10, 20, 50, 100]

    AP, RP, NDCG = [], [], []
    P, R, F1 = {}, {}, {}

    for queryID in queryResults:

        relevanceScore = []
        PTemp, RTemp, F1Temp = {}, {}, {}

        psum, rank, relevantNumber, rp = 0, 0, 0, 0

        results = queryResults[queryID]

        relevantDocuments = relevanceJudgements.get(queryID, [])

        if len(relevantDocuments) == 0:
            continue

        for document in results:
            rank += 1
            isRelevant = 1 if document in relevantDocuments else 0

            if isRelevant:
                relevantNumber += 1

            if rank <= len(relevantDocuments):
                rp = relevantNumber

            precision = relevantNumber / rank
            recall = relevantNumber / len(relevantDocuments)

            if isRelevant:
                psum += precision

            if rank in kVals:
                P = designateVals(P, precision, rank)
                R = designateVals(R, recall, rank)

                f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                F1 = designateVals(F1, f1, rank)

            relevanceScore.append(isRelevant)

        # =========================
        # NDCG
        # =========================
        dc_value = 0.0
        for i, score in enumerate(relevanceScore):
            dc_value += score / math.log2(i + 2)

        idc_value = 0.0
        for i, score in enumerate(sorted(relevanceScore, reverse=True)):
            idc_value += score / math.log2(i + 2)

        ndcg = dc_value / idc_value if idc_value != 0 else 0

        # =========================
        # MAP + RP
        # =========================
        avgPrecision = psum / len(relevantDocuments)
        rPrecision = relevantNumber / len(relevantDocuments)

        AP.append(avgPrecision)
        RP.append(rPrecision)
        NDCG.append(ndcg)

    # =========================
    # FINAL OUTPUT
    # =========================
    printMeanVals(AP, 'Average Precision')
    printMeanVals(RP, 'R-precision')
    printMeanVals(NDCG, 'nDCG')


# =========================
# MAIN
# =========================
def main():
    cmd = input('Enter command: ')
    cmd_params = cmd.split()

    if len(cmd_params) == 3:
        qrels = cmd_params[1]
        runfile = cmd_params[2]

        queryResults = retrieveQueryResults(runfile)
        getRevelanceJudgements(qrels)

        calculateMetrics(queryResults, 1)
    else:
        print("Usage: eval qrels.txt run.txt")


main()
