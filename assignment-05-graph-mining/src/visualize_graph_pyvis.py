import os
import math
import json
import pandas as pd
import networkx as nx
from pyvis.network import Network


START_NODE = "START_NODE"
END_NODE = "END_NODE"


def load_graph(nodes_path, edges_path):
    """
    Load graph from nodes.csv and edges.csv.
    """
    nodes_df = pd.read_csv(nodes_path)
    edges_df = pd.read_csv(edges_path)

    graph = nx.DiGraph()

    for _, row in nodes_df.iterrows():
        label = str(row["label"]).strip()
        if label:
            graph.add_node(label)

    for _, row in edges_df.iterrows():
        source = str(row["source_label"]).strip()
        target = str(row["target_label"]).strip()
        weight = float(row["weight"])

        if source and target:
            graph.add_edge(source, target, weight=weight)

    print(f"Original graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    return graph


def add_explicit_start_end_nodes(graph):
    """
    Add explicit START and END nodes to align with BPMN-style process flow.
    """
    graph = graph.copy()

    original_nodes = [n for n in graph.nodes() if n not in [START_NODE, END_NODE]]

    start_candidates = [n for n in original_nodes if graph.in_degree(n) == 0]
    end_candidates = [n for n in original_nodes if graph.out_degree(n) == 0]

    graph.add_node(START_NODE)
    graph.add_node(END_NODE)

    # If no natural starts/ends exist because the graph is strongly connected,
    # we infer them from edge frequency heuristics.
    if not start_candidates:
        incoming_weight = {}
        for node in original_nodes:
            total_in = sum(graph[u][node].get("weight", 1.0) for u in graph.predecessors(node))
            incoming_weight[node] = total_in

        min_in = min(incoming_weight.values())
        start_candidates = [n for n, w in incoming_weight.items() if w == min_in]

    if not end_candidates:
        outgoing_weight = {}
        for node in original_nodes:
            total_out = sum(graph[node][v].get("weight", 1.0) for v in graph.successors(node))
            outgoing_weight[node] = total_out

        min_out = min(outgoing_weight.values())
        end_candidates = [n for n, w in outgoing_weight.items() if w == min_out]

    for node in start_candidates:
        if not graph.has_edge(START_NODE, node):
            graph.add_edge(START_NODE, node, weight=1.0)

    for node in end_candidates:
        if not graph.has_edge(node, END_NODE):
            graph.add_edge(node, END_NODE, weight=1.0)

    print(f"Graph with START/END: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print(f"Start candidates: {start_candidates}")
    print(f"End candidates: {end_candidates}")

    return graph, start_candidates, end_candidates


def compute_metrics(graph):
    """
    Compute node metrics for visualization and right-side panel.
    """
    betweenness = nx.betweenness_centrality(graph, normalized=True)
    degree_centrality = nx.degree_centrality(graph)

    metrics = {}
    for node in graph.nodes():
        metrics[node] = {
            "betweenness": round(betweenness.get(node, 0.0), 4),
            "degree": round(degree_centrality.get(node, 0.0), 4),
            "in_degree": int(graph.in_degree(node)),
            "out_degree": int(graph.out_degree(node)),
        }

    return metrics


def compute_node_order(graph):
    """
    Compute a readable flow order from START to END.
    If the graph contains cycles, use shortest-path distance from START,
    then tie-break alphabetically.
    """
    nodes = [n for n in graph.nodes() if n not in [START_NODE, END_NODE]]

    try:
        distances = nx.single_source_shortest_path_length(graph, START_NODE)
    except Exception:
        distances = {}

    def sort_key(node):
        return (distances.get(node, 999999), node)

    ordered_nodes = sorted(nodes, key=sort_key)
    return ordered_nodes


def compute_layout_levels(graph, ordered_nodes):
    """
    Assign x/y positions to create a BPMN-like left-to-right flow.
    """
    distance_map = nx.single_source_shortest_path_length(graph, START_NODE)

    level_nodes = {}
    for node in ordered_nodes:
        level = distance_map.get(node, 1)
        level_nodes.setdefault(level, []).append(node)

    positions = {}

    # START
    positions[START_NODE] = {"x": 0, "y": 0}

    # Middle nodes by level
    x_gap = 260
    y_gap = 140

    for level in sorted(level_nodes.keys()):
        current_nodes = level_nodes[level]
        for idx, node in enumerate(current_nodes):
            y_centering = (len(current_nodes) - 1) / 2.0
            y = (idx - y_centering) * y_gap
            positions[node] = {
                "x": level * x_gap,
                "y": y
            }

    # END placed after the farthest level
    max_level = max(level_nodes.keys()) if level_nodes else 1
    positions[END_NODE] = {"x": (max_level + 1) * x_gap, "y": 0}

    return positions


def normalize_edge_width(weight, min_weight, max_weight):
    """
    Normalize edge width using log scale so heavy transitions do not dominate the graph.
    """
    if max_weight == min_weight:
        return 3.0

    log_w = math.log1p(weight)
    log_min = math.log1p(min_weight)
    log_max = math.log1p(max_weight)

    normalized = (log_w - log_min) / (log_max - log_min)
    return round(1.5 + normalized * 8.0, 2)


def build_pyvis_graph(graph, metrics, positions, ordered_nodes, output_file):
    """
    Build and save the interactive BPMN-like graph.
    """
    net = Network(
        height="920px",
        width="76%",
        directed=True,
        notebook=False,
        bgcolor="#ffffff",
        font_color="#222222"
    )

    # Fixed layout to preserve BPMN-like ordering.
    net.set_options("""
    var options = {
      "physics": {
        "enabled": false
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": {
          "enabled": true,
          "speed": { "x": 10, "y": 10, "zoom": 0.05 }
        }
      },
      "edges": {
        "smooth": {
          "enabled": true,
          "type": "cubicBezier",
          "roundness": 0.15
        },
        "color": {
          "inherit": false
        }
      },
      "nodes": {
        "shadow": true,
        "font": {
          "size": 16,
          "face": "Arial"
        }
      }
    }
    """)

    node_index = {node: idx + 1 for idx, node in enumerate(ordered_nodes)}

    edge_weights = [data.get("weight", 1.0) for _, _, data in graph.edges(data=True)]
    min_weight = min(edge_weights)
    max_weight = max(edge_weights)

    # Add START node
    net.add_node(
        START_NODE,
        label="START",
        shape="ellipse",
        color="#2ecc71",
        size=28,
        x=positions[START_NODE]["x"],
        y=positions[START_NODE]["y"],
        physics=False,
        borderWidth=3,
        info_type="start",
        display_name="START",
        sequence_no="",
        betweenness=metrics[START_NODE]["betweenness"],
        degree=metrics[START_NODE]["degree"],
        in_degree=metrics[START_NODE]["in_degree"],
        out_degree=metrics[START_NODE]["out_degree"]
    )

    # Add business activity nodes
    for node in ordered_nodes:
        idx = node_index[node]
        node_metrics = metrics[node]

        # BPMN-like styling
        shape = "box"
        color = "#3498db"

        if node_metrics["betweenness"] >= 0.10:
            color = "#f39c12"

        label = f"{idx}. {node}"

        net.add_node(
            node,
            label=label,
            shape=shape,
            color=color,
            size=24,
            x=positions[node]["x"],
            y=positions[node]["y"],
            physics=False,
            borderWidth=2,
            info_type="activity",
            display_name=node,
            sequence_no=idx,
            betweenness=node_metrics["betweenness"],
            degree=node_metrics["degree"],
            in_degree=node_metrics["in_degree"],
            out_degree=node_metrics["out_degree"]
        )

    # Add END node
    net.add_node(
        END_NODE,
        label="END",
        shape="ellipse",
        color="#e74c3c",
        size=28,
        x=positions[END_NODE]["x"],
        y=positions[END_NODE]["y"],
        physics=False,
        borderWidth=3,
        info_type="end",
        display_name="END",
        sequence_no="",
        betweenness=metrics[END_NODE]["betweenness"],
        degree=metrics[END_NODE]["degree"],
        in_degree=metrics[END_NODE]["in_degree"],
        out_degree=metrics[END_NODE]["out_degree"]
    )

    # Add edges
    for source, target, data in graph.edges(data=True):
        weight = float(data.get("weight", 1.0))
        width = normalize_edge_width(weight, min_weight, max_weight)

        edge_title = f"Transition: {source} -> {target} | Frequency: {int(weight)}"

        # Different color for explicit start/end edges
        if source == START_NODE or target == END_NODE:
            edge_color = "#7f8c8d"
            dashes = True
        else:
            edge_color = "#9aa0a6"
            dashes = False

        net.add_edge(
            source,
            target,
            width=width,
            value=weight,
            color=edge_color,
            title=edge_title,
            arrows="to",
            dashes=dashes
        )

    net.save_graph(output_file)
    print(f"Saved graph to: {output_file}")


def inject_custom_ui(html_file, ordered_nodes):
    """
    Inject right-side info panel and legend into the HTML file.
    """
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    sequence_html = "".join(
        f"<li>{idx + 1}. {node}</li>"
        for idx, node in enumerate(ordered_nodes)
    )

    custom_block = f"""
<style>
  body {{
    font-family: Arial, sans-serif;
  }}

  #infoPanel {{
    position: fixed;
    top: 0;
    right: 0;
    width: 24%;
    height: 100%;
    background: #f8f9fa;
    border-left: 2px solid #dcdcdc;
    padding: 18px;
    overflow-y: auto;
    box-sizing: border-box;
    z-index: 9999;
  }}

  #infoPanel h2 {{
    margin-top: 0;
    margin-bottom: 8px;
    font-size: 22px;
  }}

  #infoPanel h3 {{
    margin-top: 18px;
    margin-bottom: 8px;
    font-size: 18px;
  }}

  #infoPanel .metric {{
    margin: 8px 0;
    font-size: 15px;
    line-height: 1.5;
  }}

  #infoPanel .legend-item {{
    margin: 6px 0;
    font-size: 14px;
  }}

  #infoPanel .dot {{
    display: inline-block;
    width: 12px;
    height: 12px;
    margin-right: 8px;
    border-radius: 50%;
    vertical-align: middle;
  }}

  #infoPanel .box {{
    display: inline-block;
    width: 14px;
    height: 10px;
    margin-right: 8px;
    border-radius: 2px;
    vertical-align: middle;
  }}

  #sequenceList {{
    margin: 0;
    padding-left: 18px;
    font-size: 13px;
    line-height: 1.45;
  }}

  #sequenceWrap {{
    max-height: 260px;
    overflow-y: auto;
    border: 1px solid #e0e0e0;
    padding: 10px;
    background: #fff;
    border-radius: 6px;
  }}
</style>

<div id="infoPanel">
  <h2>Process Graph Info</h2>
  <div class="metric">Click a node to see details.</div>

  <h3>Legend</h3>
  <div class="legend-item"><span class="dot" style="background:#2ecc71;"></span> START event</div>
  <div class="legend-item"><span class="dot" style="background:#e74c3c;"></span> END event</div>
  <div class="legend-item"><span class="box" style="background:#3498db;"></span> Normal activity</div>
  <div class="legend-item"><span class="box" style="background:#f39c12;"></span> Bottleneck-like activity</div>

  <h3>Selected Node</h3>
  <div id="selectedNodeInfo">
    <div class="metric"><b>Name:</b> -</div>
    <div class="metric"><b>Type:</b> -</div>
    <div class="metric"><b>Sequence No:</b> -</div>
    <div class="metric"><b>Betweenness:</b> -</div>
    <div class="metric"><b>Degree Centrality:</b> -</div>
    <div class="metric"><b>In-degree:</b> -</div>
    <div class="metric"><b>Out-degree:</b> -</div>
  </div>

  <h3>Flow Order</h3>
  <div id="sequenceWrap">
    <ol id="sequenceList">
      {sequence_html}
    </ol>
  </div>
</div>

<script>
  network.on("click", function(params) {{
      if (params.nodes.length > 0) {{
          var nodeId = params.nodes[0];
          var node = nodes.get(nodeId);

          var nodeType = node.info_type || "activity";
          var seqNo = (node.sequence_no === "" || node.sequence_no === undefined) ? "-" : node.sequence_no;

          document.getElementById("selectedNodeInfo").innerHTML = `
              <div class="metric"><b>Name:</b> ${{node.display_name || node.label}}</div>
              <div class="metric"><b>Type:</b> ${{nodeType}}</div>
              <div class="metric"><b>Sequence No:</b> ${{seqNo}}</div>
              <div class="metric"><b>Betweenness:</b> ${{node.betweenness}}</div>
              <div class="metric"><b>Degree Centrality:</b> ${{node.degree}}</div>
              <div class="metric"><b>In-degree:</b> ${{node.in_degree}}</div>
              <div class="metric"><b>Out-degree:</b> ${{node.out_degree}}</div>
          `;
      }}
  }});
</script>
"""

    html = html.replace("</body>", custom_block + "\n</body>")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)

    print("Injected right-side panel and legend successfully.")


def main():
    print("===== FINAL BPMN-LIKE PROCESS GRAPH =====")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    nodes_path = os.path.join(project_root, "data", "processed", "nodes.csv")
    edges_path = os.path.join(project_root, "data", "processed", "edges.csv")
    output_file = os.path.join(project_root, "outputs", "process_graph.html")

    if not os.path.exists(nodes_path):
        raise FileNotFoundError(f"nodes.csv not found: {nodes_path}")

    if not os.path.exists(edges_path):
        raise FileNotFoundError(f"edges.csv not found: {edges_path}")

    graph = load_graph(nodes_path, edges_path)
    graph, start_candidates, end_candidates = add_explicit_start_end_nodes(graph)

    metrics = compute_metrics(graph)
    ordered_nodes = compute_node_order(graph)
    positions = compute_layout_levels(graph, ordered_nodes)

    build_pyvis_graph(
        graph=graph,
        metrics=metrics,
        positions=positions,
        ordered_nodes=ordered_nodes,
        output_file=output_file
    )

    inject_custom_ui(output_file, ordered_nodes)

    print("Done.")


if __name__ == "__main__":
    main()