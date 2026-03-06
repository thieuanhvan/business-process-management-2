import logging
from pathlib import Path

from src.event_log_reader import load_event_log
from src.process_graph_builder import build_process_graph
from src.process_metrics import compute_process_metrics
from src.process_traces import compute_top_traces
from src.resource_social_network import build_handover_graph
from src.visualization import draw_process_graph, draw_handover_graph
from src.time_analysis import (
    compute_case_duration,
    compute_waiting_time,
    detect_bottlenecks
)

# =========================================================
# LOGGING CONFIGURATION
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# =========================================================
# MAIN FUNCTION
# =========================================================

def main():

    logger.info("Starting Assignment 02 - Event Log Process Mining")

    project_root = Path(__file__).resolve().parent

    data_file = project_root / "data" / "insurance_claims_event_log.csv"

    output_dir = project_root / "outputs" / "run"
    output_dir.mkdir(parents=True, exist_ok=True)

    # =====================================================
    # LOAD EVENT LOG
    # =====================================================

    logger.info("Loading event log...")

    df = load_event_log(data_file)

    logger.info(f"Dataset loaded: {df.shape}")

    # =====================================================
    # BUILD PROCESS GRAPH
    # =====================================================

    logger.info("Building process graph...")

    process_graph, transitions_df = build_process_graph(df)

    transitions_path = output_dir / "process_transitions.csv"

    transitions_df.to_csv(
        transitions_path,
        index=False
    )

    logger.info(f"Transitions saved: {transitions_path}")

    logger.info(f"Process graph nodes: {process_graph.number_of_nodes()}")
    logger.info(f"Process graph edges: {process_graph.number_of_edges()}")

    # =====================================================
    # PROCESS METRICS
    # =====================================================

    logger.info("Computing process metrics...")

    metrics_df = compute_process_metrics(process_graph)

    metrics_path = output_dir / "process_metrics.csv"

    metrics_df.to_csv(
        metrics_path,
        index=False
    )

    logger.info(f"Metrics saved: {metrics_path}")

    # =====================================================
    # PROCESS TRACES
    # =====================================================

    logger.info("Computing top process traces...")

    traces_df = compute_top_traces(df)

    traces_path = output_dir / "top_traces.csv"

    traces_df.to_csv(
        traces_path,
        index=False
    )

    logger.info(f"Top traces saved: {traces_path}")

    if len(traces_df) > 0:

        logger.info(f"Most common trace: {traces_df.iloc[0]['trace']}")
        logger.info(f"Trace frequency: {traces_df.iloc[0]['frequency']}")

    # =====================================================
    # DRAW PROCESS GRAPH
    # =====================================================

    logger.info("Drawing process graph...")

    draw_process_graph(
        process_graph,
        output_dir
    )

    logger.info("Process graph saved")

    # =====================================================
    # TIME ANALYSIS
    # =====================================================

    logger.info("Computing case duration...")

    case_duration_df = compute_case_duration(df)

    case_duration_path = output_dir / "case_duration.csv"

    case_duration_df.to_csv(
        case_duration_path,
        index=False
    )

    logger.info(f"Case duration saved: {case_duration_path}")

    # -----------------------------------------------------

    logger.info("Computing waiting time between activities...")

    waiting_df = compute_waiting_time(df)

    waiting_path = output_dir / "activity_waiting_time.csv"

    waiting_df.to_csv(
        waiting_path,
        index=False
    )

    logger.info(f"Waiting time saved: {waiting_path}")

    # -----------------------------------------------------

    logger.info("Detecting bottlenecks...")

    bottlenecks_df = detect_bottlenecks(waiting_df)

    bottleneck_path = output_dir / "bottlenecks.csv"

    bottlenecks_df.to_csv(
        bottleneck_path,
        index=False
    )

    logger.info(f"Bottlenecks saved: {bottleneck_path}")

    # =====================================================
    # SOCIAL NETWORK MINING
    # =====================================================

    logger.info("Building handover social network...")

    resource_graph, resource_transitions = build_handover_graph(

        df=df,

        resource_col="agent_name",
        case_col="case_id",
        time_col="timestamp",

        # Important: allow self handover
        remove_self_loops=False,

        # keep strongest edges
        top_n=50,

        # keep all weights
        min_weight=1
    )

    resource_transitions_path = output_dir / "resource_transitions.csv"

    resource_transitions.to_csv(
        resource_transitions_path,
        index=False
    )

    logger.info(f"Resource transitions saved: {resource_transitions_path}")

    logger.info(f"Handover graph nodes: {resource_graph.number_of_nodes()}")
    logger.info(f"Handover graph edges: {resource_graph.number_of_edges()}")

    # -----------------------------------------------------

    logger.info("Drawing handover graph...")

    draw_handover_graph(
        resource_graph,
        output_dir
    )

    logger.info("Handover graph saved")

    # =====================================================

    logger.info("Assignment 02 finished successfully")


# =========================================================

if __name__ == "__main__":
    main()