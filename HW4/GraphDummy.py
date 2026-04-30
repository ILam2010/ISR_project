# GraphDummy.py (FIXED VERSION)

docID = set()
graph = {}

# -----------------------------
# Dummy graph (source → outlinks)
# -----------------------------
dummy_graph = {
    "A": ["B", "C"],
    "B": ["C"],
    "C": ["A"],
    "D": ["C"],
    "E": ["D"]
}

# -----------------------------
# Build graph
# -----------------------------
for source, outlinks in dummy_graph.items():
    docID.add(source)
    graph[source] = outlinks

    for ol in outlinks:
        docID.add(ol)

# Ensure all nodes exist
for node in docID:
    if node not in graph:
        graph[node] = []

# -----------------------------
# Identify sink nodes
# -----------------------------
sinkNodes = {node for node in docID if len(graph[node]) == 0}

# -----------------------------
# Write LinkGraphDummy.txt
# format: source out1 out2 out3
# -----------------------------
with open("linkgraph.txt", "w") as f:
    for node in graph:
        line = node + " " + " ".join(graph[node])
        f.write(line + "\n")

# -----------------------------
# Output debug info
# -----------------------------
print("Doc IDs:", docID)
print("Sink Nodes:", sinkNodes)
print("Graph written to LinkGraphDummy.txt")
