from common.ConnectivityService import ConnectivityService as Service
from common.ConnectivityService import DirectedService as DirectedService
from common.ConnectivityService import ServiceRequest as ServiceRequest
from common.Connection import *
from common.Node import Roadm as Roadm
from common.Topology import Topology as Topology
from common.GraphVertex import GraphVertex as Vertex
from common.tls import TLS as TLS
from common.CommonStrings import CommonStrings as Strings
from common.NodeEdgePoint import NodeEdgePoint as Nep
from common.Node import Node as node
from common.pcsmInfo import PcsmState as PcsmState
from common.pcsmInfo import GPcsmInfo as GPcsmInfo
from common.tlsstate import TlsState as TlsState
from common.Node import Relation as NepRel
from common.NodeEdgePoint import ConnectionEdgePoint as Cep
from common.Link import Link
from neo4j import GraphDatabase
from neo4j import exceptions as neo4jexceptions


def RoadmNameFromDegree( degree):
    rd = degree.split("=")
    if len(rd) < 2:
        raise Exception ("Degree name does not contain roadm id/name")
    return rd[0]

# return Roadm and NEP entries.
def validateUserLink ( list):
    roadm = []
    nepids= []
    for item in list:
        rd = item.split('-')
        lth = len(rd)
        if lth != 2:
            raise Exception ('Bad Input')
        for node in rd:
            nodedegree = node.split(':')
            lth = len(nodedegree)
            if lth != 2:
                raise Exception ('Bad Format for ' + node + 'in ' + rd )
            for nd in nodedegree:
                lth = len(nd)
                if lth < 1:
                    raise Exception('Bad Format for ' + node + 'in ' + rd)
            roadm.append(nodedegree[0])
            nepids.append(nodedegree[1])
    print(roadm)
    print(nepids)
    lth = len(roadm)-2
    while lth > 1:
        if roadm[lth] != roadm[lth-1]:
            raise Exception ('Link specification error')
        lth -= 2
    return roadm, nepids


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
    def updateVirtualNode( tx, roadm, degree):
        pass


    @staticmethod
    def createService():
        service = Service('cs1')
        smca = SmcA('scma1')
        nmca = NmcA('nmca1')
        smc = Smc('smc1')
        nmc = Nmc('nmc1')
        s1 = DirectedService('cs-1', 'R1:D1:SIP1')
        s2 = DirectedService('cs-2', 'R5:D1:SIP1')

        vtx:vertex = []

        vtx.append(service)
        vtx.append(smca)
        vtx.append(nmca)
        vtx.append(smc)
        vtx.append(nmc)
        vtx.append(s1)
        vtx.append(s2)

        nepRel = []
        smclink = ['R1:R1D1-R2:R2D1', 'R2:R2D2-R3:R3D2', 'R3:R3D1-R4:R4D1', 'R4:R4D2-R5:R5D1']
        rdm,neps = validateUserLink(smclink)

        start = Roadm(rdm[0])

        startNep = 'R1:D1P1'
        endNep = 'R5:D1P1'
      
    
        startTxNep = Nep(startNep, startNep + 'tx', Strings.Y_TXDIRECTION)
        startRxNep = Nep(startNep, startNep + 'rx', Strings.Y_RXDIRECTION)
        startceptx = Cep(startNep, service.name + startNep + 'tx')
        startceprx = Cep(startNep, service.name + startNep + 'rx')
        nepRel.append(NepRel('smc', startceprx, smc))
        #nepRel.append(NepRel('smc', startceptx, smc))
        #nepRel.append(NepRel('nmc', startceprx, nmc))
        #nepRel.append(NepRel('nmc', startceptx, nmc))
        cnrel1 = NepRel('mynep', startceptx, startTxNep)
        cnrel2 = NepRel('mynep', startceprx, startRxNep)
        nepRel.append(cnrel1)
        nepRel.append(cnrel2)
        rel1 = NepRel('nep', start, startTxNep)
        rel2 = NepRel('nep', start, startRxNep)
        nepRel.append(rel1)
        nepRel.append(rel2)

        vtx.append(startTxNep)
        vtx.append(startRxNep)
        vtx.append(startceptx)
        vtx.append(startceprx)

        endTxNep = Nep(endNep, endNep + 'tx', Strings.Y_TXDIRECTION)
        endRxNep = Nep(endNep, endNep + 'rx', Strings.Y_RXDIRECTION)
        endceptx = Cep(endNep, service.name + endNep + 'tx')
        endceprx = Cep(endNep, service.name + endNep + 'rx')
        #nepRel.append(NepRel('smc', endceprx, smc))
        nepRel.append(NepRel('smc', endceptx, smc))
        #nepRel.append(NepRel('nmc', endceprx, nmc))
        #nepRel.append(NepRel('nmc', endceptx, nmc))
        cnrel1 = NepRel('mynep', endceptx, endTxNep)
        cnrel2 = NepRel('mynep', endceprx, endRxNep)
        nepRel.append(cnrel1)
        nepRel.append(cnrel2)
        vtx.append(endTxNep)
        vtx.append(endRxNep)
        vtx.append(endceptx)
        vtx.append(endceprx)
        linkId = 0;
        vtx.append(start)
        for i in range(1,len(rdm), 2):
            endRdm = Roadm(rdm[i])
            vtx.append(endRdm)

            nepTx = Nep(neps[i - 1], neps[i - 1] + 'tx', Strings.Y_TXDIRECTION)
            nepRx = Nep(neps[i - 1], neps[i - 1] + 'rx', Strings.Y_RXDIRECTION)
            cepTx = Cep(neps[i - 1], service.name + neps[i - 1] + 'tx')
            cepRx = Cep(neps[i - 1], service.name + neps[i - 1] + 'rx')
            #nepRel.append(NepRel('smc', cepRx, smc))
            nepRel.append(NepRel('smc', cepTx, smc))
            #nepRel.append(NepRel('nmc', cepRx, nmc))
            #nepRel.append(NepRel('nmc', cepTx, nmc))
            cnrel3 = NepRel('mynep', cepTx, nepTx)
            cnrel4 = NepRel('mynep', cepRx, nepRx)
            nepRel.append(cnrel3)
            nepRel.append(cnrel4)
            ccRel3 = NepRel('next', startceprx, cepTx)
            ccRel4 = NepRel('next', cepRx, startceptx)
            nepRel.append(ccRel3)
            nepRel.append(ccRel4)

            vtx.append(nepTx)
            vtx.append(nepRx)
            vtx.append(cepTx)
            vtx.append(cepRx)

            rel3 = NepRel('nep', start, nepTx)
            rel4 = NepRel('nep', start, nepRx)


            nepLocalTx = Nep(neps[i], neps[i] + 'tx', Strings.Y_TXDIRECTION)
            nepLocalRx = Nep(neps[i], neps[i] + 'rx', Strings.Y_RXDIRECTION)
            startceptx =  Cep( neps[i], service.name + neps[i] + 'tx')
            startceprx =  Cep( neps[i], service.name + neps[i] + 'rx')
            nepRel.append(NepRel('smc', startceprx, smc))
            #nepRel.append(NepRel('smc', startceptx, smc))
            #nepRel.append(NepRel('nmc', startceprx, nmc))
            #nepRel.append(NepRel('nmc', startceptx, nmc))
            cnrel1 = NepRel('mynep', startceptx, nepLocalTx)
            cnrel2 = NepRel('mynep', startceprx, nepLocalRx)
            nepRel.append(cnrel1)
            nepRel.append(cnrel2)

            vtx.append(nepLocalTx)
            vtx.append(nepLocalRx)
            vtx.append(startceptx)
            vtx.append(startceprx)

            rel1 = NepRel('nep', endRdm, nepLocalTx)
            rel2 = NepRel('nep', endRdm, nepLocalRx)

            nepRel.append(rel1)
            nepRel.append(rel2)
            nepRel.append(rel3)
            nepRel.append(rel4)
            start = endRdm

            link1 = Link( nepTx, nepLocalRx, smclink[linkId] +'start')
            link2 = Link( nepLocalTx, nepTx, smclink[linkId] + 'end')
            nepRel.append(NepRel('start', link1, nepTx) )
            nepRel.append(NepRel('end', link1, nepLocalRx))
            nepRel.append(NepRel('start', link2, nepLocalTx))
            nepRel.append(NepRel('end', link2, nepRx))
            vtx.append(link1)
            vtx.append(link2)
            linkId += 1


        ccRel3 = NepRel('next', startceprx, endceptx)
        ccRel4 = NepRel('next', endceprx, startceptx)
        nepRel.append(ccRel3)
        nepRel.append(ccRel4)

        rel1 = NepRel('nep', start, endTxNep)
        rel2 = NepRel('nep', start, endRxNep)
        nepRel.append(rel1)
        nepRel.append(rel2)



        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()

            for vt in vtx:
                DbService.addVertex(tx, vt)
            for nep in nepRel:
                DbService.addEdge( tx, nep.rel, nep.src, nep.dst)


            DbService.addEdge(tx, "smca", s1, smca)
            DbService.addEdge(tx, "nmca", s1, nmca)
            DbService.addEdge(tx, "smc",  s1, smc)
            DbService.addEdge(tx, "contains", smca, smc)
            DbService.addEdge(tx, "contains", smca, nmca)
            DbService.addEdge(tx, "contains", smc,  nmc)
            DbService.addEdge(tx, "contains", nmca, nmc)
            DbService.addEdge(tx, "contains", service, s1)
            DbService.addEdge(tx, "contains", service, s2)

            DbService.updateVirtualNode(tx, rdm, nep)
            
            tx.commit()


    @staticmethod
    def AddPcsmInfo(name: str, pcsmstate: PcsmState):
    #TODO exit
        return
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


        downstream  = TlsState( Strings.V_INGRESS, tls.name + "downstream")
        egressState  = TlsState( Strings.V_EGRESS, tls.name + "upstream")


        ingressRnc = GPcsmInfo("rnc", "1r" + degree.name)
        ingressTlc = GPcsmInfo("tlc", "2t" + degree.name)
        egressRnc  = GPcsmInfo("rnc", "3r" + degree.name)
        egresstlc  = GPcsmInfo("tlc", "4t" + degree.name)

        peerEgRnc = GPcsmInfo("rnc", "1r" + adjacent.name)
        peerEgTlc = GPcsmInfo("tlc", "2t" + adjacent.name)
        peerInRnc = GPcsmInfo("rnc", "3r" + adjacent.name)
        peerInTlc = GPcsmInfo("tlc", "4t" + adjacent.name)

        peerEgRnc.owner = peerEgTlc.owner = peerInRnc.owner = peerInTlc.owner = 'peer'

        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()
            DbService.addVertex(tx, tls)
            DbService.AddDegreeNode(adjacent, tx)
            DbService.addVertex(tx, degree)
            #TODO DbService.addVertex(tx, downstream)
            #TODO DbService.addVertex(tx, egressState)
            DbService.AddDegreeNode(degree, tx)

            DbService.addEdge(tx, "degree", tls, degree)
            DbService.createEdge(tx, Strings.VR_DEGROADM, degree, Strings.VTYPE_ROADM, roadmNode)

            DbService.addEdge(tx, "adjacent_degree", tls, adjacent)
            DbService.addEdge(tx, "downstream", tls, downstream)
            DbService.addEdge(tx, "upstream", tls, egressState)

