import pandas as pd
import networkx as nx


def compute_process_metrics(G):
    """
    Compute graph metrics for activities in process graph.

    Metrics:
    - PageRank
    - Betweenness centrality
    - In-degree
    - Out-degree
    """

    pagerank = nx.pagerank(G)

    betweenness = nx.betweenness_centrality(G)

    rows = []

    for node in G.nodes():

        rows.append({
            "activity": node,
            "pagerank": pagerank.get(node, 0),
            "betweenness": betweenness.get(node, 0),
            "in_degree": G.in_degree(node),
            "out_degree": G.out_degree(node)
        })

    df = pd.DataFrame(rows)

    df = df.sort_values("pagerank", ascending=False)

    return df