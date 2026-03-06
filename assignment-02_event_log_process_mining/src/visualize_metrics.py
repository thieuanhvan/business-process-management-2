import matplotlib.pyplot as plt


def draw_pagerank_chart(metrics_df, output_path):
    """
    Draw bar chart of PageRank scores for activities.
    """

    df = metrics_df.sort_values("pagerank", ascending=False)

    activities = df["activity"]
    scores = df["pagerank"]

    plt.figure(figsize=(8, 4))

    plt.bar(activities, scores)

    plt.title("Activity Importance (PageRank)")
    plt.xlabel("Activity")
    plt.ylabel("PageRank Score")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(output_path)

    plt.close()