"""
Node2Vec on BPMN-like Healthcare Process (Diabetes)

Steps:
1. Build process graph (BPMN simplified)
2. Learn node embeddings using Node2Vec
3. Apply clustering (KMeans)
4. Interpret clusters based on structure

Author: You + ChatGPT
"""

import networkx as nx
from my_node2vec_111 import Node2Vec
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# =========================
# STEP 1: BUILD BPMN GRAPH
# =========================

G = nx.DiGraph()

edges = [
    ("Registration", "Initial Assessment"),
    ("Initial Assessment", "Blood Test"),
    ("Initial Assessment", "Diagnosis"),
    ("Blood Test", "Diagnosis"),
    ("Diagnosis", "Medication Prescription"),
    ("Diagnosis", "Lifestyle Advice"),
    ("Medication Prescription", "Follow-up Visit"),
    ("Lifestyle Advice", "Follow-up Visit"),
    ("Follow-up Visit", "Follow-up Visit"),  # loop
    ("Diagnosis", "Emergency Care"),
]

G.add_edges_from(edges)

print("Nodes:", G.nodes())
print("Edges:", G.edges())

# =========================
# STEP 2: NODE2VEC EMBEDDING
# =========================

"""
Node2Vec learns embedding vectors for each node
based on graph structure (neighbors, paths, etc.)
"""

node2vec = Node2Vec(
    G,
    dimensions=16,
    walk_length=10,
    num_walks=100,
    workers=1
)

model = node2vec.fit(window=5, min_count=1)

# Extract embeddings
embeddings = []
nodes = list(G.nodes())

for node in nodes:
    embeddings.append(model.wv[node])

# =========================
# STEP 3: CLUSTERING
# =========================

"""
Group nodes with similar structural roles
"""

kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(embeddings)

# =========================
# STEP 4: PRINT RESULTS
# =========================

print("\n===== CLUSTER RESULTS =====")

cluster_dict = {}
for node, label in zip(nodes, labels):
    cluster_dict.setdefault(label, []).append(node)

for cluster, node_list in cluster_dict.items():
    print(f"\nCluster {cluster}:")
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

plt.title("BPMN Node Clustering (Node2Vec)")
plt.show()

# =========================
# STEP 6: INTERPRETATION
# =========================

"""
Interpret clusters based on process roles:

Typical pattern:

Cluster A:
- Registration, Initial Assessment
→ START / ENTRY nodes

Cluster B:
- Diagnosis, Blood Test
→ DECISION / CORE PROCESS nodes

Cluster C:
- Follow-up, Lifestyle Advice, Medication
→ TREATMENT / LOOP nodes

Node2Vec groups nodes not by name,
but by STRUCTURAL POSITION in graph.
"""