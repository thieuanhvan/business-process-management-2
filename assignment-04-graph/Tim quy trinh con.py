# tim_quy_trinh_con_safe.py

# ===== DEFINE GRAPH =====
G1_nodes = {"A","B","C","D","E"}
G1_edges = {("A","B"),("B","C"),("C","D"),("D","E")}

G2_nodes = {"A","C","D","E","F"}
G2_edges = {("A","C"),("C","D"),("D","E"),("E","F")}

# ===== COMMON =====
common_nodes = G1_nodes & G2_nodes

common_edges = set()
for e in G1_edges:
    if e in G2_edges:
        common_edges.add(e)

# ===== PRINT =====
print("=== COMMON SUBGRAPH ===")
print("Nodes:", common_nodes)
print("Edges:", common_edges)

# ===== HTML EXPORT =====
html = "<html><body><h2>Common Subgraph</h2><ul>"
for u,v in common_edges:
    html += f"<li>{u} → {v}</li>"
html += "</ul></body></html>"

with open("common_subgraph.html","w",encoding="utf-8") as f:
    f.write(html)

print("Saved: common_subgraph.html")