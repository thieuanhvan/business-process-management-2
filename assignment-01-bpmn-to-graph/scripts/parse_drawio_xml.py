from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import csv
import re
from html import unescape

# =====================================================
# CONFIG
# =====================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DRAWIO_XML = DATA_DIR / "business-processes.drawio.xml"
NODES_CSV = DATA_DIR / "nodes.csv"
EDGES_CSV = DATA_DIR / "edges.csv"

# CHANGE THIS TO YOUR NEO4J IMPORT DIR
NEO4J_IMPORT_DIR = Path(
    r"C:\Users\Win\.Neo4jDesktop2\Data\dbmss\dbms-da65e4f1-1060-484b-a197-f053ff3094e7\import"
)

# =====================================================
# HELPERS
# =====================================================
def clean_label(value: str) -> str:
    """
    Remove HTML tags and decode HTML entities from draw.io labels
    """
    if not value:
        return ""
    text = re.sub("<[^<]+?>", " ", value)
    text = unescape(text)
    return " ".join(text.split())

def normalize_code(text: str) -> str:
    return text.upper().replace(" ", "_")

# =====================================================
# MAIN
# =====================================================
print(f"XML FILE: {DRAWIO_XML}")
print(f"Exists: {DRAWIO_XML.exists()}")

tree = ET.parse(DRAWIO_XML)
root = tree.getroot()

all_nodes = []
all_edges = []

bp_summary = {}

for diagram in root.findall(".//diagram"):
    bp_name = diagram.get("name", "").strip()
    if not bp_name.startswith("BP"):
        print(f"\n⚠️  SKIP PAGE: {bp_name}")
        continue

    bp_id = bp_name.split("-")[0].strip()

    print("\n" + "=" * 50)
    print(f"PAGE: {bp_name}")

    mxroot = diagram.find(".//mxGraphModel/root")
    if mxroot is None:
        print("⚠️  No mxGraphModel found")
        continue

    cells = mxroot.findall("mxCell")

    nodes = {}
    edges = []

    # -------------------------------------------------
    # PASS 1: COLLECT NODES
    # -------------------------------------------------
    for cell in cells:
        if cell.get("vertex") == "1":
            cell_id = cell.get("id")
            raw_value = cell.get("value") or ""
            label = clean_label(raw_value)

            node = {
                "id": f"{bp_id}_{cell_id}",
                "bp_id": bp_id,
                "bp_name": bp_name,
                "name": label,
                "code": normalize_code(label) if label else f"NODE_{cell_id}",
                "type": "Task"  # classify later
            }

            nodes[cell_id] = node
            all_nodes.append(node)

    # -------------------------------------------------
    # PASS 2: COLLECT EDGES
    # -------------------------------------------------
    incoming = {k: 0 for k in nodes}
    outgoing = {k: 0 for k in nodes}

    for cell in cells:
        if cell.get("edge") == "1":
            src = cell.get("source")
            tgt = cell.get("target")

            if src in nodes and tgt in nodes:
                edge = {
                    "source": nodes[src]["id"],
                    "target": nodes[tgt]["id"]
                }
                edges.append(edge)
                all_edges.append(edge)

                outgoing[src] += 1
                incoming[tgt] += 1

    # -------------------------------------------------
    # CLASSIFY START / END
    # -------------------------------------------------
    for cid, node in nodes.items():
        if incoming[cid] == 0:
            node["type"] = "Start"
            node["code"] = "START"
            node["name"] = "Start"
        elif outgoing[cid] == 0:
            node["type"] = "End"
            node["code"] = "END"
            node["name"] = "End"

    # -------------------------------------------------
    # DEBUG OUTPUT
    # -------------------------------------------------
    print(f"Vertex count: {len(nodes)}")
    print(f"Edge count  : {len(edges)}")

    print("\n--- NODES ---")
    for n in nodes.values():
        print(
            f"[{n['type']}] id={n['id']} | code={n['code']} | name='{n['name']}'"
        )

    print("\n--- EDGES ---")
    for e in edges:
        print(f"{e['source']} -> {e['target']}")

    bp_summary[bp_id] = {
        "nodes": len(nodes),
        "edges": len(edges)
    }

# =====================================================
# WRITE CSV FILES
# =====================================================
with open(NODES_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["id", "bp_id", "bp_name", "name", "code", "type"]
    )
    writer.writeheader()
    writer.writerows(all_nodes)

with open(EDGES_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["source", "target"]
    )
    writer.writeheader()
    writer.writerows(all_edges)

# =====================================================
# COPY TO NEO4J IMPORT DIRECTORY
# =====================================================
shutil.copy(NODES_CSV, NEO4J_IMPORT_DIR / NODES_CSV.name)
shutil.copy(EDGES_CSV, NEO4J_IMPORT_DIR / EDGES_CSV.name)

# =====================================================
# SUMMARY
# =====================================================
print("\n" + "=" * 50)
print("SUMMARY")
total_nodes = 0
total_edges = 0

for bp, info in bp_summary.items():
    print(f"{bp}: {info['nodes']} nodes, {info['edges']} edges")
    total_nodes += info["nodes"]
    total_edges += info["edges"]

print("-" * 50)
print(f"TOTAL NODES: {total_nodes}")
print(f"TOTAL EDGES: {total_edges}")
print("=" * 50)

print("✔ nodes.csv & edges.csv generated")
print("✔ copied to Neo4j import directory")
