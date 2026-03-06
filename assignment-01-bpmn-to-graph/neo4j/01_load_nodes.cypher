// Load BusinessProcess + Node
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row

WITH row
WHERE row.id IS NOT NULL

FOREACH (_ IN CASE WHEN row.type = 'BusinessProcess' THEN [1] ELSE [] END |
  MERGE (bp:BusinessProcess {id: row.id})
  SET bp.name = row.name
)

FOREACH (_ IN CASE WHEN row.type = 'Node' THEN [1] ELSE [] END |
  MERGE (n:Node {id: row.id})
  SET
    n.code = row.code,
    n.name = row.name,
    n.nodeType = row.nodeType,
    n.bp_id = row.bp_id
);
