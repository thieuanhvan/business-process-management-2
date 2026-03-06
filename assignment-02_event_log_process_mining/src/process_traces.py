import pandas as pd


def compute_top_traces(df, case_col="case_id", activity_col="activity_name", time_col="timestamp", top_n=10):

    # Sắp xếp theo case và thời gian
    df_sorted = df.sort_values([case_col, time_col])

    # Ghép các activity thành một trace
    traces = (
        df_sorted
        .groupby(case_col)[activity_col]
        .apply(lambda x: " → ".join(x))
        .reset_index(name="trace")
    )

    # Đếm số lần xuất hiện của mỗi trace
    trace_freq = (
        traces["trace"]
        .value_counts()
        .reset_index()
    )

    trace_freq.columns = ["trace", "frequency"]

    return trace_freq.head(top_n)