from collections import defaultdict

# =========================
# LOAD QREL FILE (FIXED)
# =========================
def load_qrels(file_path):
    qrels = defaultdict(dict)
    rel_count = defaultdict(int)

    with open(file_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 3:
                continue

            qid = parts[0]
            docid = parts[1]
            rel = int(parts[2])

            # 🔥 FIX: treat graded relevance properly
            qrels[qid][docid] = rel

            if rel > 0:
                rel_count[qid] += 1

    return qrels, rel_count


# =========================
# LOAD RUN FILE
# =========================
def load_run(file_path):
    run = defaultdict(list)

    with open(file_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 6:
                continue

            qid = parts[0]
            docid = parts[2]
            score = float(parts[4])

            run[qid].append((docid, score))

    for qid in run:
        run[qid].sort(key=lambda x: x[1], reverse=True)

    return run


# =========================
# AVERAGE PRECISION (FIXED LOGIC)
# =========================
def average_precision(ranked_list, qrels, qid):
    num_rel = 0
    score = 0.0

    for i, (docid, _) in enumerate(ranked_list, start=1):

        # 🔥 FIX: any rel >= 1 is relevant
        if qrels[qid].get(docid, 0) > 0:
            num_rel += 1
            score += num_rel / i

    if num_rel == 0:
        return 0.0

    return score / num_rel


# =========================
# PRECISION @ K
# =========================
def precision_at_k(ranked_list, qrels, qid, k):
    rel = 0

    for i, (docid, _) in enumerate(ranked_list[:k]):
        if qrels[qid].get(docid, 0) > 0:
            rel += 1

    return rel / k


# =========================
# R-PRECISION
# =========================
def r_precision(ranked_list, qrels, qid, R):
    if R == 0:
        return 0.0

    rel = 0
    for i, (docid, _) in enumerate(ranked_list[:R]):
        if qrels[qid].get(docid, 0) > 0:
            rel += 1

    return rel / R


# =========================
# MAIN
# =========================
def main():

    qrels, rel_count = load_qrels("cranqrel")
    run = load_run("trainingperformance.txt")

    MAP = 0
    P10 = 0
    RPREC = 0

    num_queries = len(run)

    for qid in run:
        ranked_list = run[qid]

        MAP += average_precision(ranked_list, qrels, qid)
        P10 += precision_at_k(ranked_list, qrels, qid, 10)
        RPREC += r_precision(ranked_list, qrels, qid, rel_count[qid])

    if num_queries == 0:
        print("No queries found")
        return

    print("\n===== RESULTS =====")
    print("MAP:", MAP / num_queries)
    print("P@10:", P10 / num_queries)
    print("R-Precision:", RPREC / num_queries)


if __name__ == "__main__":
    main()
