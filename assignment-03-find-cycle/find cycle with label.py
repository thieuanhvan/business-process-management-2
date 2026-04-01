def print_graph_info(graph, labels):
    """Hàm in thông tin danh sách các Node và Nhãn"""
    print("DANH SÁCH THÔNG TIN NODE TRONG ĐỒ THỊ:")
    print(f"{'Node ID':<10} | {'Nhãn (Label)':<15}")
    print("-" * 30)
    for node in sorted(graph.keys()):
        label = labels.get(node, "N/A")
        print(f"{node:<10} | {label:<15}")
    print("-" * 30 + "\n")

def find_cycles_with_details(graph, labels):
    visited = {node: 0 for node in graph}  # 0: Trắng, 1: Xám, 2: Đen
    parent = {node: None for node in graph}
    all_cycles = []

    def dfs(u, p):
        visited[u] = 1
        parent[u] = p

        for v in graph.get(u, []):
            if v == p:
                continue

            if visited[v] == 1:
                # Phát hiện chu kỳ: Truy vết từ u ngược về v
                cycle = []
                curr = u
                while curr != v:
                    cycle.append(curr)
                    curr = parent[curr]
                cycle.append(v)
                # Đảo ngược để theo đúng chiều di chuyển của DFS
                all_cycles.append(cycle[::-1])

            elif visited[v] == 0:
                dfs(v, u)

        visited[u] = 2

    # Duyệt qua tất cả các đỉnh để đảm bảo không sót thành phần liên thông
    for node in graph:
        if visited[node] == 0:
            dfs(node, None)

    return all_cycles


# --- 1. Thiết lập Đồ thị (Vô hướng) ---
# graph = {
#     0: [1, 2],
#     1: [0, 2],
#     2: [0, 1, 3, 4],
#     3: [2, 4],
#     4: [2, 3]
# }
graph = {
    0: [1],
    1: [0, 2],
    2: [1, 3],
    3: [2, 4,5],
    4: [3,6],
    5: [3,6],
    6: [4,5,7],
    7: [6,8],
    8: [7]
}
# --- 2. Thiết lập Nhãn Node ---
# Gán nhãn 1 (event) ; 2 cho tất cả (Task), 3 (gateXor)
node_labels = {node: 2 for node in graph}
node_labels[0] = 1 # Node Event
node_labels[8] = 1 # Node Event
node_labels[3] = 3 ## Node Co Nhan Gate XOR
node_labels[6] = 3 ## Node Co Nhan Gate XOR

# --- 3. In danh sách Node và Nhãn trước ---
print_graph_info(graph, node_labels)
# --- 3. Thực hiện tìm kiếm ---
found_cycles = find_cycles_with_details(graph, node_labels)

# --- 4. In kết quả theo yêu cầu ---
print("DANH SÁCH CHU TRÌNH TÌM ĐƯỢC:")
print("-" * 30)

if not found_cycles:
    print("Không tìm thấy chu kỳ nào.")
else:
    for i, cycle in enumerate(found_cycles, 1):
        # Tạo danh sách các chuỗi định dạng "ID(Label)"
        formatted_nodes = [f"{node}(Label:{node_labels[node]})" for node in cycle]

        # Thêm node đầu tiên vào cuối để đóng vòng chu kỳ khi in
        first_node = cycle[0]
        formatted_nodes.append(f"{first_node}(Label:{node_labels[first_node]})")

        # Nối lại bằng mũi tên
        path_string = " -> ".join(formatted_nodes)
        print(f"Chu kỳ {i}: {path_string}")

print("-" * 30)