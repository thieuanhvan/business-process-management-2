MATCH (bp:BusinessProcess)-[:HAS_NODE]->(n:Node)
WHERE n.code = 'TESTING'
RETURN bp.id, bp.name;


MATCH (bp:BusinessProcess {id:'BP2'})
MATCH (s:Node {code:'START'})<-[:HAS_NODE]-(bp)
MATCH (e:Node {code:'END'})<-[:HAS_NODE]-(bp)
MATCH p = (s)-[:NEXT*]->(e)
RETURN [n IN nodes(p) | n.name] AS path;


MATCH (bp:BusinessProcess {id:'BP2'})-[:HAS_NODE]->(n)
OPTIONAL MATCH (n)-[r:NEXT]->(m)
RETURN bp, n, r, m;