#TODO TLC-RNC details
            # DbService.addVertex(tx, ingressRnc)
            # DbService.addVertex(tx, ingressTlc)
            # DbService.addVertex(tx, egressRnc)
            # DbService.addVertex(tx, egresstlc)
            # DbService.addVertex(tx, peerEgRnc)
            # DbService.addVertex(tx, peerEgTlc)
            # DbService.addVertex(tx, peerInRnc)
            # DbService.addVertex(tx, peerInTlc)

            rd_name = RoadmNameFromDegree(adjacent.name)
            ad_roadm = Roadm(rd_name)

            DbService.addVertex(tx, ad_roadm)
            DbService.addEdge(tx, Strings.VR_DEGROADM, adjacent, ad_roadm)

#TODO Enable this for PCSM
          #  DbService.addEdge(tx, "nextpcsm", downstream, ingressRnc)
          #  DbService.addEdge(tx, "nextpcsm", ingressRnc, ingressTlc)
          #  DbService.addEdge(tx, 'nextpcsm', peerInTlc, peerInRnc)

            startNextPcsm = ingressTlc

#TODO enable for PCSM
          #  DbService.addEdge(tx, "prevpcsm", egressState, egressRnc)
          #  DbService.addEdge(tx, "prevpcsm", egressRnc, egresstlc)
          #  DbService.addEdge(tx, 'prevpcsm', peerEgTlc, peerEgRnc)

            startPrevPcsm = egresstlc


            for ila in ilas:
                DbService.AddIlaNode(ila, tx)
                DbService.addEdge(tx, "ila", tls, ila)
                ilaTlc = GPcsmInfo("tlc", "1." + ila.name)
                peerIlaTlc = GPcsmInfo("tlc", "2." + ila.name)
                peerIlaTlc.owner = 'peer'
                DbService.addVertex(tx, ilaTlc)
                DbService.addVertex(tx, peerIlaTlc)
                #DbService.addEdge(tx, 'myila',ilaTlc, ila)
             #   DbService.addEdge(tx, 'nextpcsm',startNextPcsm, ilaTlc)
             #   DbService.addEdge(tx, 'prevpcsm',startPrevPcsm, peerIlaTlc)
                startNextPcsm = ilaTlc
                startPrevPcsm = peerIlaTlc
         #   DbService.addEdge(tx, 'prevpcsm', startNextPcsm, peerEgTlc)
         #   DbService.addEdge(tx, 'nextpcsm', startPrevPcsm, peerInTlc)
            tx.commit()
