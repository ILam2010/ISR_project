import decimal

decimal.getcontext().prec = 10

graphPages = {}
d = 0.85


class Page:
    def __init__(self, page):
        self.page = page
        self.rank = 1.0
        self.inLinkPages = []
        self.noOfOutLinks = 0


def initializegraphPages(graphFile):
    with open(graphFile, 'r') as textFile:
        for line in textFile:
            line = line.strip()

            if not line:
                continue

            pages = line.split()

            if pages[0] not in graphPages:
                graphPages[pages[0]] = Page(pages[0])

            graphPages[pages[0]].inLinkPages = pages[1:]

            for out in pages[1:]:
                if out not in graphPages:
                    graphPages[out] = Page(out)
                graphPages[out].noOfOutLinks += 1


def computePageRank(iterations=20):
    N = len(graphPages)

    for _ in range(iterations):
        newRanks = {}

        sinkPR = sum(p.rank for p in graphPages.values() if p.noOfOutLinks == 0)

        for page in graphPages:
            rank = (1 - d) / N
            rank += d * sinkPR / N

            for p in graphPages:
                if page in graphPages[p].inLinkPages and graphPages[p].noOfOutLinks > 0:
                    rank += d * graphPages[p].rank / graphPages[p].noOfOutLinks

            newRanks[page] = rank

        for page in graphPages:
            graphPages[page].rank = newRanks[page]


def printResults():
    sorted_pages = sorted(
        graphPages.items(),
        key=lambda x: x[1].rank,
        reverse=True
    )

    print("\nPageRank Results:")
    for p, obj in sorted_pages:
        print(p, obj.rank)


# ---------------- MAIN ----------------
initializegraphPages("linkgraph.txt")
computePageRank()
printResults()
