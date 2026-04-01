def find_all_cycles(graph):
    visited = {node: 0 for node in graph}  # 0: white, 1: gray, 2: black
    parent = {node: None for node in graph}
    cycles = []

    def dfs(u, p):
        visited[u] = 1
        parent[u] = p

        for v in graph.get(u, []):
            if v == p:  # Bỏ qua nút cha vừa đi tới
                continue

            if visited[v] == 1:
                # Tìm thấy một chu kỳ (Back-edge)
                current_cycle = []
                curr = u
                current_cycle.append(v)
                while curr != v:
                    current_cycle.append(curr)
                    curr = parent[curr]
                cycles.append(current_cycle)

            elif visited[v] == 0:
                dfs(v, u)

        visited[u] = 2

    for node in graph:
        if visited[node] == 0:
            dfs(node, None)

    return cycles


# --- Chạy thử ví dụ ---
# Đồ thị có 2 chu kỳ: (0-1-2) và (2-3-4)
#graph = {
#    0: [1, 2],
#    1: [0, 2],
#    2: [0, 1, 3, 4],
#    3: [2, 4],
#    4: [2, 3]
#}
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

found_cycles = find_all_cycles(graph)

if found_cycles:
    print(f"Tìm thấy {len(found_cycles)} chu kỳ:")
    for i, cycle in enumerate(found_cycles):
        print(f"Chu kỳ {i + 1}: {' -> '.join(map(str, cycle + [cycle[0]]))}")
else:
    print("Không tìm thấy chu kỳ nào.")

