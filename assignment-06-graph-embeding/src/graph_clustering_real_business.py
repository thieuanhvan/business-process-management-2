import networkx as nx
import numpy as np
from sklearn.cluster import KMeans


# =========================
# 1. CREATE REAL BUSINESS PROCESSES
# =========================

def create_process_graphs():
    graphs = []
    labels = []

    # -------- FINANCE 1: Invoice Processing
    G1 = nx.DiGraph()
    G1.add_edges_from([
        ("Start","Receive Invoice"),
        ("Receive Invoice","Validate Invoice"),
        ("Validate Invoice","Reject"),
        ("Validate Invoice","Approve"),
        ("Reject","End"),
        ("Approve","Make Payment"),
        ("Make Payment","End")
    ])
    graphs.append(G1)
    labels.append("Finance")

    # -------- FINANCE 2: Loan Approval
    G2 = nx.DiGraph()
    G2.add_edges_from([
        ("Start","Submit Loan"),
        ("Submit Loan","Check Credit"),
        ("Check Credit","Reject"),
        ("Check Credit","Approve"),
        ("Reject","End"),
        ("Approve","Disburse Loan"),
        ("Disburse Loan","End")
    ])
    graphs.append(G2)
    labels.append("Finance")

    # -------- MANUFACTURING 1
    G3 = nx.DiGraph()
    G3.add_edges_from([
        ("Start","Prepare Materials"),
        ("Prepare Materials","Assemble Product"),
        ("Assemble Product","Test Product"),
        ("Test Product","Package Product"),
        ("Package Product","End")
    ])
    graphs.append(G3)
    labels.append("Manufacturing")

    # -------- MANUFACTURING 2 (Food Production)
    G4 = nx.DiGraph()
    G4.add_edges_from([
        ("Start","Prepare Ingredients"),
        ("Prepare Ingredients","Cook Food"),
        ("Cook Food","Quality Check"),
        ("Quality Check","Pack Food"),
        ("Pack Food","End")
    ])
    graphs.append(G4)
    labels.append("Manufacturing")

    return graphs, labels


# =========================
# 2. GRAPH → FEATURE VECTOR
# =========================

def graph_to_vector(G):
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()

    degrees = [d for _, d in G.degree()]
    avg_degree = np.mean(degrees)

    density = nx.density(G)

    branching_nodes = sum(1 for n in G.nodes() if G.out_degree(n) > 1)
    end_nodes = sum(1 for n in G.nodes() if G.out_degree(n) == 0)

    return np.array([
        num_nodes,
        num_edges,
        avg_degree,
        density,
        branching_nodes,
        end_nodes
    ])


def build_embeddings(graphs):
    return np.array([graph_to_vector(G) for G in graphs])


# =========================
# 3. CLUSTERING
# =========================

def run_clustering(embeddings):
    model = KMeans(n_clusters=2, random_state=42, n_init=10)
    return model.fit_predict(embeddings)


# =========================
# 4. PRINT RESULT
# =========================

def print_result(cluster_labels, true_labels):
    print("\n===== CLUSTER RESULT =====")

    clusters = {}
    for i, c in enumerate(cluster_labels):
        clusters.setdefault(c, []).append(i)

    for c, items in clusters.items():
        print(f"\nCluster {c}:")
        for i in items:
            print(f" - Graph {i} ({true_labels[i]})")


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    graphs, true_labels = create_process_graphs()

    print("===== PROCESS TYPES =====")
    for i, label in enumerate(true_labels):
        print(f"Graph {i}: {label}")

    embeddings = build_embeddings(graphs)

    print("\n===== EMBEDDINGS =====")
    print(embeddings)

    cluster_labels = run_clustering(embeddings)

    print_result(cluster_labels, true_labels)