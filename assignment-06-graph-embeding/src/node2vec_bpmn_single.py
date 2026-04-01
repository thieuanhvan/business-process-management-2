import networkx as nx
import numpy as np
from node2vec import Node2Vec
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# =========================
# 1. BUILD BPMN GRAPH (HARD-CODE)
# =========================

def build_graph():
    """
    Example: Online Order Fulfillment Process
    """

    G = nx.DiGraph()

    # Nodes
    nodes = {
        0: ("Start", "START"),
        1: ("Receive Order", "TASK"),
        2: ("Validate Payment", "TASK"),
        3: ("Payment Failed", "EVENT"),
        4: ("Check Inventory", "TASK"),
        5: ("Out of Stock", "EVENT"),
        6: ("Pack Items", "TASK"),
        7: ("Ship Order", "TASK"),
        8: ("Complete Order", "END"),
        9: ("Cancel Order", "END"),
        10: ("Notify Customer", "EVENT")
    }

    for node_id, (label, node_type) in nodes.items():
        G.add_node(node_id, label=label, type=node_type)

    # Edges (flow)
    edges = [
        (0,1),
        (1,2),
        (2,3),
        (2,4),
        (3,9),
        (4,5),
        (4,6),
        (5,10),
        (10,9),
        (6,7),
        (7,8)
    ]

    G.add_edges_from(edges)

    return G


# =========================
# 2. NODE2VEC
# =========================

def run_node2vec(G):
    node2vec = Node2Vec(
        G,
        dimensions=16,
        walk_length=10,
        num_walks=50,
        workers=1
    )

    model = node2vec.fit(window=5, min_count=1)

    nodes = list(G.nodes())
    embeddings = np.array([model.wv[str(n)] for n in nodes])

    return nodes, embeddings


# =========================
# 3. CLUSTERING (KMEANS)
# =========================

def run_clustering(nodes, embeddings, k=3):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    cluster_map = dict(zip(nodes, labels))
    return cluster_map


# =========================
# 4. EXPLAIN
# =========================

def explain(G, cluster_map):
    print("\n===== CLUSTER RESULT =====")

    clusters = {}

    for node, c in cluster_map.items():
        clusters.setdefault(c, []).append(node)

    for c, nodes in clusters.items():
        print(f"\nCluster {c}:")

        for n in nodes:
            label = G.nodes[n]['label']
            node_type = G.nodes[n]['type']
            print(f" - {label} [{node_type}]")

        # SIMPLE EXPLANATION
        types = [G.nodes[n]['type'] for n in nodes]

        if "START" in types or "END" in types:
            print(" -> Control nodes (Start/End)")
        elif "EVENT" in types:
            print(" -> Exception / notification events")
        else:
            print(" -> Core business tasks (main flow)")


# =========================
# 5. VISUALIZE
# =========================

def visualize(G, cluster_map):
    plt.figure(figsize=(12, 7))

    pos = nx.spring_layout(G, seed=42)

    colors = [cluster_map[n] for n in G.nodes()]
    labels = {n: G.nodes[n]['label'] for n in G.nodes()}

    nx.draw(
        G,
        pos,
        labels=labels,
        node_color=colors,
        cmap=plt.cm.Set3,
        node_size=2000,
        font_size=8,
        arrows=True
    )

    plt.title("BPMN Graph + Node2Vec Clustering")
    plt.show()


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    # Step 1: BPMN -> Graph
    G = build_graph()
    print("Graph created:", G.number_of_nodes(), "nodes")

    # Step 2: Node2Vec
    nodes, embeddings = run_node2vec(G)

    # Step 3: Clustering
    cluster_map = run_clustering(nodes, embeddings, k=3)

    # Step 4: Explain
    explain(G, cluster_map)

    # Step 5: Visualize
    visualize(G, cluster_map)