import matplotlib.pyplot as plt
import networkx as nx


def draw_social_network(G, output_path, top_n=40):
    """
    Draw handover social network.

    Parameters
    ----------
    G : nx.DiGraph
    output_path : str or Path
    top_n : int
        Keep top N nodes by degree for readability
    """

    if G.number_of_nodes() == 0:
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, "No social network data available", ha="center", va="center")
        plt.axis("off")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        return

    # Keep top nodes for clearer visualization
    degree_dict = dict(G.degree())
    top_nodes = sorted(degree_dict, key=degree_dict.get, reverse=True)[:top_n]
    H = G.subgraph(top_nodes).copy()

    plt.figure(figsize=(14, 10))

    pos = nx.spring_layout(H, k=0.8, seed=42)

    weights = [H[u][v]["weight"] for u, v in H.edges()]
    max_w = max(weights) if weights else 1
    widths = [w / max_w * 4 for w in weights]

    node_sizes = [H.degree(n) * 120 + 300 for n in H.nodes()]

    nx.draw_networkx_nodes(
        H,
        pos,
        node_size=node_sizes,
        node_color="lightgreen"
    )

    nx.draw_networkx_edges(
        H,
        pos,
        width=widths,
        edge_color="darkblue",
        arrows=True,
        alpha=0.8
    )

    nx.draw_networkx_labels(
        H,
        pos,
        font_size=7
    )

    plt.title("Handover Graph - Social Network from Event Log")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()