import networkx as nx


def build_handover_graph(df):

    G = nx.DiGraph()

    df = df.sort_values(["case_id", "timestamp"])

    for case_id, group in df.groupby("case_id"):

        resources = group["resource"].tolist()

        for i in range(len(resources) - 1):

            r1 = resources[i]
            r2 = resources[i + 1]

            if r1 == r2:
                continue

            if G.has_edge(r1, r2):
                G[r1][r2]["weight"] += 1
            else:
                G.add_edge(r1, r2, weight=1)

    return G


def compute_centrality(G):

    degree = nx.degree_centrality(G)

    betweenness = nx.betweenness_centrality(G)

    closeness = nx.closeness_centrality(G)

    return degree, betweenness, closeness