import pandas as pd
import networkx as nx
from pyvis.network import Network
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer


# ===============================
# STEP 1: CREATE AND SAVE SAMPLE EVENT LOG
# ===============================

def create_and_save_event_log(csv_path="eventlog.csv"):
    """
    Create a sample event log for a patient examination process.

    Process structure:
    Start -> Registration -> XOR ->
        (General Examination OR Laboratory Test) ->
        Diagnosis & Prescription -> End
    """

    data = [
        # Case 1: Registration -> General Examination -> Diagnosis & Prescription
        {"case_id": "1", "activity": "Registration", "timestamp": "2024-01-01 08:00:00"},
        {"case_id": "1", "activity": "General Examination", "timestamp": "2024-01-01 08:20:00"},
        {"case_id": "1", "activity": "Diagnosis & Prescription", "timestamp": "2024-01-01 08:45:00"},

        # Case 2: Registration -> Laboratory Test -> Diagnosis & Prescription
        {"case_id": "2", "activity": "Registration", "timestamp": "2024-01-01 09:00:00"},
        {"case_id": "2", "activity": "Laboratory Test", "timestamp": "2024-01-01 09:30:00"},
        {"case_id": "2", "activity": "Diagnosis & Prescription", "timestamp": "2024-01-01 10:10:00"},

        # Case 3: Registration -> General Examination -> Diagnosis & Prescription
        {"case_id": "3", "activity": "Registration", "timestamp": "2024-01-01 10:00:00"},
        {"case_id": "3", "activity": "General Examination", "timestamp": "2024-01-01 10:20:00"},
        {"case_id": "3", "activity": "Diagnosis & Prescription", "timestamp": "2024-01-01 10:50:00"},

        # Case 4: Registration -> Laboratory Test -> Diagnosis & Prescription
        {"case_id": "4", "activity": "Registration", "timestamp": "2024-01-01 11:00:00"},
        {"case_id": "4", "activity": "Laboratory Test", "timestamp": "2024-01-01 11:25:00"},
        {"case_id": "4", "activity": "Diagnosis & Prescription", "timestamp": "2024-01-01 12:00:00"},

        # Case 5: Registration -> General Examination -> Diagnosis & Prescription
        {"case_id": "5", "activity": "Registration", "timestamp": "2024-01-01 13:00:00"},
        {"case_id": "5", "activity": "General Examination", "timestamp": "2024-01-01 13:15:00"},
        {"case_id": "5", "activity": "Diagnosis & Prescription", "timestamp": "2024-01-01 13:40:00"},
    ]

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df.to_csv(csv_path, index=False)

    print(f"Saved sample event log to: {csv_path}")
    print(df)

    return df


# ===============================
# STEP 2: RUN ALPHA MINER
# ===============================

def run_alpha_miner(df, output_png="alpha_result.png"):
    """
    Run Alpha Miner from a pandas DataFrame.
    """

    df_pm = df.rename(columns={
        "case_id": "case:concept:name",
        "activity": "concept:name",
        "timestamp": "time:timestamp"
    })

    log = log_converter.apply(df_pm)

    net, initial_marking, final_marking = alpha_miner.apply(log)

    print("\n===== ALPHA MINER RESULT =====")
    print("Places:")
    for place in net.places:
        print("  ", place)

    print("\nTransitions:")
    for transition in net.transitions:
        print("  ", transition)

    print("\nInitial marking:", initial_marking)
    print("Final marking:", final_marking)

    try:
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        pn_visualizer.save(gviz, output_png)
        print(f"\nSaved discovered Petri net image to: {output_png}")
    except Exception as e:
        print("\nGraphviz is not available, so PNG export failed.")
        print("Fallback to interactive HTML visualization.")
        print("Error:", e)
        draw_html_graph(df)


# ===============================
# STEP 3: DRAW HTML GRAPH AS FALLBACK
# ===============================

def draw_html_graph(df, output_html="alpha_result.html"):
    """
    Draw a simple interactive process graph from event log
    when Graphviz is not available.
    """

    graph = nx.DiGraph()

    for case_id in df["case_id"].unique():
        case_df = df[df["case_id"] == case_id].sort_values("timestamp")
        activities = case_df["activity"].tolist()

        for i in range(len(activities) - 1):
            source = activities[i]
            target = activities[i + 1]

            if graph.has_edge(source, target):
                graph[source][target]["weight"] += 1
            else:
                graph.add_edge(source, target, weight=1)

    net = Network(height="650px", width="100%", directed=True, notebook=False)

    net.set_options("""
    {
      "physics": {
        "enabled": false
      },
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "LR",
          "sortMethod": "directed"
        }
      },
      "edges": {
        "smooth": {
          "enabled": true,
          "type": "cubicBezier"
        },
        "arrows": {
          "to": {
            "enabled": true
          }
        }
      }
    }
    """)

    for node in graph.nodes():
        if node == "Registration":
            color = "#87CEFA"
        elif node == "General Examination":
            color = "#90EE90"
        elif node == "Laboratory Test":
            color = "#FFD700"
        elif node == "Diagnosis & Prescription":
            color = "#FFA07A"
        else:
            color = "#D3D3D3"

        net.add_node(
            node,
            label=node,
            shape="box",
            color=color,
            font={"size": 18}
        )

    for source, target, data in graph.edges(data=True):
        net.add_edge(
            source,
            target,
            label=str(data["weight"]),
            title=f"Frequency: {data['weight']}"
        )

    net.write_html(output_html)
    print(f"Saved HTML process graph to: {output_html}")


# ===============================
# MAIN
# ===============================

if __name__ == "__main__":
    df_event_log = create_and_save_event_log("eventlog.csv")
    run_alpha_miner(df_event_log, "alpha_result.png")