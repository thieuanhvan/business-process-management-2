# ============================================
# NODE2VEC - BPMN GRAPH EMBEDDING (FINAL)
# ============================================

# Cài thư viện nếu chưa có:
# pip install networkx node2vec

import networkx as nx
from my_node2vec_111 import Node2Vec


# --------------------------------------------
# Hàm in đẹp
# --------------------------------------------
def print_line():
    print("=" * 60)


def explain_similarity(score):
    if score >= 0.85:
        return "RẤT GIỐNG"
    elif score >= 0.75:
        return "GIỐNG"
    elif score >= 0.6:
        return "KHÁ GIỐNG"
    else:
        return "KHÔNG GIỐNG"


# --------------------------------------------
# Main
# --------------------------------------------
def main():

    # ----------------------------------------
    # 1. Tạo đồ thị BPMN
    # ----------------------------------------
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

    # ----------------------------------------
    # 2. Thông tin graph
    # ----------------------------------------
    print_line()
    print("THÔNG TIN ĐỒ THỊ\n")

    print(f"Số node: {G.number_of_nodes()}")
    print(f"Số edge: {G.number_of_edges()}")

    print("\nDanh sách node:")
    for node in G.nodes():
        print(f" - {node}")

    print("\nDanh sách edge:")
    for u, v in G.edges():
        print(f" {u} → {v}")

    # ----------------------------------------
    # 3. Chạy Node2Vec
    # ----------------------------------------
    print_line()
    print("CHẠY NODE2VEC...\n")

    node2vec = Node2Vec(
        G,
        dimensions=32,
        walk_length=10,
        num_walks=100,
        workers=1
    )

    model = node2vec.fit(window=5, min_count=1)

    # ----------------------------------------
    # 4. In embedding
    # ----------------------------------------
    print_line()
    print("NODE EMBEDDING (5 chiều đầu)\n")

    for node in G.nodes():
        vector = model.wv[node]
        print(f"{node}: {vector[:5]}")
        print("→ Vector biểu diễn node trong graph\n")

    # ----------------------------------------
    # 5. Similarity giữa các node
    # ----------------------------------------
    print_line()
    print("ĐỘ TƯƠNG ĐỒNG GIỮA CÁC NODE\n")

    nodes = list(G.nodes())

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            n1 = nodes[i]
            n2 = nodes[j]

            sim = model.wv.similarity(n1, n2)

            if sim >= 0.7:
                label = explain_similarity(sim)

                print(f"{n1} ↔ {n2}")
                print(f"  Similarity = {sim:.4f}")
                print(f"  Đánh giá   = {label}\n")

    # ----------------------------------------
    # 6. Node giống nhất
    # ----------------------------------------
    print_line()
    print("NODE GIỐNG NHAU NHẤT\n")

    for node in nodes:
        print(f"\nNode: {node}")

        similar_nodes = model.wv.most_similar(node, topn=3)

        for n, score in similar_nodes:
            label = explain_similarity(score)

            print(f"  → {n}")
            print(f"    Similarity = {score:.4f}")
            print(f"    Đánh giá   = {label}")


# --------------------------------------------
# Run
# --------------------------------------------
if __name__ == "__main__":
    main()