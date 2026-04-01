from pathlib import Path

import pandas as pd
from pyvis.network import Network


def load_data():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir.parent / "data"

    graphs = pd.read_csv(data_dir / "graph.csv")
    nodes = pd.read_csv(data_dir / "node.csv")
    edges = pd.read_csv(data_dir / "edge.csv")

    return graphs, nodes, edges


def get_node_color(node_type: str) -> str:
    if node_type == "start":
        return "#7BE141"
    if node_type == "end":
        return "#FB7E81"
    return "#97C2FC"


def build_single_network(graphs_df: pd.DataFrame, nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> Network:
    net = Network(
        height="800px",
        width="100%",
        directed=True,
        bgcolor="white",
        font_color="black"
    )

    net.set_options("""
    const options = {
      "physics": {
        "enabled": true,
        "stabilization": {
          "enabled": true,
          "iterations": 1000
        }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      },
      "nodes": {
        "shape": "dot",
        "size": 22,
        "font": {
          "size": 16
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true
          }
        },
        "font": {
          "size": 12,
          "align": "middle"
        },
        "smooth": {
          "enabled": true,
          "type": "dynamic"
        }
      }
    }
    """)

    graph_name_map = {
        int(row["graph_id"]): str(row["graph_name"])
        for _, row in graphs_df.iterrows()
    }

    # Add all nodes from all graphs into the same network
    for _, row in nodes_df.iterrows():
        graph_id = int(row["graph_id"])
        node_id = int(row["node"])
        label = str(row["label"])
        node_type = str(row["type"])
        graph_name = graph_name_map.get(graph_id, f"Graph {graph_id}")

        net.add_node(
            node_id,
            label=label,
            title=(
                f"Node: {label}<br>"
                f"Type: {node_type}<br>"
                f"Graph ID: {graph_id}<br>"
                f"Graph Name: {graph_name}"
            ),
            color=get_node_color(node_type)
        )

    # Add all edges from all graphs into the same network
    for _, row in edges_df.iterrows():
        graph_id = int(row["graph_id"])
        source = int(row["source"])
        target = int(row["target"])
        edge_type = str(row["label"])
        prob = row["prob"]

        net.add_edge(
            source,
            target,
            label=f"{edge_type} ({prob})",
            title=(
                f"Graph ID: {graph_id}<br>"
                f"Type: {edge_type}<br>"
                f"Probability: {prob}"
            )
        )

    return net


def add_single_legend(html_file: Path):
    legend_html = """
    <div style="
        position:absolute;
        top:20px;
        left:20px;
        z-index:9999;
        background:white;
        padding:12px 14px;
        border:1px solid #999;
        border-radius:8px;
        font-family:Arial,sans-serif;
        font-size:14px;
        line-height:1.6;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);
    ">
        <b>Legend</b><br>
        <span style="color:#7BE141;">●</span> Start Event<br>
        <span style="color:#97C2FC;">●</span> Task/Event<br>
        <span style="color:#FB7E81;">●</span> End Event<br><br>

        <b>Edge Types</b><br>
        sequence = normal flow<br>
        xor = decision branch<br>
        parallel = parallel branch
    </div>
    """

    html = html_file.read_text(encoding="utf-8")
    html = html.replace("<body>", "<body>\n" + legend_html, 1)
    html_file.write_text(html, encoding="utf-8")


def main():
    graphs_df, nodes_df, edges_df = load_data()

    print("Graphs:")
    print(graphs_df)

    print("\nNodes:")
    print(nodes_df)

    print("\nEdges:")
    print(edges_df)

    net = build_single_network(graphs_df, nodes_df, edges_df)

    output_dir = Path(__file__).resolve().parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "bp_graph.html"
    net.write_html(str(output_file))

    add_single_legend(output_file)

    print(f"\nSaved one HTML file only: {output_file}")


if __name__ == "__main__":
    main()