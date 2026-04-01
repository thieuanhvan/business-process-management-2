# ============================================
# BPMN GRAPH - BUILD & PRINT
# File: python bpmn_graph.py
# ============================================

import networkx as nx


def print_line():
    print("=" * 60)


def build_graph():
    G = nx.DiGraph()

    edges = [
        ("Start", "T1"),
        ("T1", "XOR"),
        ("XOR", "T2"),
        ("XOR", "T3"),
        ("T2", "JOIN"),
        ("T3", "JOIN"),
        ("JOIN", "T4"),
        ("T4", "End")
    ]

    G.add_edges_from(edges)
    return G


def main():
    G = build_graph()

    print_line()
    print("THÔNG TIN ĐỒ THỊ BPMN\n")

    print(f"Số node: {G.number_of_nodes()}")
    print(f"Số edge: {G.number_of_edges()}")

    print("\nDanh sách node:")
    for node in G.nodes():
        print(f" - {node}")

    print("\nDanh sách edge:")
    for u, v in G.edges():
        print(f" {u} → {v}")

    print("\nAdjacency list:")
    for node in G.nodes():
        neighbors = list(G.successors(node))
        print(f" {node} → {neighbors}")


if __name__ == "__main__":
    main()