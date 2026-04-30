# Graph.py

def read_graph(file):
    graph = {}

    with open(file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue

            node = parts[0]
            links = parts[1:]

            graph[node] = links

    return graph


def main():
    # ✅ use REAL graph, not dummy
    graph = read_graph("linkgraph.txt")

    print("Graph loaded:")
    for k, v in graph.items():
        print(k, "->", v)


if __name__ == "__main__":
    main()
