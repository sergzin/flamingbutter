
## FlamingButter
This project visualise ISIS L2 topology using Neo4j database and help planning MPLS LSP bandwidth demands. 


### Installation requirements

Project should work fine on Linux and OSx with the following requirements.
- Neo4j server version 2.3.7 installed locally
    - disable authentication `dbms.security.auth_enabled=false` in configuration file `neo4j-server.properties`
- python 2.7
- python modules
    - lxml==3.6.0
    - py2neo==2.0.8
    - requests==2.9.1

On Windown use Vagrant + Virtualbox.
From the root of the project type `vagrant up`


### Files

`isisparser.py` - import ISIS topological data in Neo4j graph database
it require file with output from command `show isis database extensive | display xml`

`place_demands.py` - uses Neo4j API to calculate a path 
between Source and Destination ISIS Nodes and place bandwidth per path.

`get_demands.py` - (optional) download and save LSP demands from InfluxDB.

`resolve_demands.py` - (optional) helper script to convert CSV file with 
hostname,loopback IP,LSP bandwidth to a CSV file with Source,Destination,LSP bandwidth

`settings.py` - project settings in Python file

`spf.py` - implementation of REST API query to Neo4j DB.


### Neo4j Database schema

#### What is connected and how?
```
// What is related, and how
MATCH (a)-[r]->(b)
WHERE labels(a) <> [] AND labels(b) <> []
RETURN DISTINCT head(labels(a)) AS This, type(r) as To, head(labels(b)) AS That
LIMIT 10
```

|  This	|  To	| That
|-------|-------|------
|Router	|LINK	|Router
|Prefix	|ISIS	|Router

Relationship `LINK` and `ISIS` have property called `metric`.
`metric` represent ISIS cost.



### CypherQueries

The following two queries delete all information in neo4j database.
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