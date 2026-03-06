// Load relationships
LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row

MATCH (src:Node {id: row.source})
MATCH (dst:Node {id: row.target})

MERGE (src)-[:NEXT]->(dst);
