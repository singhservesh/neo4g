#from neo4j.v1 import GraphDatabase
from common.Node import Roadm as roadm
from common.GraphVertex import GraphVertex as vertex
from common.Node import Degree as degree
from common.Connection import *
from common.CommonStrings import CommonStrings as Strings
from common.NodeEdgePoint import NodeEdgePoint as Nep
from common.ConnectivityService import ConnectivityService as Service
from common.ConnectivityService import ServiceRequest as ServiceReq

from common.ConnectivityService import DirectedService as DirectedService
from common.tls import TLS as TLS
from common.dbservices import DbService as db
from common.JsonTopology import JsonTopology as JsonTopology
from neo4j import exceptions as neo4jexceptions
from neo4j import SessionExpired as Neo4jSessionException
from neobolt.exceptions import CypherSyntaxError as ErrorInCypherSyntax
from common.pcsmInfo import PcsmState as PcsmState

import json
import time

pcsmstate = PcsmState()
pcsmstate.lbandState = 'BLOCKED'
pcsmstate.cbandState = 'READY'



def addTlsToRoadm( tlsname,Rdm, db, jsontls):
    tls=TLS(tlsname)
    isDegreeAdded = False
    try:
        for node in jsontls.nodeList:
            if isDegreeAdded == False:
                tls.addDegree(node)
                isDegreeAdded = True
            else:
                tls.addAdjacentRoadm(node)
        db.addTls(tls, currentRoadName)
        db.AddTlsToRoadm(Rdm, tls)
        db.createTlsLink(tls, jsontls.linkList)

    except Exception as ex:
        print("Exception:" + ex.__name__ + str(ex))


def validateUserLink ( list):
    roadm = []
    degree= []
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
            degree.append(nodedegree[1])
    print(roadm)
    print(degree)
    lth = len(roadm)-2
    while lth > 1:
        if roadm[lth] != roadm[lth-1]:
            raise Exception ('Link specification error')
        lth -= 2


def createTestService( database:db, service:ServiceReq):
    database.createtestservice(service)

def readfile(filename):
    f = open(filename, "r")
    return f.read()

def createConnection ():
    pass
    service = Service('cs-1')
    smca = SmcA('scma')
    nmca = NmcA('nmca')
    smc = Smc('smc')
    nmc = Nmc('nmc')
    userlink = []
    validateUserLink(userlink)
    s1 = DirectedService('cs-1', 'R1:D1:SIP1')
    s2 = DirectedService('cs-1', 'R5:D1:SIP1')


db.installInstance()
print("Testing Json Decode")

data = readfile("tls.json")
data2 = readfile("tls2.json")

d1tls = readfile("d1.json")
d2tls = readfile("d2.json")
d3tls = readfile("d3.json")

jsond1 = json.loads(d1tls)
jsond2 = json.loads(d2tls)
jsond3 = json.loads(d3tls)

topod1 = JsonTopology.decodeme(jsond1)
topod2 = JsonTopology.decodeme(jsond2)
topod3 = JsonTopology.decodeme(jsond3)

currentRoadName = 'R3'
Rdm = roadm(currentRoadName)


addTlsToRoadm('d1tls',Rdm,db,topod1)
addTlsToRoadm('d2tls',Rdm,db,topod2)
addTlsToRoadm('d3tls',Rdm,db,topod3)

#create all services.
topo_s1  = ["R1:R1D2-R2:R2D1",  "R2:R2D2-R3:R3D3", "R3:R3D2-R4:R4D1", "R4:R4D3-R9:R9D1","R9:R9D3-R13:R13D1"]
topo_s10 = ["R10:R10D1-R7:R7D1","R7:R7D2-R8:R8D1", "R8:R8D2-R3:R3D1", "R3:R3D2-R4:R4D1","R4:R4D3-R9:R9D1","R9:R9D2-R14:R14D1"]
topo_s11 = ["R11:R11D1-R7:R7D3","R7:R7D2-R8:R8D1", "R8:R8D2-R3:R3D1", "R3:R3D2-R4:R4D1","R4:R4D2-R5:R5D1","R5:R5D2-R6:R6D1"]
topo_s12 = ["R12:R12D1-R8:R8D3","R8:R8D2-R3:R3D1", "R3:R3D2-R4:R4D1"]


