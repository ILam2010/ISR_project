README_HW4 = 
HW4 - Link Analysis (PageRank & HITS)

Overview:
This project builds a document link graph and applies ranking algorithms to measure document importance.

What this project does:
- Builds a document similarity graph using TF-IDF and cosine similarity
- Creates a link graph where each document connects to its most similar documents
- Applies PageRank to compute global importance of documents
- Applies HITS algorithm to compute authority and hub scores

Algorithms Used:
- PageRank (with damping factor 0.85)
- HITS (Authority + Hub computation)

How to Run:
1. Run PageRank:
   python PageRank.py

2. Run HITS:
   python HITS.py

3. Run Dummy Graph Tests:
   python PageRankDummy.py

Output Files:
- pagerank_results.txt
- auth.txt
- hub.txt

Key Idea:
Documents are treated as nodes in a graph, and links are based on similarity instead of hyperlinks.

