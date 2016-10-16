
## FlamingButter

### Installation requirements

- Neo4j server installed locally
    - disable authentication `dbms.security.auth_enabled=false` in configuration file `neo4j-server.properties`
- python 2.7
- python modules
    - lxml==3.6.0
    - py2neo==2.0.8
    - requests==2.9.1

### Files

`isisparser.py` - import ISIS topological data in Neo4j graph database
    it require file with output from command `show isis database detail | display xml`

### CypherQueries

delete connected nodes and links - `match (n)-[r]-() delete n,r`
delete not connected nodes - `match (n) delete n`

list of subnets connected to more that 2 routers (not p2p)
`match (a:Prefix)-[r]->(:Router) with a, count(*) as n where n > 2 match (a)-->(z:Router) return a,z`

Smimilar as previous query - find all ISIS DIS nodes (LAN segmens)
`match (a:Router)-[r]->(z:Router)  where NOT (a.name =~ '.+.00$') return a,r,z`

Example Dijkstra ECMP query
```
match (a:Router{name:'at-vie05b-ri2-re0.00'}), (z:Router{name:'HU-MON-MONR-RA2.00'}), 
p = allshortestPaths((a)-[r:LINK*]->(z))  
WITH reduce(cost = 0, rel in rels(p) | cost + rel.metric) as sumcost, p
return sumcost,extract(n IN nodes(p)| n.name)
```