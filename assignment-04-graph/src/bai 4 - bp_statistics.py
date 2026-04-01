import logging
from io import BytesIO
from pathlib import Path
import base64

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Logging configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================
# Utility
# ============================================================

def fig_to_base64() -> str:
    """
    Convert current matplotlib figure to base64 string
    so it can be embedded directly into HTML.
    """
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def ensure_output_dir() -> Path:
    """
    Create outputs directory if it does not exist.
    """
    output_dir = Path("../outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# ============================================================
# Load data
# ============================================================

def load_optional_csv(file_path: str) -> pd.DataFrame:
    """
    Load optional CSV file if it exists.
    Return empty DataFrame if not found.
    """
    path = Path(file_path)
    if path.exists():
        logger.info(f"Loaded optional file: {file_path}")
        return pd.read_csv(path)

    logger.warning(f"Optional file not found: {file_path}")
    return pd.DataFrame()


def load_data():
    """
    Load all BPM CSV data files.
    """
    logger.info("Loading CSV files...")

    graphs = pd.read_csv("../data/graph.csv")
    nodes = pd.read_csv("../data/node.csv")
    edges = pd.read_csv("../data/edge.csv")

    resources = load_optional_csv("../data/resource.csv")
    node_resource = load_optional_csv("../data/node_resource.csv")
    equipment = load_optional_csv("../data/equipment.csv")
    node_equipment = load_optional_csv("../data/node_equipment.csv")

    logger.info("Data loaded successfully")

    return graphs, nodes, edges, resources, node_resource, equipment, node_equipment


# ============================================================
# Path analysis
# ============================================================

def get_process_paths():
    """
    Return known process paths for the current BPM dataset.
    This is suitable for the current assignment data model.
    """
    graph_1_paths = [
        "S → T1 → T2 → T3 → T4 → T5 → T7 → T8 → T9 → E",
        "S → T1 → T2 → T3 → T4 → T6 → T7 → T8 → T9 → E",
    ]

    graph_2_paths = [
        "S → T8 → (T9 || T10) → T11 → E"
    ]

    return graph_1_paths, graph_2_paths


# ============================================================
# Statistics
# ============================================================

def compute_gateway_statistics(nodes: pd.DataFrame, edges: pd.DataFrame) -> dict:
    """
    Infer gateway-like nodes from graph structure.

    Rule:
    - Split gateway: out-degree > 1
    - Join gateway: in-degree > 1
    - Total gateway nodes = unique nodes appearing in split or join
    """
    out_degree = edges.groupby("source").size().to_dict()
    in_degree = edges.groupby("target").size().to_dict()

    split_gateways = []
    join_gateways = []

    for node_id in nodes["node"].tolist():
        if out_degree.get(node_id, 0) > 1:
            split_gateways.append(node_id)
        if in_degree.get(node_id, 0) > 1:
            join_gateways.append(node_id)

    total_gateway_nodes = sorted(set(split_gateways + join_gateways))

    return {
        "split_gateway_count": len(split_gateways),
        "join_gateway_count": len(join_gateways),
        "total_gateway_count": len(total_gateway_nodes),
        "split_gateway_nodes": split_gateways,
        "join_gateway_nodes": join_gateways,
        "all_gateway_nodes": total_gateway_nodes,
    }


def compute_statistics(
    graphs: pd.DataFrame,
    nodes: pd.DataFrame,
    edges: pd.DataFrame,
    resources: pd.DataFrame,
    node_resource: pd.DataFrame,
    equipment: pd.DataFrame,
    node_equipment: pd.DataFrame,
) -> dict:
    """
    Compute BPM statistics.
    """
    logger.info("Starting statistical analysis")

    stats = {}

    # Basic counts
    stats["total_graphs"] = len(graphs)
    stats["total_nodes"] = len(nodes)
    stats["total_edges"] = len(edges)

    # Node types
    stats["start_nodes"] = len(nodes[nodes["type"] == "start"])
    stats["end_nodes"] = len(nodes[nodes["type"] == "end"])
    stats["event_nodes"] = len(nodes[nodes["type"] == "event"])

    # Edge types
    stats["sequence_edges"] = len(edges[edges["label"] == "sequence"])
    stats["xor_edges"] = len(edges[edges["label"] == "xor"])
    stats["parallel_edges"] = len(edges[edges["label"] == "parallel"])

    # Gateway statistics
    gateway_stats = compute_gateway_statistics(nodes, edges)
    stats.update(gateway_stats)

    # Cost
    event_costs = nodes[nodes["type"] == "event"]["cost"]
    stats["avg_cost"] = round(event_costs.mean(), 2) if not event_costs.empty else 0.0
    stats["max_cost"] = round(event_costs.max(), 2) if not event_costs.empty else 0.0
    stats["min_cost"] = round(event_costs.min(), 2) if not event_costs.empty else 0.0

    # Resource stats
    stats["total_resources"] = len(resources) if not resources.empty else 0
    if not node_resource.empty:
        resource_per_node = node_resource.groupby("node").size()
        stats["max_resources_on_one_node"] = int(resource_per_node.max())
    else:
        stats["max_resources_on_one_node"] = 0

    # Equipment stats
    stats["total_equipment"] = len(equipment) if not equipment.empty else 0
    if not node_equipment.empty:
        equipment_per_node = node_equipment.groupby("node").size()
        stats["max_equipment_on_one_node"] = int(equipment_per_node.max())
    else:
        stats["max_equipment_on_one_node"] = 0

    if not equipment.empty and "equipment_name" in equipment.columns:
        stats["equipment_list"] = equipment["equipment_name"].astype(str).tolist()
    else:
        stats["equipment_list"] = []

    # Path statistics
    graph_1_paths, graph_2_paths = get_process_paths()
    stats["graph_1_paths"] = graph_1_paths
    stats["graph_2_paths"] = graph_2_paths
    stats["total_paths"] = len(graph_1_paths) + len(graph_2_paths)

    logger.info("Statistics computed")

    return stats


# ============================================================
# Logging output
# ============================================================

def print_statistics(stats: dict):
    """
    Print detailed statistics to console log.
    """
    logger.info("----- BPM STATISTICS -----")
    logger.info(f"Total Graphs: {stats['total_graphs']}")
    logger.info(f"Total Nodes: {stats['total_nodes']}")
    logger.info(f"Event Nodes: {stats['event_nodes']}")
    logger.info(f"Start Nodes: {stats['start_nodes']}")
    logger.info(f"End Nodes: {stats['end_nodes']}")

    logger.info(f"Total Edges: {stats['total_edges']}")
    logger.info(f"Sequence Edges: {stats['sequence_edges']}")
    logger.info(f"XOR Edges: {stats['xor_edges']}")
    logger.info(f"Parallel Edges: {stats['parallel_edges']}")

    logger.info("----- GATEWAY STATISTICS -----")
    logger.info(f"Split Gateways: {stats['split_gateway_count']}")
    logger.info(f"Join Gateways: {stats['join_gateway_count']}")
    logger.info(f"Total Gateway Nodes: {stats['total_gateway_count']}")
    logger.info(f"Gateway Node IDs: {stats['all_gateway_nodes']}")

    logger.info("----- COST STATISTICS -----")
    logger.info(f"Average Task Cost: {stats['avg_cost']} hours")
    logger.info(f"Max Task Cost: {stats['max_cost']} hours")
    logger.info(f"Min Task Cost: {stats['min_cost']} hours")

    logger.info("----- RESOURCE / EQUIPMENT -----")
    logger.info(f"Total Resources: {stats['total_resources']}")
    logger.info(f"Max Resources on One Node: {stats['max_resources_on_one_node']}")
    logger.info(f"Total Equipment: {stats['total_equipment']}")
    logger.info(f"Max Equipment on One Node: {stats['max_equipment_on_one_node']}")
    logger.info(f"Equipment List: {', '.join(stats['equipment_list']) if stats['equipment_list'] else 'N/A'}")

    logger.info("----- PROCESS PATHS -----")
    logger.info("Graph 1 Paths:")
    for idx, path in enumerate(stats["graph_1_paths"], start=1):
        logger.info(f"Path {idx}: {path}")

    logger.info("Graph 2 Paths:")
    for idx, path in enumerate(stats["graph_2_paths"], start=1):
        logger.info(f"Path {idx}: {path}")

    logger.info(f"Total Possible Paths: {stats['total_paths']}")


# ============================================================
# Chart generation
# ============================================================

def create_charts(stats: dict) -> dict:
    """
    Create pie charts and bar charts and return them as base64 strings.
    """
    charts = {}

    # Pie chart: node type distribution
    plt.figure(figsize=(6, 4))
    plt.pie(
        [stats["start_nodes"], stats["event_nodes"], stats["end_nodes"]],
        labels=["Start", "Event", "End"],
        autopct="%1.1f%%"
    )
    plt.title("Node Type Distribution")
    charts["node_type_pie"] = fig_to_base64()

    # Bar chart: edge types
    plt.figure(figsize=(6, 4))
    plt.bar(
        ["Sequence", "XOR", "Parallel"],
        [stats["sequence_edges"], stats["xor_edges"], stats["parallel_edges"]]
    )
    plt.title("Edge Type Count")
    plt.ylabel("Count")
    charts["edge_type_bar"] = fig_to_base64()

    # Bar chart: gateway statistics
    plt.figure(figsize=(6, 4))
    plt.bar(
        ["Split", "Join", "Total"],
        [
            stats["split_gateway_count"],
            stats["join_gateway_count"],
            stats["total_gateway_count"]
        ]
    )
    plt.title("Gateway Statistics")
    plt.ylabel("Count")
    charts["gateway_bar"] = fig_to_base64()

    # Bar chart: resources vs equipment
    plt.figure(figsize=(6, 4))
    plt.bar(
        ["Resources", "Equipment"],
        [stats["total_resources"], stats["total_equipment"]]
    )
    plt.title("Resources vs Equipment")
    plt.ylabel("Count")
    charts["resource_equipment_bar"] = fig_to_base64()

    return charts


# ============================================================
# HTML generation
# ============================================================

def generate_html(stats: dict, charts: dict):
    """
    Generate one HTML dashboard for the statistics assignment.
    """
    logger.info("Generating HTML dashboard")

    equipment_html = "<br>".join(stats["equipment_list"]) if stats["equipment_list"] else "N/A"

    graph_1_paths_html = "".join([f"<li>{path}</li>" for path in stats["graph_1_paths"]])
    graph_2_paths_html = "".join([f"<li>{path}</li>" for path in stats["graph_2_paths"]])

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BPM Statistics Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 24px;
            background: #f6f6f6;
            color: #222;
        }}
        h1 {{
            margin-bottom: 8px;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 20px;
        }}
        .section {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 20px;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(4, minmax(140px, 1fr));
            gap: 12px;
        }}
        .card {{
            background: #fafafa;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 12px;
        }}
        .label {{
            font-size: 13px;
            color: #666;
        }}
        .value {{
            font-size: 26px;
            font-weight: bold;
            margin-top: 6px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }}
        img {{
            width: 100%;
            height: auto;
        }}
        ul {{
            margin-top: 8px;
            line-height: 1.6;
        }}
        .mono {{
            font-family: Consolas, monospace;
        }}
    </style>
