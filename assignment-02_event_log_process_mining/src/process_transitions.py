import pandas as pd


def export_transitions(G, output_path):

    rows = []

    for u, v, data in G.edges(data=True):

        rows.append({
            "source": u,
            "target": v,
            "frequency": data["weight"]
        })

    df = pd.DataFrame(rows)

    df = df.sort_values("frequency", ascending=False)

    df.to_csv(output_path, index=False)

    return df