srq1 = ServiceReq('s1','s1')
smca1 = SmcA('scma1')
nmca1 = NmcA('nmca1')
smc1 = Smc('smc1')
nmc1 = Nmc('nmc1')
srq1.smca = smca1
srq1.a = 'R1D2P1'
srq1.z = 'R13D1P1'
srq1.smcs.append(smc1)
srq1.nmcs.append(nmc1)
srq1.nmcas.append(nmca1)
srq1.tc = topo_s1
createTestService(db,srq1)
#exit(1)
srq10 = ServiceReq('s10','s10')
smca10 = SmcA('scma10')
nmca10 = NmcA('nmca10')
smc10 = Smc('smc10')
nmc10 = Nmc('nmc10')
srq10.smca = smca10
srq10.a = 'R10D1P1'
srq10.z = 'R14D1P1'
srq10.smcs.append(smc10)
srq10.nmcs.append(nmc10)
srq10.nmcas.append(nmca10)
srq10.tc = topo_s10
createTestService(db,srq10)

#exit(1)

srq11 = ServiceReq('s11','s11')
smca11 = SmcA('scma11')
nmca11 = NmcA('nmca11')
smc11 = Smc('smc11')
nmc11 = Nmc('nmc11')
srq11.smca = smca11
srq11.a = 'R11D1P1'
srq11.z = 'R6D1P1'
srq11.smcs.append(smc11)
srq11.nmcs.append(nmc11)
srq11.nmcas.append(nmca11)
srq11.tc = topo_s11
createTestService(db,srq11)

#exit(1)
srq12 = ServiceReq('s12','s12')
smca12 = SmcA('scma12')
nmca12 = NmcA('nmca12')
smc12 = Smc('smc12')
nmc12 = Nmc('nmc12')
srq12.smca = smca12
srq12.a = 'R12D1P1'
srq12.z = 'R4D1P1'
srq12.smcs.append(smc12)
srq12.nmcs.append(nmc12)
srq12.nmcas.append(nmca12)
srq12.tc = topo_s12
createTestService(db,srq12)

exit(1)


m = json.loads(data);
m2 = json.loads(data2);
S= JsonTopology.decodeme(m)
S2= JsonTopology.decodeme(m2)


#time.sleep(200)
repeat = 0

data = readfile("tls.json")

tls = TLS("tlsNode")
tls2 = TLS ("sfoside")


isDegreeAdded = False
try:
    for node in S2.nodeList:
        if isDegreeAdded == False:
            tls2.addDegree(node)
            isDegreeAdded = True
        else:
            tls2.addAdjacentRoadm(node)
    db.addTls(tls2, currentRoadName)
    db.AddTlsToRoadm(Rdm, tls2)
    db.createTlsLink(tls2, S2.linkList)

except Exception as ex:
    print("Exception:" + ex.__name__ + str(ex))


isDegreeAdded = False

while repeat !=1:
    start = time.ctime()
    try:
        for node in S.nodeList:
            if node.type == Strings.VTYPE_ILA:
                #db.AddIlaNode(node)
                tls.addILA(node)
                #db.AddPcsmInfo('pcsm-ila-' + node.name, pcsmstate)
            else:
                #db.AddDegreeNode(node)
                 if isDegreeAdded == False:
                     tls.addDegree(node)
                     isDegreeAdded = True
                 else :
                    tls.addAdjacentRoadm(node)
                #db.AddPcsmInfo('pcsm-mux-' + node.name, pcsmstate)
                #db.AddPcsmInfo('pcsm-tlc-' + node.name, pcsmstate)
        for link in S.linkList:
            # pass
            db.createNepLink( link.name, link.src, link.dst)

        #db.DeleteAllRecords();
        print('Start ' + start)
    except neo4jexceptions.ConnectionExpired as ce:
        print( "Exception :Connection expired: " + str(ce))
        continue

    except Neo4jSessionException as SessExp:
        print( "Session Expired:" + str(SessExp))
        continue

    except  ErrorInCypherSyntax as er:
        print("Exception" + str(er))
        continue

    except Exception as ex:
        print("Exception:" + ex.__name__ + str(ex) )
        continue

    print('End at ' + time.ctime())
    repeat=1
    #db.addTopology("firsttopo", "firstRoadm")

    db.addTls(tls, currentRoadName)
    db.AddTlsToRoadm(Rdm, tls)
    db.createTlsLink(tls, S.linkList)
    # for link in S.linkList:
        # pass
        # db.createNepLink(link.name, link.src, link.dst)
    #createConnection()
    db.createService()
    exit(7)
    #print ("Sleeping....")
    #time.sleep(5)
while repeat!=10001:
    try:
        data = db.GetNodeWithName('node')
        repeat = repeat + 1
        for record in data:
            #print ( record['m'].__dict__['_properties'])
            #print ( record['m'].__dict__)
            #print (repeat)
            pass
    except  ErrorInCypherSyntax as er:
        print("Exception" + str(er))

    except Exception as ex:
        print("Exception" + ex.__name__ + str(ex))

print(S)

