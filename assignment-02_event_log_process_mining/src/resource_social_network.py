import pandas as pd
import networkx as nx


def build_handover_graph(
        df,
        resource_col="agent_name",
        case_col="case_id",
        time_col="timestamp",
        remove_self_loops=False,
        top_n=50,
        min_weight=1
):
    """
    Build Handover-of-Work social network.

    Parameters
    ----------
    df : pandas.DataFrame
        Event log
    resource_col : str
        Resource column
    case_col : str
        Case ID column
    time_col : str
        Timestamp column
    remove_self_loops : bool
        Remove A->A transitions
    top_n : int
        Keep top N transitions
    min_weight : int
        Minimum frequency

    Returns
    -------
    G : networkx.DiGraph
    transitions_df : DataFrame
    """

    work_df = df.copy()

    work_df[time_col] = pd.to_datetime(work_df[time_col], errors="coerce")
    work_df = work_df.dropna(subset=[case_col, time_col, resource_col])

    work_df = work_df.sort_values([case_col, time_col])

    transitions = []

    for _, group in work_df.groupby(case_col):

        resources = group[resource_col].astype(str).tolist()

        for i in range(len(resources) - 1):

            r1 = resources[i]
            r2 = resources[i + 1]

            if remove_self_loops and r1 == r2:
                continue

            transitions.append((r1, r2))

    if len(transitions) == 0:

        empty_df = pd.DataFrame(
            columns=["from_resource", "to_resource", "weight"]
        )

        return nx.DiGraph(), empty_df

    transitions_df = pd.DataFrame(
        transitions,
        columns=["from_resource", "to_resource"]
    )

    transitions_df = (
        transitions_df
        .value_counts()
        .reset_index(name="weight")
        .sort_values("weight", ascending=False)
    )

    transitions_df = transitions_df[
        transitions_df["weight"] >= min_weight
    ]

    if top_n is not None:
        transitions_df = transitions_df.head(top_n)

    G = nx.DiGraph()

    for _, row in transitions_df.iterrows():

        G.add_edge(
            row["from_resource"],
            row["to_resource"],
            weight=int(row["weight"])
        )

    return G, transitions_df