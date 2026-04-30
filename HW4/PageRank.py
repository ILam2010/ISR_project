# PageRank.py

DAMPING = 0.85
ITERATIONS = 20


def read_graph(file):
    graph = {}
    nodes = set()

    with open(file, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue

            node = parts[0]
            links = parts[1:]

            graph[node] = links
            nodes.add(node)

            for l in links:
                nodes.add(l)

    # ensure all nodes exist
    for n in nodes:
        if n not in graph:
            graph[n] = []

    return graph, nodes


def pagerank(graph, nodes):
    N = len(nodes)
    rank = {n: 1 / N for n in nodes}

    for _ in range(ITERATIONS):
        new_rank = {n: (1 - DAMPING) / N for n in nodes}

        # sink nodes (no outgoing links)
        sink_rank = sum(rank[n] for n in nodes if len(graph[n]) == 0)

        for n in nodes:
            # distribute sink evenly
            new_rank[n] += DAMPING * sink_rank / N

        for n in nodes:
            if len(graph[n]) == 0:
                continue

            share = rank[n] / len(graph[n])
            for out in graph[n]:
                new_rank[out] += DAMPING * share

        rank = new_rank

    return rank


def save_results(rank):
    with open("pagerank_results.txt", "w") as f:
        for k, v in sorted(rank.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{k} {v}\n")


def main():
    graph, nodes = read_graph("linkgraph.txt")  # ✅ FIXED HERE
    rank = pagerank(graph, nodes)
    save_results(rank)

    print("PageRank completed. Results saved.")


if __name__ == "__main__":
    main()
