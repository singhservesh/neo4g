from neo4j import GraphDatabase

from common.Node import Roadm as Roadm
from common.Topology import Topology as Topology
from common.GraphVertex import GraphVertex as Vertex
from common.Node import Degree as degree
from common.Node import Ila as Ila
from common.tls import TLS as TLS
from common.CommonStrings import CommonStrings as Strings
from common.NodeEdgePoint import NodeEdgePoint as Nep
from common.Node import Node as node
from neo4j import exceptions as neo4jexceptions
from common.pcsmInfo import PcsmState as PcsmState
from common.pcsmInfo import GPcsmInfo as GPcsmInfo
from common.tlsstate import TlsState as TlsState
from common.pcsmInfo import PcsmInfo as Pcsm

class DbService:

    _dbdriver = None
    _RetryTimeOut = 3 #seconds
    _RetryCount   = 10  #times.
    #TODO, add RLock.
    #dbService.__dbdriver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "infinera"))

    @staticmethod
    def createVertex ( vtex: Vertex, extra=""):
        return "MERGE(n:" + vtex.type + '{ uuid: "' + vtex.uuid + '"' + extra + ' }) ON CREATE SET n += {p}'

    @staticmethod
    def resolve(address):
        host, port = address
        if host == "192.168.56.102":
            yield "192.168.56.102", port
            yield "192.168.56.102", port+1
            yield "192.168.56.101", port
            yield "192.168.56.101", port+1
        else:
            yield host, port

    @staticmethod
    #def installInstance (bolturl="bolt://192.168.56.101:7687", username="neo4j", password="infinera"):
    def installInstance(bolturl="bolt+routing://192.168.56.101:7687", username="neo4j", password="infinera"):
    #def installInstance (bolturl="bolt://192.168.56.101:7687", username="neo4j", password="infinera"):
        if len(bolturl) < 1:
            raise Exception ("DB URL cannot be empty.")
        if len(username) < 1:
            raise Exception ("DB User name cannot be empty.")
        if len(password) < 1:
            raise Exception ("DB User password cannot be enmpy.")

        if DbService._dbdriver is None:
            try:
                #dbService._dbdriver = GraphDatabase.driver(bolturl, auth=(username, password), resolver=dbService.resolve)
                DbService._dbdriver = GraphDatabase.driver(bolturl, auth=(username, password))

            except BrokenPipeError as brokenpipe:
                print('Broken pipe error: ' + str(brokenpipe))
                exit(1)
            except ConnectionAbortedError as connAbort:
                print('connection aborted: ' + str(connAbort))
                exit(1)
            except ConnectionRefusedError as refused:
                print("Connection refused: " + str(refused))
                exit(1)
            except ConnectionResetError as connRest:
                print("Connection refused as it got reset: " + str( connRest))
                exit(1)
            except neo4jexceptions.ServiceUnavailable as failed:
                print("Connection failed. Please check if neo4j server is up and running: " + str(failed))
                exit(1)
            except neo4jexceptions.SecurityError as tlsfailed:
                print(""
                      "Connection failed. Please check if user credentials/TLS are fine. " + str(tlsfailed))
                exit(1)
            else:
                print ("Connection Created")
            finally:
                print ("Connection")

    @staticmethod
    def getInstance():
        if DbService._dbdriver == None:
            raise Exception ("DB service is not installed. Use installInstance to initialized db")
        return DbService._dbdriver

    @staticmethod
    def uninstallInstance():
        if DbService._dbdriver is not None:
            DbService._dbdriver.close()
        DbService._dbdriver = None

    def __init__(self):
        if DbService._dbdriver is None:
            raise Exception("DB service is not installed. Use installInstance to initialized db")

    @staticmethod
    def AddRoadm(node):
        print ("add vertex")


    @staticmethod
    def addVertex (tx, vtx: Vertex, extraProperty="" ):
        query = "MERGE (a: " + vtx.type + " { uuid: '" + vtx.uuid + "', name: '" + vtx.name +"'}) ON CREATE set a={prop}"
        tx.run(query,  parameters={"prop": vtx.properties})

    @staticmethod
    def AddIlaNode(node: node, tx):

        pairs = []
        nepuuids = []
        for nep in node.neps:
            pairs.append(nep.properties)
            if Strings.G_PORT_DIRECTION not in nep.properties:
                print(nep.properties)
            nepuuids.append(nep.uuid)

        insert_nep_query = "UNWIND {pairs} as map " \
                           + 'MERGE(n:nep {uuid: map["uuid"], ' \
                           + Strings.G_PORT_DIRECTION + ': map["'  + Strings.G_PORT_DIRECTION +'"]})'\
                           + 'ON CREATE SET n += map'


        insert_relation_query = '''
                UNWIND {nepuuids} as id
                MATCH(p: ila { uuid: {nodeuuid}})
                MATCH(q: nep { uuid: id })
                MERGE (p)-[rel:nep]->(q)
                '''
        insert_ila_query = "MERGE(n:ila {uuid: {nodeuuid}}) ON CREATE SET n += {prop}"

        tx.run(insert_nep_query, parameters={"pairs": pairs})
        tx.run(insert_ila_query, parameters={"nodeuuid": node.uuid, "prop": node.properties})
        tx.run(insert_relation_query, parameters={"nodeuuid": node.uuid, "nepuuids": nepuuids})
        return tx

    @staticmethod
    def AddDegreeNode(node: node, tx):

        pairs = []
        nepuuids = []
        for nep in node.neps:
            pairs.append(nep.properties)
            if Strings.G_PORT_DIRECTION not in nep.properties:
                #print( nep.properties)
                pass
            nepuuids.append(nep.uuid)

        insert_nep_query = "UNWIND {pairs} as map " \
                           + 'MERGE(n:nep {uuid: map["uuid"], ' \
                           + Strings.G_PORT_DIRECTION + ': map["'  + Strings.G_PORT_DIRECTION +'"]})'\
                           + 'ON CREATE SET n += map'

        insert_relation_query = '''
                UNWIND {nepuuids} as id
                MATCH(p: degree { uuid: {nodeuuid}})
                MATCH(q: nep { uuid: id })
                MERGE (p)-[rel:nep]->(q)
                '''
        insert_degree_query = "MERGE(n:degree {uuid: {nodeuuid}}) ON CREATE SET n += {prop}"

        #print(insert_nep_query + "\n" + insert_degree_query + "\n" + insert_relation_query)

        tx.run(insert_nep_query, parameters={"pairs": pairs})
        tx.run(insert_degree_query, parameters={"nodeuuid": node.uuid, "prop": node.properties})
        tx.run(insert_relation_query, parameters={"nodeuuid": node.uuid, "nepuuids": nepuuids})

        return tx


    @staticmethod
    def addEdge(tx, label, srcvtx: Vertex, dstvtx: Vertex):
        a = "MATCH (src:" + srcvtx.type + "{ uuid: '" + srcvtx.uuid + "'   }) "
        b = "MATCH (dst:" + dstvtx.type + "{ uuid: '" + dstvtx.uuid + "'  }) "
        l = "MERGE (src)-[rel: " + label + "]->(dst)" + " return rel"
        query = a + b + l
        tx.run(query)

    @staticmethod
    def createEdge(tx, label, srcvtx: Vertex, dstvtxtype: str, dstvtxuuid):
        a = "MATCH (src:" + srcvtx.type + "{ uuid: '" + srcvtx.uuid + "'   }) "
        b = "MATCH (dst:" + dstvtxtype + "{ uuid: '" + dstvtxuuid + "'  }) "
        l = "MERGE (src)-[rel: " + label + "]->(dst)" + " return rel"
        query = a + b + l
        tx.run(query)

    @staticmethod
    def addTlsLink( srcnep: Nep, dstnep: Nep):
        a1 = "MATCH (src1: nep { name: '" + srcnep.name + "', link-port-direction: '" + Strings.Y_TXDIRECTION + "'}) "
        b1 = "MATCH (dst1: nep { name: '" + dstnep.name + "', link-port-direction: '" + Strings.Y_RXDIRECTION + "'}) "
        a2 = "MATCH (src2: nep { name: '" + dstnep.name + "', link-port-direction: '" + Strings.Y_TXDIRECTION + "'}) "
        b2 = "MATCH (dst2: nep { name: '" + srcnep.name + "', link-port-direction: '" + Strings.Y_RXDIRECTION + "'}) "
        l1 = "MERGE (src1)-[rel1:nextnode]->(dst1) "
        l2 = "MERGE (src2)-[rel2:nextnode]->(dst2) "
        link1 = "MERGE (k1: tlslink{ name: '" + srcnep.name + "-" + dstnep.name + "', startnep:'" + srcnep.name + "', endnep: '" + dstnep.name + "'})"
        link2 = "MERGE (k2: tlslink{ name: '" + dstnep.name + "-" + srcnep.name + "', startnep:'" + dstnep.name + "', endnep: '" + srcnep.name + "'})"
        rel1  = '''
            MERGE (k1)-[rel:tlslink]->(src1)
            MERGE (k1)-[:tlslink]->(dst1)
            MERGE (k2)-[:tlslink]->(src2)
            MERGE (k2)-[:tlslink]->(dst2)
            '''
        query = a1 + b1 + a2 + b2 + l1 + l2 + link1 + link2 + rel1;




        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            tx.run(query)
            tx.commit()


    @staticmethod
    def createTlsLink( tls, tlsLinks):

        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            for link in tlsLinks:
                DbService.addVertex(tx, link)
                DbService.createEdge(tx, "start", link, Strings.VTYPE_NEP, link.src )
                DbService.createEdge(tx, "end", link, Strings.VTYPE_NEP, link.dst)
                DbService.addEdge(tx, "link", tls, link)
            tx.commit()


    @staticmethod
    def createNepLink(linkName: str, txNep: str, rxNep: str):
        if linkName is None or txNep is None or rxNep is None:
            msg = "Link creation failed. One of the item is None: linkName "
            if txNep is None:
                msg += "TxNep UUID"
            if rxNep is None:
                msg += "RxNep UUID"
            raise Exception(msg)

        query = 'MATCH(srcNep: nep { ' + Strings.Y_UUID + ": '" + txNep + "'," + \
                Strings.G_PORT_DIRECTION + ": '" + Strings.Y_TXDIRECTION + "'}) " + \
                'MATCH(dstNep: nep { ' + Strings.Y_UUID + ": '" + rxNep + "'," + \
                Strings.G_PORT_DIRECTION + ": '" + Strings.Y_RXDIRECTION + "'}) " +\
                'MERGE (srcNep)-[rel:link]->(dstNep)'
        #print (query)
        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            tx.run(query)
            tx.commit()

    @staticmethod
    def createService():
        #print ("Service created.")
        pass

    @staticmethod
    def AddPcsmInfo(name: str, pcsmstate: PcsmState):

        info = GPcsmInfo(name, pcsmstate)

        query = 'MERGE(n:' + info.type + ' {uuid: "' + info.uuid + '" })' \
                           + 'ON CREATE SET n += {props}'

        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            tx.run( query, parameters={"props": info.properties})
            tx.commit()

    @staticmethod
    def DeleteAllRecords():
        query = 'match(m) detach delete m'
        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            tx.run( query)
            tx.commit()
    @staticmethod
    def GetNodeWithName(name):
        with DbService._dbdriver.session() as session:
            return session.run('MATCH(m:degree {name:"N=1"}) return m')
        #dbService.installInstance( "bolt://localhost:7687", "neo4j", "infinera" )

    @staticmethod
    def addTopology(topologyName, roadmNode):
        topo = Topology(topologyName)
        roadm = Roadm(roadmNode)
        topo.addRoadmNode(roadm)
        insert_toplogy_query = "MERGE(n:" + topo.type + '{ uuid: "' + topo.uuid + '"}) ' \
                               + 'ON CREATE SET n += {my_prop}'
        insert_roadm_query = "MERGE(n:" + roadm.type + '{ uuid: "' + roadm.uuid + '"}) ' \
                               + 'ON CREATE SET n += {my_prop}'
        insert_relation_query = "MATCH(src: " + topo.type + "{ uuid: {source_uuid} })" \
                        + "MATCH(dst: " + roadm.type + "{ uuid: {dest_uuid} }) " \
                        + "MERGE (src)-[rel:roadm]->(dst)"

        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            tx.run(insert_toplogy_query, parameters={"my_prop": topo.properties})
            tx.run(insert_roadm_query,   parameters={"my_prop": roadm.properties})
            tx.run(insert_relation_query, parameters={"source_uuid": topo.uuid, "dest_uuid": roadm.uuid})
            tx.commit()
    @staticmethod
    def getRoadmByName (name):
        q = 'MATCH (n:roadm { name: "' + name + '"} return n'
        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            tx.run(q)
            tx.commit()



    @staticmethod
    def AddTlsToRoadm(roadm, tls:TLS):


        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            DbService.addVertex(tx, roadm)
            rdm = tx.run('MATCH (n:roadm { uuid: "' +  roadm.uuid + '" }) return n.uuid')
            roadms = rdm.value();
            print ( len(roadms))
            print ( "roadm = " +  roadms[0] )
            DbService.addEdge(tx, "tls", roadm, tls)
            tx.commit()

    @staticmethod
    def addTls (tls:TLS, roadmNode):
        ilas = tls.getIlaList()
        degree=tls.getDegree()
        adjacent = tls.getAdjacentRoadm()

        if degree is None or adjacent is None:
            raise Exception ("Empty Degree/Adjacent, invalid tls specification")
        #
        # q_insert_tls    = DbService.createVertex( tls )
        # q_insert_adj    = DbService.createVertex( adjacent )
        # q_insert_degree =  DbService.createVertex( degree )


        ingressState = TlsState( Strings.V_INGRESS, tls.name + "ingress")
        egressState  = TlsState( Strings.V_EGRESS,  tls.name + "egress")


        ingressRnc = GPcsmInfo("rnc", "1rnc" + degree.name)
        ingressTlc = GPcsmInfo("tlc", "2tlc" + degree.name)
        egressRnc =  GPcsmInfo("rnc", "3rnc" + degree.name)
        egresstlc =  GPcsmInfo("tlc", "4tlc" + degree.name)

        peerEgRnc = GPcsmInfo("rnc", "5rnc" + adjacent.name)
        peerEgTlc = GPcsmInfo("tlc", "6tlc" + adjacent.name)

        peerInRnc = GPcsmInfo("rnc", "7rnc" + adjacent.name)
        peerInTlc = GPcsmInfo("tlc", "8tlc" + adjacent.name)

        peerEgRnc.owner = 'peer'
        peerEgTlc.owner = 'peer'
        peerInRnc.owner = 'peer'
        peerInTlc.owner = 'peer'

        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            DbService.addVertex(tx, tls)
            DbService.AddDegreeNode(adjacent, tx)
            DbService.addVertex(tx, degree)
            DbService.addVertex(tx, ingressState)
            DbService.addVertex(tx, egressState)
            DbService.AddDegreeNode(degree, tx)

            DbService.addEdge(tx, "degree", tls, degree)
            DbService.addEdge(tx, "adjacent_node", tls, adjacent)
            DbService.addEdge(tx, "ingress", tls, ingressState)
            DbService.addEdge(tx, "egress", tls, egressState)

