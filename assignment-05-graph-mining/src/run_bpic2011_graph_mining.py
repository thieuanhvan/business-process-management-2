import os
import math
import logging
from collections import Counter, defaultdict

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from pm4py.objects.log.importer.xes import importer as xes_importer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class BPIC2011GraphMining:
    """
    Full pipeline for Assignment 05:
    BPIC 2011 hospital event log -> process graph -> graph mining metrics.

    Main outputs:
    - events.csv
    - nodes.csv
    - edges.csv
    - path_statistics.csv
    - cycle_summary.csv
    - centrality.csv
    - graph_summary.txt
    - process_graph.png
    """

    def __init__(self, xes_path: str, processed_dir: str, outputs_dir: str):
        self.xes_path = xes_path
        self.processed_dir = processed_dir
        self.outputs_dir = outputs_dir

        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.outputs_dir, exist_ok=True)

        self.events_df = None
        self.graph = None
        self.case_paths = None

    def run(self):
        logging.info("===== STEP 1: LOAD XES LOG =====")
        self.events_df = self.load_xes_as_dataframe()

        logging.info("===== STEP 2: PREPROCESS EVENTS =====")
        self.events_df = self.preprocess_events(self.events_df)
        self.events_df.to_csv(
            os.path.join(self.processed_dir, "events.csv"),
            index=False,
            encoding="utf-8-sig"
        )

        logging.info("===== STEP 3: BUILD CASE PATHS =====")
        self.case_paths = self.build_case_paths(self.events_df)

        logging.info("===== STEP 4: BUILD DIRECTLY-FOLLOWS GRAPH =====")
        self.graph = self.build_directly_follows_graph(self.case_paths)

        logging.info("===== STEP 5: EXPORT NODES AND EDGES =====")
        self.export_nodes_and_edges(self.graph)

        logging.info("===== STEP 6: COMPUTE BASIC GRAPH STATISTICS =====")
        basic_stats = self.compute_basic_statistics(self.graph, self.case_paths)

        logging.info("===== STEP 7: PATH ANALYSIS =====")
        path_df = self.compute_path_statistics(self.case_paths)
        path_df.to_csv(
            os.path.join(self.processed_dir, "path_statistics.csv"),
            index=False,
            encoding="utf-8-sig"
        )

        logging.info("===== STEP 8: CYCLE DETECTION =====")
        cycle_df = self.detect_cycles(self.graph)
        cycle_df.to_csv(
            os.path.join(self.processed_dir, "cycle_summary.csv"),
            index=False,
            encoding="utf-8-sig"
        )

        logging.info("===== STEP 9: CENTRALITY METRICS =====")
        centrality_df = self.compute_centrality_metrics(self.graph)
        centrality_df.to_csv(
            os.path.join(self.outputs_dir, "centrality.csv"),
            index=False,
            encoding="utf-8-sig"
        )

        logging.info("===== STEP 10: DRAW GRAPH =====")
        self.draw_graph(self.graph)

        logging.info("===== STEP 11: WRITE SUMMARY =====")
        self.write_summary(
            basic_stats=basic_stats,
            path_df=path_df,
            cycle_df=cycle_df,
            centrality_df=centrality_df
        )

        logging.info("Pipeline completed successfully.")

    def load_xes_as_dataframe(self) -> pd.DataFrame:
        """
        Load an XES file using PM4Py and convert it into a flat event dataframe.
        """
        log = xes_importer.apply(self.xes_path)

        rows = []
        for trace_idx, trace in enumerate(log):
            case_id = trace.attributes.get("concept:name", f"CASE_{trace_idx + 1}")

            for event in trace:
                activity = event.get("concept:name")
                timestamp = event.get("time:timestamp")
                resource = event.get("org:resource", None)
                lifecycle = event.get("lifecycle:transition", None)

                rows.append({
                    "case_id": str(case_id),
                    "activity": str(activity) if activity is not None else "UNKNOWN",
                    "timestamp": pd.to_datetime(timestamp, errors="coerce"),
                    "resource": resource,
                    "lifecycle": lifecycle
                })

        df = pd.DataFrame(rows)
        logging.info("Loaded %s events from XES", len(df))
        return df

    def preprocess_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Basic preprocessing:
        - drop missing activity/timestamp if any
        - sort by case_id and timestamp
        - keep only core columns for assignment
        """
        df = df.copy()

        df = df.dropna(subset=["case_id", "activity", "timestamp"])
        df["activity"] = df["activity"].astype(str).str.strip()
        df = df[df["activity"] != ""]
        df = df.sort_values(by=["case_id", "timestamp"]).reset_index(drop=True)

        logging.info("After preprocessing: %s events", len(df))
        logging.info("Unique cases: %s", df["case_id"].nunique())
        logging.info("Unique activities: %s", df["activity"].nunique())

        return df

    def build_case_paths(self, df: pd.DataFrame) -> dict:
        """
        Convert event table into ordered activity paths per case.
        """
        case_paths = {}
        grouped = df.groupby("case_id")

        for case_id, group in grouped:
            activities = group["activity"].tolist()
            if len(activities) > 0:
                case_paths[case_id] = activities

        logging.info("Built %s case paths", len(case_paths))
        return case_paths

    def build_directly_follows_graph(self, case_paths: dict) -> nx.DiGraph:
        """
        Build a directed weighted graph:
        - node: activity
        - edge: directly-follows relation
        - edge weight: frequency
        """
        graph = nx.DiGraph()

        for case_id, activities in case_paths.items():
            for i in range(len(activities)):
                activity = activities[i]
                if not graph.has_node(activity):
                    graph.add_node(activity)

            for i in range(len(activities) - 1):
                src = activities[i]
                dst = activities[i + 1]

                if graph.has_edge(src, dst):
                    graph[src][dst]["weight"] += 1
                else:
                    graph.add_edge(src, dst, weight=1)

        logging.info(
            "Graph created with %s nodes and %s edges",
            graph.number_of_nodes(),
            graph.number_of_edges()
        )
        return graph

    def export_nodes_and_edges(self, graph: nx.DiGraph):
        """
        Export nodes.csv and edges.csv.
        """
        node_list = sorted(list(graph.nodes()))
        node_id_map = {node: idx + 1 for idx, node in enumerate(node_list)}

        nodes_df = pd.DataFrame([
            {"node_id": node_id_map[node], "label": node}
            for node in node_list
        ])

        edges_df = pd.DataFrame([
            {
                "source_id": node_id_map[u],
                "source_label": u,
                "target_id": node_id_map[v],
                "target_label": v,
                "weight": data.get("weight", 1)
            }
            for u, v, data in graph.edges(data=True)
        ]).sort_values(by=["source_label", "target_label"]).reset_index(drop=True)

        nodes_df.to_csv(
            os.path.join(self.processed_dir, "nodes.csv"),
            index=False,
            encoding="utf-8-sig"
        )
        edges_df.to_csv(
            os.path.join(self.processed_dir, "edges.csv"),
            index=False,
            encoding="utf-8-sig"
        )

    def compute_basic_statistics(self, graph: nx.DiGraph, case_paths: dict) -> dict:
        """
        Compute graph-level summary metrics.
        """
        num_nodes = graph.number_of_nodes()
        num_edges = graph.number_of_edges()
        num_cases = len(case_paths)

        total_events = sum(len(path) for path in case_paths.values())
        avg_trace_length = total_events / num_cases if num_cases > 0 else 0

        in_degrees = dict(graph.in_degree())
        out_degrees = dict(graph.out_degree())

        start_nodes = [n for n in graph.nodes() if in_degrees.get(n, 0) == 0]
        end_nodes = [n for n in graph.nodes() if out_degrees.get(n, 0) == 0]

        density = nx.density(graph) if num_nodes > 1 else 0.0
        is_dag = nx.is_directed_acyclic_graph(graph)

        stats = {
            "num_cases": num_cases,
            "total_events": total_events,
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "avg_trace_length": avg_trace_length,
            "num_start_nodes": len(start_nodes),
            "num_end_nodes": len(end_nodes),
            "graph_density": density,
            "is_dag": is_dag,
            "start_nodes": start_nodes,
            "end_nodes": end_nodes
        }

        logging.info("Basic stats: %s", stats)
        return stats

    def compute_path_statistics(self, case_paths: dict) -> pd.DataFrame:
        """
        Count unique paths and their frequencies.
        """
        path_counter = Counter()

        for case_id, activities in case_paths.items():
            path_str = " -> ".join(activities)
            path_counter[path_str] += 1

        rows = []
        for idx, (path_str, freq) in enumerate(path_counter.most_common(), start=1):
            path_length = len(path_str.split(" -> "))
            rows.append({
                "path_rank": idx,
                "path": path_str,
                "frequency": freq,
                "path_length": path_length
            })

        return pd.DataFrame(rows)

    def detect_cycles(self, graph: nx.DiGraph) -> pd.DataFrame:
        """
        Detect simple cycles in the graph.
        """
        cycles = list(nx.simple_cycles(graph))

        rows = []
        for idx, cycle in enumerate(cycles, start=1):
            rows.append({
                "cycle_id": idx,
                "cycle_length": len(cycle),
                "cycle_path": " -> ".join(cycle) + " -> " + cycle[0]
            })

        if not rows:
            rows.append({
                "cycle_id": 0,
                "cycle_length": 0,
                "cycle_path": "NO_CYCLE_FOUND"
            })

        return pd.DataFrame(rows)

    def compute_centrality_metrics(self, graph: nx.DiGraph) -> pd.DataFrame:
        """
        Compute graph centrality metrics.
        """
        if graph.number_of_nodes() == 0:
            return pd.DataFrame(columns=[
                "activity",
                "in_degree",
                "out_degree",
                "degree_centrality",
                "betweenness_centrality",
                "closeness_centrality"
            ])

        degree_centrality = nx.degree_centrality(graph)
        betweenness_centrality = nx.betweenness_centrality(graph, normalized=True)
        closeness_centrality = nx.closeness_centrality(graph)

        rows = []
        for node in graph.nodes():
            rows.append({
                "activity": node,
                "in_degree": graph.in_degree(node),
                "out_degree": graph.out_degree(node),
                "degree_centrality": degree_centrality.get(node, 0.0),
                "betweenness_centrality": betweenness_centrality.get(node, 0.0),
                "closeness_centrality": closeness_centrality.get(node, 0.0)
            })

        df = pd.DataFrame(rows).sort_values(
            by=["betweenness_centrality", "degree_centrality"],
            ascending=False
        ).reset_index(drop=True)

        return df

    def draw_graph(self, graph: nx.DiGraph):
        """
        Draw a weighted process graph.
        """
        plt.figure(figsize=(18, 12))

        pos = nx.spring_layout(graph, seed=42, k=1.2)

        edge_weights = [graph[u][v]["weight"] for u, v in graph.edges()]
        max_weight = max(edge_weights) if edge_weights else 1
        edge_widths = [1 + (w / max_weight) * 4 for w in edge_weights]

        nx.draw_networkx_nodes(
            graph,
            pos,
            node_size=1800
        )
        nx.draw_networkx_labels(
            graph,
            pos,
            font_size=8
        )
        nx.draw_networkx_edges(
            graph,
            pos,
            width=edge_widths,
            arrows=True,
            arrowsize=20,
            connectionstyle="arc3,rad=0.08"
        )

        edge_labels = {
            (u, v): data["weight"]
            for u, v, data in graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(
            graph,
            pos,
            edge_labels=edge_labels,
            font_size=7
        )

        plt.title("BPIC 2011 - Directly-Follows Process Graph")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.outputs_dir, "process_graph.png"),
            dpi=300,
            bbox_inches="tight"
        )
        plt.close()

    def write_summary(
        self,
        basic_stats: dict,
        path_df: pd.DataFrame,
        cycle_df: pd.DataFrame,
        centrality_df: pd.DataFrame
    ):
        """
        Write a human-readable summary text file.
        """
        summary_path = os.path.join(self.processed_dir, "graph_summary.txt")

        top_paths = path_df.head(5)
        top_central = centrality_df.head(10)
        num_cycles = 0 if (
            len(cycle_df) == 1 and cycle_df.iloc[0]["cycle_id"] == 0
        ) else len(cycle_df)

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("BPIC 2011 GRAPH MINING SUMMARY\n")
            f.write("=" * 60 + "\n\n")

            f.write("1. BASIC STATISTICS\n")
            f.write(f"- Number of cases: {basic_stats['num_cases']}\n")
            f.write(f"- Total events: {basic_stats['total_events']}\n")
            f.write(f"- Number of nodes (activities): {basic_stats['num_nodes']}\n")
            f.write(f"- Number of edges (transitions): {basic_stats['num_edges']}\n")
            f.write(f"- Average trace length: {basic_stats['avg_trace_length']:.2f}\n")
            f.write(f"- Number of start nodes: {basic_stats['num_start_nodes']}\n")
            f.write(f"- Number of end nodes: {basic_stats['num_end_nodes']}\n")
            f.write(f"- Graph density: {basic_stats['graph_density']:.6f}\n")
            f.write(f"- Is DAG: {basic_stats['is_dag']}\n")
            f.write(f"- Start nodes: {basic_stats['start_nodes']}\n")
            f.write(f"- End nodes: {basic_stats['end_nodes']}\n\n")

            f.write("2. TOP 5 MOST FREQUENT PATHS\n")
            for _, row in top_paths.iterrows():
                f.write(
                    f"- Rank {row['path_rank']}: freq={row['frequency']}, "
                    f"length={row['path_length']}\n"
                )
                f.write(f"  {row['path']}\n")
            f.write("\n")

            f.write("3. CYCLE ANALYSIS\n")
            f.write(f"- Number of detected simple cycles: {num_cycles}\n")
            if num_cycles > 0:
                for _, row in cycle_df.head(10).iterrows():
                    f.write(
                        f"- Cycle {row['cycle_id']} (length={row['cycle_length']}): "
                        f"{row['cycle_path']}\n"
                    )
            f.write("\n")

            f.write("4. TOP 10 CENTRAL ACTIVITIES\n")
            for idx, row in top_central.iterrows():
                f.write(
                    f"- {row['activity']}: "
                    f"in={row['in_degree']}, "
                    f"out={row['out_degree']}, "
                    f"degree={row['degree_centrality']:.4f}, "
                    f"betweenness={row['betweenness_centrality']:.4f}, "
                    f"closeness={row['closeness_centrality']:.4f}\n"
                )

            f.write("\n5. INTERPRETATION HINTS\n")
            f.write("- High betweenness: candidate bottleneck activity.\n")
            f.write("- High frequency edges: dominant process transitions.\n")
            f.write("- Many cycles: possible rework, repeated checks, or looping.\n")
            f.write("- Many unique paths: process variability is high.\n")


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    xes_path = os.path.join(project_root, "data", "raw", "BPIC2011.xes")
    processed_dir = os.path.join(project_root, "data", "processed")
    outputs_dir = os.path.join(project_root, "outputs")

    if not os.path.exists(xes_path):
        raise FileNotFoundError(
            f"XES file not found: {xes_path}\n"
            f"Please place the BPIC 2011 XES file in data/raw/BPIC2011.xes"
        )

    pipeline = BPIC2011GraphMining(
        xes_path=xes_path,
        processed_dir=processed_dir,
        outputs_dir=outputs_dir
    )
    pipeline.run()


if __name__ == "__main__":
    main()