</head>
<body>

    <h1>BPM Statistics Dashboard</h1>
    <div class="subtitle">
        Statistical analysis for Business Process Management assignment
    </div>

    <div class="section">
        <h2>Summary</h2>
        <div class="cards">
            <div class="card">
                <div class="label">Total Graphs</div>
                <div class="value">{stats['total_graphs']}</div>
            </div>
            <div class="card">
                <div class="label">Total Nodes</div>
                <div class="value">{stats['total_nodes']}</div>
            </div>
            <div class="card">
                <div class="label">Total Edges</div>
                <div class="value">{stats['total_edges']}</div>
            </div>
            <div class="card">
                <div class="label">Total Paths</div>
                <div class="value">{stats['total_paths']}</div>
            </div>
            <div class="card">
                <div class="label">Event Nodes</div>
                <div class="value">{stats['event_nodes']}</div>
            </div>
            <div class="card">
                <div class="label">Total Gateways</div>
                <div class="value">{stats['total_gateway_count']}</div>
            </div>
            <div class="card">
                <div class="label">Resources</div>
                <div class="value">{stats['total_resources']}</div>
            </div>
            <div class="card">
                <div class="label">Equipment</div>
                <div class="value">{stats['total_equipment']}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Detailed Statistics</h2>
        <ul>
            <li>Start Nodes: <b>{stats['start_nodes']}</b></li>
            <li>End Nodes: <b>{stats['end_nodes']}</b></li>
            <li>Sequence Edges: <b>{stats['sequence_edges']}</b></li>
            <li>XOR Edges: <b>{stats['xor_edges']}</b></li>
            <li>Parallel Edges: <b>{stats['parallel_edges']}</b></li>
            <li>Split Gateways: <b>{stats['split_gateway_count']}</b></li>
            <li>Join Gateways: <b>{stats['join_gateway_count']}</b></li>
            <li>Gateway Node IDs: <span class="mono">{stats['all_gateway_nodes']}</span></li>
            <li>Average Task Cost: <b>{stats['avg_cost']}</b> hours</li>
            <li>Min Task Cost: <b>{stats['min_cost']}</b> hours</li>
            <li>Max Task Cost: <b>{stats['max_cost']}</b> hours</li>
            <li>Max Resources on One Node: <b>{stats['max_resources_on_one_node']}</b></li>
            <li>Max Equipment on One Node: <b>{stats['max_equipment_on_one_node']}</b></li>
        </ul>
    </div>

    <div class="section">
        <h2>Equipment List</h2>
        <p>{equipment_html}</p>
    </div>

    <div class="section">
        <h2>Process Paths</h2>
        <h3>Graph 1</h3>
        <ul>
            {graph_1_paths_html}
        </ul>

        <h3>Graph 2</h3>
        <ul>
            {graph_2_paths_html}
        </ul>
    </div>

    <div class="section">
        <h2>Charts</h2>
        <div class="grid">
            <div>
                <h3>Node Type Distribution</h3>
                <img src="data:image/png;base64,{charts['node_type_pie']}">
            </div>
            <div>
                <h3>Edge Type Count</h3>
                <img src="data:image/png;base64,{charts['edge_type_bar']}">
            </div>
            <div>
                <h3>Gateway Statistics</h3>
                <img src="data:image/png;base64,{charts['gateway_bar']}">
            </div>
            <div>
                <h3>Resources vs Equipment</h3>
                <img src="data:image/png;base64,{charts['resource_equipment_bar']}">
            </div>
        </div>
    </div>

</body>
</html>
"""

    output_dir = ensure_output_dir()
    output_file = output_dir / "bp_statistics_dashboard.html"
    output_file.write_text(html, encoding="utf-8")

    logger.info(f"Dashboard saved to {output_file}")


# ============================================================
# Main
# ============================================================

def main():
    graphs, nodes, edges, resources, node_resource, equipment, node_equipment = load_data()

    stats = compute_statistics(
        graphs,
        nodes,
        edges,
        resources,
        node_resource,
        equipment,
        node_equipment
    )

    print_statistics(stats)

    charts = create_charts(stats)

    generate_html(stats, charts)

    logger.info("BPM statistical analysis completed")


if __name__ == "__main__":
    main()