#TLC-RNC details
            DbService.addVertex(tx, ingressRnc)
            DbService.addVertex(tx, ingressTlc)
            DbService.addVertex(tx, egressRnc)
            DbService.addVertex(tx, egresstlc)
            DbService.addVertex(tx, peerEgRnc)
            DbService.addVertex(tx, peerEgTlc)
            DbService.addVertex(tx, peerInRnc)
            DbService.addVertex(tx, peerInTlc)


            DbService.addEdge(tx, "nextpcsm", ingressState, ingressRnc)
            DbService.addEdge(tx, "nextpcsm", ingressRnc, ingressTlc)
            DbService.addEdge(tx, 'nextpcsm', peerInTlc, peerInRnc)

            startNextPcsm = ingressTlc

            DbService.addEdge(tx, "prevpcsm", egressState, egressRnc)
            DbService.addEdge(tx, "prevpcsm", egressRnc, egresstlc)
            DbService.addEdge(tx, 'prevpcsm', peerEgTlc, peerEgRnc)

            startPrevPcsm = egresstlc


            for ila in ilas:
                DbService.AddIlaNode(ila, tx)
                DbService.addEdge(tx, "ila", tls, ila)
                ilaTlc = GPcsmInfo("tlc", "666tlc-" + ila.name)
                peerIlaTlc = GPcsmInfo("tlc", "999tlc-" + ila.name)
                peerIlaTlc.owner = 'peer'
                DbService.addVertex(tx, ilaTlc)
                DbService.addVertex(tx, peerIlaTlc)
                #DbService.addEdge(tx, 'myila',ilaTlc, ila)
                DbService.addEdge(tx, 'nextpcsm',startNextPcsm, ilaTlc)
                DbService.addEdge(tx, 'prevpcsm',startPrevPcsm, peerIlaTlc)
                startNextPcsm = ilaTlc
                startPrevPcsm = peerIlaTlc
            DbService.addEdge(tx, 'prevpcsm', startNextPcsm, peerEgTlc)
            DbService.addEdge(tx, 'nextpcsm', startPrevPcsm, peerInTlc)
            tx.commit()
#s = dbService()
#print (s.getInstance())
#print (dbService.getInstance())
