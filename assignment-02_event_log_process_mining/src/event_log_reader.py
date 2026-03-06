import pandas as pd


def load_event_log(path):

    df = pd.read_csv(path)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values(["case_id", "timestamp"])

    return df