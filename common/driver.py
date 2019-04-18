#from neo4j.v1 import GraphDatabase
from common.Topology import Topology as Topology
from common.Node import Roadm as Roadm
from common.GraphVertex import GraphVertex as vertex
from common.Node import Degree as degree
from common.Node import Ila as ila
from common.CommonStrings import CommonStrings as Strings
from common.NodeEdgePoint import NodeEdgePoint as Nep
from common.Direction import Direction as Direction
from common.dbservices import DbService as db
from common.JsonTopology import JsonTopology as tapitopology

import json

from neo4j import GraphDatabase
from neo4j import exceptions as Neo4jException
try:
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "infinera"))
except BrokenPipeError as brokenpipe:
    print ('Broken pipe error')
    exit(1)
except ConnectionAbortedError as connAbort:
    print('connection aborted')
    exit(1)
except ConnectionRefusedError as refused:
    print("Connection refused")
    exit(1)
except ConnectionResetError as connRest:
    print("Connection refused as it got reset.")
    exit(1)
except Neo4jException.ServiceUnavailable as failed:
    print("Connection failed. Please check if neo4j server is up and running.")
    exit(1)
except Neo4jException.SecurityError as tlsfailed:
    print("Connection failed. Please check if neo4j server is up and running. Check if TLS auth is fine")
    exit(1)

db.installInstance()

def add_vertex(tx, vtx:vertex):
    q = " MERGE (a: " + vtx.type + " { uuid: $uuid, name:$name, type:$type })"
    tx.run(q,  uuid=vtx.uuid, name=vtx.name, type=vtx.type )

def add_edge(tx, label, srcvtx:vertex, dstvtx: vertex):
    a = "MATCH (src:" + srcvtx.type + "{ uuid: '" + srcvtx.uuid +"'   }) "
    b = "MATCH (dst:" + dstvtx.type + "{ uuid: '" + dstvtx.uuid + "'  }) "
    l = "CREATE (src)-[rel: " + label + "]->(dst)"
    tx.run (a + b + l)

def add_unique_edge( tx, label, srcvtx:vertex, dstvtx: vertex):
    a = "MATCH (src:" + srcvtx.type + "{ uuid: '" + srcvtx.uuid + "'   }) "
    b = "MATCH (dst:" + dstvtx.type + "{ uuid: '" + dstvtx.uuid + "'  }) "
    l = "MERGE (src)-[rel: " + label + "]->(dst)" + " return rel"
    tx.run(a + b + l)

def readfile(filename):
    f = open(filename, "r")
    return f.read()

def addfullnode(tx, node: Direction):

    pairs = []
    nepuuids = []
    for nep in node.neps:
        pairs.append(nep.properties)
        nepuuids.append( nep.uuid)

    insert_query = '''
    UNWIND {pairs} as map
    MERGE(n:nep {uuid: map["uuid"], link-port-direction: map["link-port-direction"]}) 
    ON CREATE SET n += map 
    '''
    tx.run(insert_query, parameters={"pairs": pairs})

    if node.type == 'degree':
        insert_query = '''
                UNWIND {nepuuids} as id
                MATCH(p: degree { uuid: {nodeuuid}})
                MATCH(q: nep { uuid: id })
                MERGE (p)-[rel:nep]->(q)
                '''
        tx.run("MERGE(n:degree {uuid: {nodeuuid}}) ON CREATE SET n += {prop}", parameters={"nodeuuid": node.uuid, "prop": node.properties})
        tx.run(insert_query, parameters={ "nodeuuid": node.uuid,"nepuuids": nepuuids})

    else:
        insert_query = '''
                UNWIND {nepuuids} as id
                MATCH(p: ila { uuid: {nodeuuid}})
                MATCH(q: nep { uuid: id })
                MERGE (p)-[rel:nep]->(q)
                '''
        tx.run("MERGE(n:ila {uuid: {nodeuuid}}) ON CREATE SET n += {prop}", parameters={"nodeuuid": node.uuid, "prop": node.properties})
        tx.run(insert_query, parameters={"nodeuuid": node.uuid, "nepuuids": nepuuids})


