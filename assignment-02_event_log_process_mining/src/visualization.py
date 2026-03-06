import matplotlib.pyplot as plt
import networkx as nx


# =====================================================
# PROCESS GRAPH
# =====================================================

def draw_process_graph(G, output_dir):
    """
    Draw process activity graph
    """

    plt.figure(figsize=(12, 9))

    pos = nx.spring_layout(G, seed=42)

    node_sizes = [
        900 + 120 * G.degree(n)
        for n in G.nodes()
    ]

    edge_widths = []
    edge_labels = {}

    for u, v, data in G.edges(data=True):

        weight = data.get("weight", 1)

        edge_widths.append(0.5 + weight * 0.2)

        edge_labels[(u, v)] = weight

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="lightblue",
        node_size=node_sizes
    )

    nx.draw_networkx_edges(
        G,
        pos,
        width=edge_widths,
        edge_color="gray",
        arrows=True,
        alpha=0.6
    )

    nx.draw_networkx_labels(
        G,
        pos,
        font_size=9
    )

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=8
    )

    plt.title("Process Graph")

    plt.axis("off")

    plt.tight_layout()

    plt.savefig(
        output_dir / "process_graph.png",
        dpi=300
    )

    plt.close()


# =====================================================
# HANDOVER SOCIAL NETWORK
# =====================================================

def draw_handover_graph(G, output_dir):

    plt.figure(figsize=(16, 12))

    if G.number_of_nodes() == 0:

        plt.text(
            0.5,
            0.5,
            "No handover transitions",
            ha="center",
            va="center",
            fontsize=14
        )

        plt.axis("off")

        plt.savefig(
            output_dir / "handover_graph.png",
            dpi=300
        )

        plt.close()

        return

    # -------------------------------------------------

    pos = nx.spring_layout(
        G,
        seed=42,
        k=2.0,
        iterations=200
    )

    # -------------------------------------------------
    # NODE SIZE BASED ON DEGREE
    # -------------------------------------------------

    degrees = dict(G.degree())

    node_sizes = [
        300 + degrees[n] * 120
        for n in G.nodes()
    ]

    # -------------------------------------------------
    # EDGE WIDTH BASED ON WEIGHT
    # -------------------------------------------------

    weights = [
        G[u][v]["weight"]
        for u, v in G.edges()
    ]

    max_w = max(weights)

    widths = [
        0.5 + (w / max_w) * 3
        for w in weights
    ]

    # -------------------------------------------------
    # DRAW NODES
    # -------------------------------------------------

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color="lightgreen",
        node_size=node_sizes,
        alpha=0.9
    )

    # -------------------------------------------------
    # DRAW EDGES
    # -------------------------------------------------

    nx.draw_networkx_edges(
        G,
        pos,
        width=widths,
        edge_color="gray",
        arrows=True,
        alpha=0.5,
        connectionstyle="arc3,rad=0.08"
    )

    # -------------------------------------------------
    # NODE LABELS
    # -------------------------------------------------

    nx.draw_networkx_labels(
        G,
        pos,
        font_size=8
    )

    # -------------------------------------------------
    # EDGE LABELS (WEIGHT)
    # -------------------------------------------------

    edge_labels = {
        (u, v): G[u][v]["weight"]
        for u, v in G.edges()
    }

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=6
    )

    # -------------------------------------------------

    plt.title("Handover of Work Social Network")

    plt.axis("off")

    plt.tight_layout()

    plt.savefig(
        output_dir / "handover_graph.png",
        dpi=300
    )

    plt.close()