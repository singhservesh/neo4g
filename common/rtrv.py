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


db.installInstance()
print("Testing Json Decode")



