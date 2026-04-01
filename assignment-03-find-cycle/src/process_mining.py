import networkx as nx


def build_process_graph(df):

    G = nx.DiGraph()

    df = df.sort_values(["case_id", "timestamp"])

    for case_id, group in df.groupby("case_id"):

        activities = group["activity"].tolist()

        for i in range(len(activities) - 1):

            a = activities[i]
            b = activities[i + 1]

            if G.has_edge(a, b):
                G[a][b]["weight"] += 1
            else:
                G.add_edge(a, b, weight=1)

    return G


def detect_cycles(G):

    cycles = list(nx.simple_cycles(G))

    return cycles


def classify_cycle(cycle):

    if len(cycle) == 2:
        return "REWORK"

    if len(cycle) > 2:
        return "LOOP"

    return "UNKNOWN"