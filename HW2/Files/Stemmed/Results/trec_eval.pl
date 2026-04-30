#!/usr/bin/env python3
import sys
from collections import defaultdict

# -----------------------------
# Usage check
# -----------------------------
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print("Usage: trec_eval [-q] <qrel_file> <trec_file>")
    sys.exit(1)

print_all_queries = False

# -----------------------------
# Parse arguments
# -----------------------------
args = sys.argv[1:]

if len(args) == 3:
    args.pop(0)  # remove -q
    print_all_queries = True

qrel_file = args[0]
trec_file = args[1]

# -----------------------------
# Read QREL file
# -----------------------------
qrel = defaultdict(dict)
num_rel = defaultdict(int)

with open(qrel_file, "r") as f:
    data = f.read().split()

# QREL format: topic, dummy, doc_id, rel
for i in range(0, len(data), 4):
    topic = data[i]
    doc_id = data[i + 2]
    rel = float(data[i + 3])

    qrel[topic][doc_id] = rel
    num_rel[topic] += rel

# -----------------------------
# Read TREC file
# -----------------------------
trec = defaultdict(dict)

with open(trec_file, "r") as f:
    data = f.read().split()

# TREC format: topic, dummy, doc_id, dummy, score, dummy
for i in range(0, len(data), 6):
    topic = data[i]
    doc_id = data[i + 2]
    score = float(data[i + 4])

    trec[topic][doc_id] = score

# -----------------------------
# Evaluation settings
# -----------------------------
recalls = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
cutoffs = [5, 10, 15, 20, 30, 100, 200, 500, 1000]

# -----------------------------
# Metrics storage
# -----------------------------
tot_num_ret = 0
tot_num_rel = 0
tot_num_rel_ret = 0

sum_prec_at_cutoffs = [0] * len(cutoffs)
sum_prec_at_recalls = [0] * len(recalls)

sum_avg_prec = 0
sum_r_prec = 0
num_topics = 0


# -----------------------------
# Evaluation function
# -----------------------------
def eval_print(qid, ret, rel, rel_ret,
               prec_recalls, map_score,
               prec_cutoffs, rp):

    print(f"\nQueryid (Num):    {qid}")
    print("Total number of documents over all queries")
    print(f"    Retrieved:    {ret}")
    print(f"    Relevant:     {rel}")
    print(f"    Rel_ret:      {rel_ret}")

    print("Interpolated Recall - Precision Averages:")
    for i, r in enumerate(recalls):
        print(f"    at {r:.2f}       {prec_recalls[i]:.4f}")

    print("Average precision (MAP):")
    print(f"                  {map_score:.4f}")

    print("Precision at cutoffs:")
    for c, val in zip(cutoffs, prec_cutoffs):
        print(f"  At {c:4d} docs:   {val:.4f}")

    print("R-Precision:")
    print(f"    Exact:        {rp:.4f}")


# -----------------------------
# Main loop over topics
# -----------------------------
for topic in sorted(trec.keys()):

    if num_rel[topic] == 0:
        continue

    num_topics += 1

    scores = trec[topic]

    prec_list = [0] * 1001
    rec_list = [0] * 1001

    num_ret = 0
    num_rel_ret = 0
    sum_prec = 0

    # sort docs by score desc, then doc_id asc
    sorted_docs = sorted(scores.items(), key=lambda x: (-x[1], x[0]))

    for doc_id, score in sorted_docs:

        num_ret += 1
        rel = qrel[topic].get(doc_id, 0)

        if rel > 0:
            sum_prec += rel * (1 + num_rel_ret) / num_ret
            num_rel_ret += rel

        prec_list[num_ret] = num_rel_ret / num_ret
        rec_list[num_ret] = num_rel_ret / num_rel[topic]

        if num_ret >= 1000:
            break

    avg_prec = sum_prec / num_rel[topic]

    final_recall = num_rel_ret / num_rel[topic]

    for i in range(num_ret + 1, 1001):
        prec_list[i] = num_rel_ret / i
        rec_list[i] = final_recall

    # -------------------------
    # Precision at cutoffs
    # -------------------------
    prec_at_cutoffs = []
    for c in cutoffs:
        prec_at_cutoffs.append(prec_list[c])

    # -------------------------
    # R-Precision
    # -------------------------
    r = num_rel[topic]
    int_r = int(r)
    frac_r = r - int_r

    if r > num_ret:
        r_prec = num_rel_ret / r
    else:
        if frac_r > 0:
            r_prec = (1 - frac_r) * prec_list[int_r] + frac_r * prec_list[int_r + 1]
        else:
            r_prec = prec_list[int_r]

    # -------------------------
    # Interpolated precision
    # -------------------------
    max_prec = 0
    for i in range(1000, 0, -1):
        if prec_list[i] > max_prec:
            max_prec = prec_list[i]
        else:
            prec_list[i] = max_prec

    # -------------------------
    # Precision at recall levels
    # -------------------------
    prec_at_recalls = []
    i = 1

    for r_level in recalls:
        while i <= 1000 and rec_list[i] < r_level:
            i += 1

        if i <= 1000:
            prec_at_recalls.append(prec_list[i])
        else:
            prec_at_recalls.append(0)

    # -------------------------
    # Print per query
    # -------------------------
    if print_all_queries:
        eval_print(topic, num_ret, num_rel[topic], num_rel_ret,
                   prec_at_recalls, avg_prec,
                   prec_at_cutoffs, r_prec)

    # -------------------------
    # Aggregate
    # -------------------------
    tot_num_ret += num_ret
    tot_num_rel += num_rel[topic]
    tot_num_rel_ret += num_rel_ret

    for i in range(len(cutoffs)):
        sum_prec_at_cutoffs[i] += prec_at_cutoffs[i]

    for i in range(len(recalls)):
        sum_prec_at_recalls[i] += prec_at_recalls[i]

    sum_avg_prec += avg_prec
    sum_r_prec += r_prec


# -----------------------------
# Final averages
# -----------------------------
avg_prec_at_cutoffs = [x / num_topics for x in sum_prec_at_cutoffs]
avg_prec_at_recalls = [x / num_topics for x in sum_prec_at_recalls]

mean_avg_prec = sum_avg_prec / num_topics
avg_r_prec = sum_r_prec / num_topics

eval_print(num_topics, tot_num_ret, tot_num_rel, tot_num_rel_ret,
           avg_prec_at_recalls, mean_avg_prec,
           avg_prec_at_cutoffs, avg_r_prec)