#s = dbService()
#print (s.getInstance())

    #@staticmethod
    #def FindRoadms(smc):

    @staticmethod
    def createtestservice( service:ServiceRequest):

        smca = service.smca
        nmca = service.nmcas[0]
        smc = service.smcs[0]
        nmc = service.nmcs[0]
        s1 = DirectedService(service.name + service.a, service.a)
        s2 = DirectedService(service.name + service.z, service.z)

        vtx: vertex = []
        serviceV = Service(service.name)

        vtx.append( serviceV )
        vtx.append(smca)
        vtx.append(nmca)
        vtx.append(smc)
        vtx.append(nmc)
        vtx.append(s1)
        vtx.append(s2)

        nepRel = []
        topologyConstraint = service.tc
        rdm, neps = validateUserLink(topologyConstraint)

        start = Roadm(rdm[0])

        startNep = service.a
        endNep = service.z

        startTxNep = Nep(startNep, startNep + 'tx', Strings.Y_TXDIRECTION)
        startRxNep = Nep(startNep, startNep + 'rx', Strings.Y_RXDIRECTION)
        startceptx = Cep(startNep, service.name + startNep + 'tx')
        startceprx = Cep(startNep, service.name + startNep + 'rx')
        nepRel.append(NepRel('smc', startceprx, smc))
        # nepRel.append(NepRel('smc', startceptx, smc))
        # nepRel.append(NepRel('nmc', startceprx, nmc))
        # nepRel.append(NepRel('nmc', startceptx, nmc))
        cnrel1 = NepRel('mynep', startceptx, startTxNep)
        cnrel2 = NepRel('mynep', startceprx, startRxNep)
        nepRel.append(cnrel1)
        nepRel.append(cnrel2)
        rel1 = NepRel('nep', start, startTxNep)
        rel2 = NepRel('nep', start, startRxNep)
        nepRel.append(rel1)
        nepRel.append(rel2)

        vtx.append(startTxNep)
        vtx.append(startRxNep)
        vtx.append(startceptx)
        vtx.append(startceprx)

        endTxNep = Nep(endNep, endNep + 'tx', Strings.Y_TXDIRECTION)
        endRxNep = Nep(endNep, endNep + 'rx', Strings.Y_RXDIRECTION)
        endceptx = Cep(endNep, service.name + endNep + 'tx')
        endceprx = Cep(endNep, service.name + endNep + 'rx')
        # nepRel.append(NepRel('smc', endceprx, smc))
        nepRel.append(NepRel('smc', endceptx, smc))
        # nepRel.append(NepRel('nmc', endceprx, nmc))
        # nepRel.append(NepRel('nmc', endceptx, nmc))
        cnrel1 = NepRel('mynep', endceptx, endTxNep)
        cnrel2 = NepRel('mynep', endceprx, endRxNep)
        nepRel.append(cnrel1)
        nepRel.append(cnrel2)
        vtx.append(endTxNep)
        vtx.append(endRxNep)
        vtx.append(endceptx)
        vtx.append(endceprx)

        vtx.append(start)
        for i in range(1, len(rdm), 2):
            endRdm = Roadm(rdm[i])
            vtx.append(endRdm)

            nepTx = Nep(neps[i - 1], neps[i - 1] + 'tx', Strings.Y_TXDIRECTION)
            nepRx = Nep(neps[i - 1], neps[i - 1] + 'rx', Strings.Y_RXDIRECTION)
            cepTx = Cep(neps[i - 1], service.name + neps[i - 1] + 'tx')
            cepRx = Cep(neps[i - 1], service.name + neps[i - 1] + 'rx')
            # nepRel.append(NepRel('smc', cepRx, smc))
            nepRel.append(NepRel('smc', cepTx, smc))
            # nepRel.append(NepRel('nmc', cepRx, nmc))
            # nepRel.append(NepRel('nmc', cepTx, nmc))
            cnrel3 = NepRel('mynep', cepTx, nepTx)
            cnrel4 = NepRel('mynep', cepRx, nepRx)
            nepRel.append(cnrel3)
            nepRel.append(cnrel4)
            ccRel3 = NepRel('next', startceprx, cepTx)
            ccRel4 = NepRel('next', cepRx, startceptx)
            nepRel.append(ccRel3)
            nepRel.append(ccRel4)

            vtx.append(nepTx)
            vtx.append(nepRx)
            vtx.append(cepTx)
            vtx.append(cepRx)

            rel3 = NepRel('nep', start, nepTx)
            rel4 = NepRel('nep', start, nepRx)

            nepLocalTx = Nep(neps[i], neps[i] + 'tx', Strings.Y_TXDIRECTION)
            nepLocalRx = Nep(neps[i], neps[i] + 'rx', Strings.Y_RXDIRECTION)
            startceptx = Cep(neps[i], service.name + neps[i] + 'tx')
            startceprx = Cep(neps[i], service.name + neps[i] + 'rx')
            nepRel.append(NepRel('smc', startceprx, smc))
            # nepRel.append(NepRel('smc', startceptx, smc))
            # nepRel.append(NepRel('nmc', startceprx, nmc))
            # nepRel.append(NepRel('nmc', startceptx, nmc))
            cnrel1 = NepRel('mynep', startceptx, nepLocalTx)
            cnrel2 = NepRel('mynep', startceprx, nepLocalRx)
            nepRel.append(cnrel1)
            nepRel.append(cnrel2)

            vtx.append(nepLocalTx)
            vtx.append(nepLocalRx)
            vtx.append(startceptx)
            vtx.append(startceprx)

            rel1 = NepRel('nep', endRdm, nepLocalTx)
            rel2 = NepRel('nep', endRdm, nepLocalRx)

            nepRel.append(rel1)
            nepRel.append(rel2)
            nepRel.append(rel3)
            nepRel.append(rel4)
            start = endRdm

            link1 = NepRel('next', cepTx, startceprx)
            link2 = NepRel('next', startceptx, cepRx )
            nepRel.append(link1)
            nepRel.append(link2)



        ccRel3 = NepRel('next', startceprx, endceptx)
        ccRel4 = NepRel('next', endceprx, startceptx)
        nepRel.append(ccRel3)
        nepRel.append(ccRel4)

        rel1 = NepRel('nep', start, endTxNep)
        rel2 = NepRel('nep', start, endRxNep)
        nepRel.append(rel1)
        nepRel.append(rel2)

        with DbService._dbdriver.session() as session:
            tx = session.begin_transaction()

            for vt in vtx:
                DbService.addVertex(tx, vt)
            for nep in nepRel:
                DbService.addEdge(tx, nep.rel, nep.src, nep.dst)

            DbService.addEdge(tx, "smca", s1, smca)
            DbService.addEdge(tx, "nmca", s1, nmca)
            DbService.addEdge(tx, "smc", s1, smc)
            DbService.addEdge(tx, "contains", smca, smc)
            DbService.addEdge(tx, "contains", smca, nmca)
            DbService.addEdge(tx, "contains", smc, nmc)
            DbService.addEdge(tx, "contains", nmca, nmc)
            DbService.addEdge(tx, "contains", serviceV, s1)
            DbService.addEdge(tx, "contains", serviceV, s2)

            DbService.updateVirtualNode(tx, rdm, nep)

            tx.commit()
