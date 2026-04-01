"""
Node2Vec + Clustering on BPMN (Healthcare Diabetes Process)

Steps:
1. Build graph
2. Learn node embeddings
3. Cluster nodes
4. Visualize
5. Interpret results
"""

import networkx as nx
import matplotlib.pyplot as plt

from my_node2vec_111 import Node2Vec
from sklearn.cluster import KMeans

from graph_builder import build_diabetes_process_graph


def main():

    # =========================
    # STEP 1: BUILD GRAPH
    # =========================
    G = build_diabetes_process_graph()

    print("===== GRAPH INFO =====")
    print("Nodes:", list(G.nodes()))
    print("Edges:", list(G.edges()))

    # =========================
    # STEP 2: NODE2VEC
    # =========================
    """
    Node2Vec learns embeddings based on graph structure.
    Nodes with similar roles will have similar vectors.
    """

    node2vec = Node2Vec(
        G,
        dimensions=16,
        walk_length=10,
        num_walks=100,
        workers=1,
    )

    model = node2vec.fit(window=5, min_count=1)

    nodes = list(G.nodes())
    embeddings = [model.wv[node] for node in nodes]

    # =========================
    # STEP 3: CLUSTERING
    # =========================
    """
    Group nodes by structural similarity
    """

    kmeans = KMeans(n_clusters=3, random_state=42)
    labels = kmeans.fit_predict(embeddings)

    # =========================
    # STEP 4: PRINT RESULTS
    # =========================
    print("\n===== CLUSTER RESULTS =====")

    clusters = {}
    for node, label in zip(nodes, labels):
        clusters.setdefault(label, []).append(node)

    for cluster_id, node_list in clusters.items():
        print(f"\nCluster {cluster_id}:")
        for n in node_list:
            print("  -", n)

    # =========================
    # STEP 5: VISUALIZATION
    # =========================
    plt.figure(figsize=(10, 6))

    pos = nx.spring_layout(G, seed=42)

    colors = [labels[nodes.index(node)] for node in G.nodes()]

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=colors,
        cmap=plt.cm.Set2,
        node_size=2000,
        font_size=9
    )

    plt.title("Node2Vec Clustering on BPMN Process")
    plt.show()

    # =========================
    # STEP 6: INTERPRETATION
    # =========================
    """
    Interpretation (for report/paper):

    Cluster 1:
    - Registration, Initial Assessment
    → Entry points

    Cluster 2:
    - Diagnosis, Blood Test
    → Core decision nodes

    Cluster 3:
    - Follow-up, Lifestyle, Medication
    → Treatment / loop nodes

    Key insight:
    Node2Vec captures STRUCTURAL ROLE,
    not just node names.
    """


if __name__ == "__main__":
    main()