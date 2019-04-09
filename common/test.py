#from neo4j.v1 import GraphDatabase
from common.Node import Roadm as roadm
from common.GraphVertex import GraphVertex as vertex
from common.Node import Degree as degree
from common.Connection import *
from common.CommonStrings import CommonStrings as Strings
from common.NodeEdgePoint import NodeEdgePoint as Nep
from common.ConnectivityService import ConnectivityService as Service
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


def readfile(filename):
    f = open(filename, "r")
    return f.read()

def createConnection ():
    pass
    service = Service('cs-1')
    ds1 = DirectedService('cs-1')
    ds2 = DirectedService('cs-2')
    smca = SmcA('scma')
    nmca = NmcA('nmca')
    smc = Smc('smc')
    nmc = Nmc('nmc')
    UserLink = ['ROADM_1:D1:P1', 'ROADM:D2:P2' 'MY_ROADM:Sunnyvale:Sunnyvale;P=txlisbon']

db.installInstance()
print("Testing Json Decode")

data = readfile("tls.json")
data2 = readfile("tls2.json")
m = json.loads(data);
m2 = json.loads(data2);
S= JsonTopology.decodeme(m)
S2= JsonTopology.decodeme(m2)

Rdm = roadm('MY_ROADM')
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
    db.addTls(tls2, "MY_ROADM")
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

    db.addTls(tls, "MY_ROADM")
    db.AddTlsToRoadm(Rdm, tls)
    db.createTlsLink(tls, S.linkList)
    # for link in S.linkList:
        # pass
        # db.createNepLink(link.name, link.src, link.dst)

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

