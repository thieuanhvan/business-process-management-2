// Connect BusinessProcess to its nodes
MATCH (bp:BusinessProcess)
MATCH (n:Node)
WHERE n.bp_id = bp.id
MERGE (bp)-[:HAS_NODE]->(n);
