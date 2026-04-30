def read_file(file):
    total = 0
    count = 0

    with open(file, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                total += float(parts[1])
                count += 1

    return total, count


def main():
    pr_sum, pr_count = read_file("pagerank_results.txt")
    hub_sum, hub_count = read_file("hub.txt")
    auth_sum, auth_count = read_file("auth.txt")

    print("PageRank sum:", pr_sum, " | nodes:", pr_count)
    print("Hub sum:", hub_sum, " | nodes:", hub_count)
    print("Authority sum:", auth_sum, " | nodes:", auth_count)


if __name__ == "__main__":
    main()
