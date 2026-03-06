
import networkx as nx
import matplotlib.pyplot as plt

# 1. Tạo đồ thị (Ví dụ: Đồ thị mẫu Krackhardt Kite hoặc đồ thị tự định nghĩa)
G = nx.krackhardt_kite_graph()
# Hoặc bạn có thể tạo đồ thị tùy chỉnh bằng cách thêm cạnh:
# G = nx.Graph()
# G.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4), (4, 5)])
# 2. Tính toán các chỉ số Centrality
degree_cent = nx.degree_centrality(G)
betweenness_cent = nx.betweenness_centrality(G)
closeness_cent = nx.closeness_centrality(G)
# In kết quả ra màn hình
print(f"{'Node':<5} | {'Degree':<10} | {'Betweenness':<12} | {'Closeness':<10}")
print("-" * 45)
for node in G.nodes():
    print(f"{node:<5} | {degree_cent[node]:<10.3f} | {betweenness_cent[node]:<12.3f} | {closeness_cent[node]:<10.3f}")
# 3. Trực quan hóa đồ thị
plt.figure(figsize=(10, 7))
pos = nx.spring_layout(G)  # Thuật toán sắp xếp vị trí các nút
# Vẽ các nút, kích thước nút tỉ lệ thuận với Degree Centrality để dễ quan sát
node_sizes = [v * 5000 for v in degree_cent.values()]
nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.8)
nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')
plt.title("Mô phỏng Centrality trong Mạng lưới Xã hội", fontsize=15)
plt.axis('off')  # Tắt trục tọa độ
plt.show()
