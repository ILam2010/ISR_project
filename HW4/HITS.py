# HITS.py

ITERATIONS = 20


def read_graph(file):
    graph = {}

    with open(file, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue

            graph[parts[0]] = parts[1:]

    return graph


def get_nodes(graph):
    nodes = set(graph.keys())
    for v in graph.values():
        nodes.update(v)
    return nodes


def normalize(d):
    norm = sum(x * x for x in d.values()) ** 0.5
    if norm == 0:
        return d
    return {k: v / norm for k, v in d.items()}


def hits(graph):
    nodes = get_nodes(graph)

    auth = {n: 1.0 for n in nodes}
    hub = {n: 1.0 for n in nodes}

    for _ in range(ITERATIONS):

        new_auth = {n: 0.0 for n in nodes}
        new_hub = {n: 0.0 for n in nodes}

        # authority update
        for n in nodes:
            for p in nodes:
                if n in graph.get(p, []):
                    new_auth[n] += hub[p]

        # hub update
        for n in nodes:
            for out in graph.get(n, []):
                new_hub[n] += auth[out]

        auth = normalize(new_auth)
        hub = normalize(new_hub)

    return auth, hub


def save(file, data):
    with open(file, "w") as f:
        for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{k} {v}\n")


def main():
    graph = read_graph("linkgraph.txt")  # ✅ FIXED

    auth, hub = hits(graph)

    save("auth.txt", auth)
    save("hub.txt", hub)

    print("HITS completed. Files saved.")


if __name__ == "__main__":
    main()
