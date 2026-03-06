// ==================================================
// ASSIGNMENT 01 – BPMN TO GRAPH (FINAL SCRIPT)
// University of Information Technology (UIT)
// ==================================================
//
// This script performs:
// 1. Reset database
// 2. Load BPMN nodes from CSV
// 3. Infer BusinessProcess from bp_id
// 4. Create HAS_NODE and NEXT relationships
// 5. Execute required queries for Assignment 01
//
// IMPORTANT:
// - nodes.csv and edges.csv MUST be located in Neo4j import directory
// ==================================================



/////////////////////////////////////////////////////
// 0. RESET DATABASE
/////////////////////////////////////////////////////

MATCH (n)
DETACH DELETE n;



/////////////////////////////////////////////////////
// 1. LOAD BPMN NODES (Start / Task / End)
/////////////////////////////////////////////////////

LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
MERGE (n:Node {id: row.id})
SET
  n.code  = row.code,
  n.name  = row.name,
  n.type  = row.type,
  n.bp_id = row.bp_id;



/////////////////////////////////////////////////////
// 2. INFER BUSINESS PROCESS FROM bp_id
/////////////////////////////////////////////////////

MATCH (n:Node)
WITH DISTINCT n.bp_id AS bpId
MERGE (bp:BusinessProcess {id: bpId})
SET bp.name = bpId;



/////////////////////////////////////////////////////
// 3. LINK NODE TO BUSINESS PROCESS
/////////////////////////////////////////////////////

MATCH (n:Node)
MATCH (bp:BusinessProcess {id: n.bp_id})
MERGE (bp)-[:HAS_NODE]->(n);



/////////////////////////////////////////////////////
// 4. LOAD SEQUENCE FLOWS (NEXT RELATIONSHIP)
/////////////////////////////////////////////////////

LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (src:Node {id: row.source})
MATCH (dst:Node {id: row.target})
MERGE (src)-[:NEXT]->(dst);



/////////////////////////////////////////////////////
// 5. QUERY 1
// Which Business Process contains a given Task?
/////////////////////////////////////////////////////

// Example: find Business Processes containing task "TESTING"
MATCH (bp:BusinessProcess)-[:HAS_NODE]->(n:Node)
WHERE n.code = 'TESTING'
RETURN bp.id AS BP_ID, bp.name AS BusinessProcess;



/////////////////////////////////////////////////////
// 6. QUERY 2
// Find all paths from Start to End of a BPMN
/////////////////////////////////////////////////////

// Example: BP2 – Software Development Process
MATCH (bp:BusinessProcess {id: 'BP2'})
MATCH (start:Node {code: 'START'})<-[:HAS_NODE]-(bp)
MATCH (end:Node {code: 'END'})<-[:HAS_NODE]-(bp)
MATCH p = (start)-[:NEXT*]->(end)
RETURN
  bp.name AS BusinessProcess,
  [n IN nodes(p) | n.name] AS ExecutionPath;



/////////////////////////////////////////////////////
// 7. QUERY 3
// Visualize Graph of a Specific BPMN
/////////////////////////////////////////////////////

// Example: visualize BP2
MATCH (bp:BusinessProcess {id: 'BP2'})-[:HAS_NODE]->(n)
OPTIONAL MATCH (n)-[r:NEXT]->(m)
RETURN bp, n, r, m;



/////////////////////////////////////////////////////
// 8. FINAL CHECK (OPTIONAL)
/////////////////////////////////////////////////////

// MATCH (bp:BusinessProcess) RETURN count(bp);
// MATCH (n:Node) RETURN count(n);
// MATCH ()-[r:HAS_NODE]->() RETURN count(r);
// MATCH ()-[r:NEXT]->() RETURN count(r);