def doLink(tx, uuid):
    insert_query = '''                                                                       
    UNWIND {pairs} as pair                                                                   
    MERGE (p1:degree {uuid: {uuid}})                                                         
    MERGE (p2:nep    {name:pair, direction: "input"})                                        
    MERGE (p3:nep    {name:pair, direction: "output"})                                       
    MERGE (p1)-[:nep]-(p2)                                                                   
    MERGE (p1)-[:nep]-(p3);                                                                  
    '''
    data = [["node", "1-A-L1-1", "node", "1-A-T1-3"]
        , ["node", "1-A-T1-2", "node", ],[ "node","1-A-T1-4", "node","1-A-T1-5"]
        , ["node", "1-A-T1-6", "node", "1-A-T1-7"]]
    tx.run(insert_query, parameters={"uuid": uuid, "pairs": data})



roadm1 = Roadm ("roadm1")
roadm2 = Roadm ('roadm2')
oa1 = oa ('oa1')

NeList = []
a = Topology('SVL', '10.220.0.117')
b = Topology('UTAH', '192.168.1.1')
c = Topology('BLR', '12.12.12.12')


a.addnode (roadm1)
b.addnode (oa1)
c.addnode (roadm2)

NeList.append(a)
NeList.append(b)
NeList.append(c)

d1=degree('north')
d2=degree('west')
d3=degree('east')
ila1=ila('ila')

nepList1 = [Nep('1-A-1-L1', Strings.Y_TXDIRECTION), Nep('1-A-3', Strings.Y_TXDIRECTION), Nep('1-A-1', Strings.Y_TXDIRECTION), Nep('1-A-2', Strings.Y_TXDIRECTION),
            Nep('1-A-1-L1', Strings.Y_RXDIRECTION), Nep('1-A-3', Strings.Y_RXDIRECTION), Nep('1-A-1', Strings.Y_RXDIRECTION), Nep('1-A-2', Strings.Y_RXDIRECTION)]

nepList2 = [Nep('12-A-1-L1', Strings.Y_TXDIRECTION), Nep('12-A-3', Strings.Y_TXDIRECTION), Nep('12-A-1', Strings.Y_TXDIRECTION), Nep('12-A-2', Strings.Y_TXDIRECTION),
            Nep('12-A-1-L1', Strings.Y_RXDIRECTION), Nep('12-A-3', Strings.Y_RXDIRECTION), Nep('12-A-1', Strings.Y_RXDIRECTION), Nep('12-A-2', Strings.Y_RXDIRECTION)]

olaNep = [Nep('4-A-1-L1', Strings.Y_TXDIRECTION), Nep('4-A-2-L1', Strings.Y_TXDIRECTION),
          Nep('4-A-1-L1', Strings.Y_RXDIRECTION), Nep('4-A-2-L1', Strings.Y_RXDIRECTION)]

roadm1.adddegree(d1)
roadm1.adddegree(d2)
roadm2.adddegree(d3)
oa1.addila(ila1)

d1.neps = nepList1
d3.neps = nepList2
ila1.neps = olaNep


print(a.dump)
with driver.session() as session:
    session.write_transaction(add_vertex, a)
    session.write_transaction(add_vertex, b)
    session.write_transaction(add_vertex, c)

db.addVertex(roadm1)
db.addVertex(roadm2)
db.addVertex(oa1)

#    session.write_transaction(add_vertex, roadm1)
#    session.write_transaction(add_vertex, oa1)
#    session.write_transaction(add_vertex, roadm2)

with driver.session() as session:
    session.write_transaction(add_unique_edge, 'roadm', a, roadm1)
    session.write_transaction(add_unique_edge, 'oa', b, oa1)
    session.write_transaction(add_unique_edge, 'roadm', c, roadm2)



db.AddIlaNode(ila1)
db.AddDegreeNode(d1)
db.AddDegreeNode(d2)
db.AddDegreeNode(d3)

db.addEdge('degree', roadm1, d1)
db.addEdge('degree', roadm1, d2)
db.addEdge('degree', roadm2, d3)
db.addEdge('ila', oa1, ila1)

db.addTlsLink( nepList1[0], olaNep[0]);
db.addTlsLink( nepList2[0], olaNep[1]);

#with driver.session() as session:
 #   session.write_transaction(add_unique_edge, 'degree', roadm1, d1)
  #  session.write_transaction(add_unique_edge, 'degree', roadm1, d2)
   # session.write_transaction(add_unique_edge, 'degree', roadm2, d3)
    #session.write_transaction(add_unique_edge, 'ila', oa1, ila1)

    #session.write_transaction( doNepCreate,'east')
print("Testing Json Decode")
data = readfile("topo.json")
m = json.loads(data);
S= tapitopology.decodeme(m)
for node in S.nodeList:
    if node.type == Strings.VTYPE_ILA:
        db.AddIlaNode(node)
    else:
        db.AddDegreeNode(node)

print(S)

