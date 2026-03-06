import pandas as pd


def compute_case_duration(df):
    """
    Compute processing time of each case
    """

    data = df.copy()

    data["timestamp"] = pd.to_datetime(data["timestamp"])

    case_duration = (
        data.groupby("case_id")["timestamp"]
        .agg(["min", "max"])
        .reset_index()
    )

    case_duration["duration_hours"] = (
        (case_duration["max"] - case_duration["min"])
        .dt.total_seconds() / 3600
    )

    return case_duration


def compute_waiting_time(df):
    """
    Compute waiting time between consecutive activities
    """

    data = df.copy()

    data["timestamp"] = pd.to_datetime(data["timestamp"])

    data = data.sort_values(["case_id", "timestamp"])

    data["next_activity"] = data.groupby("case_id")["activity_name"].shift(-1)

    data["next_time"] = data.groupby("case_id")["timestamp"].shift(-1)

    data["waiting_hours"] = (
        (data["next_time"] - data["timestamp"])
        .dt.total_seconds() / 3600
    )

    waiting_df = (
        data.groupby(["activity_name", "next_activity"])["waiting_hours"]
        .mean()
        .reset_index()
    )

    waiting_df = waiting_df.dropna()

    return waiting_df


def detect_bottlenecks(waiting_df):
    """
    Detect bottlenecks based on largest waiting time
    """

    bottlenecks = waiting_df.sort_values(
        "waiting_hours",
        ascending=False
    )

    return bottlenecks