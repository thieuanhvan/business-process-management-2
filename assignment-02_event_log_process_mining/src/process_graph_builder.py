import pandas as pd
import networkx as nx


def build_process_graph(df):
    """
    Build process graph from event log.
    """

    data = df.copy()

    data = data.sort_values(["case_id", "timestamp"])

    # next activity
    data["next_activity"] = (
        data.groupby("case_id")["activity_name"]
        .shift(-1)
    )

    transitions = (
        data.groupby(["activity_name", "next_activity"])
        .size()
        .reset_index(name="frequency")
    )

    transitions = transitions.dropna()

    # build graph
    G = nx.DiGraph()

    for _, row in transitions.iterrows():

        G.add_edge(
            row["activity_name"],
            row["next_activity"],
            weight=row["frequency"]
        )

    return G, transitions