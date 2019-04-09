from typing import List

from common.Link import Link
from common.Node import Roadm as roadm
from common.GraphVertex import GraphVertex as vertex
from common.Direction import Direction as Direction
from common.Node import Degree as Degree
from common.Node import Ila as Ila
from common.CommonStrings import CommonStrings as Strings
from common.NodeEdgePoint import NodeEdgePoint as GraphNodeEdgePoint, NodeEdgePoint

import json


def MissingItemInList(obj=None, itemList: list = None):
    if obj is None:
        obj = {}
    if itemList is None:
        return 'Empty Item List'
    for item in itemList:
        if item not in obj:
            return item
    return ""

class JsonName:

    valuename: str
    value: str

    def __init__(self, valuename, value):
        self.valuename = valuename
        self.value = value

    @staticmethod
    def decodeme(obj):
        if Strings.Y_NAMED_VALUE not in obj:
            raise Exception('BadFile')
        if Strings.Y_VALUE_KEY_NAME not in obj:
            raise Exception('BadFile')
        return JsonName(obj[Strings.Y_VALUE_KEY_NAME], obj[Strings.Y_NAMED_VALUE])



class JsonNep:

    def __init__(self):
        pass

    @staticmethod
    def decodeme(obj):

        missingItem = MissingItemInList(obj, [
            Strings.Y_UUID,
            Strings.Y_NAME,
            Strings.Y_ADMIN_STATE,
            Strings.Y_OPRATIONAL_STATE,
            Strings.Y_LAYER_PROTO_NAME,
            Strings.Y_LIFE_CYCL_STATE,
            Strings.Y_PORT_DIRECTION,
            Strings.Y_MAPPED_SIP,
            Strings.Y_AGGR_NEP])

        if len(missingItem) > 0:
            raise Exception ('Json File: tag is missing: ' + missingItem)

        aggregatedNodeEdgePoint = []
        for nepid in obj[Strings.Y_AGGR_NEP]:
                aggregatedNodeEdgePoint.append(nepid)

        nep = GraphNodeEdgePoint(obj[Strings.Y_NAME], obj[Strings.Y_PORT_DIRECTION])
        attr = {}
        attr[Strings.G_PORT_DIRECTION]   = obj[Strings.Y_PORT_DIRECTION];
        #attr[Strings.Y_AGGR_NEP]         = aggregatedNodeEdgePoint,
        attr[Strings.Y_ADMIN_STATE]      = obj[Strings.Y_ADMIN_STATE]
        #attr[Strings.Y_MAPPED_SIP]       = obj[Strings.Y_MAPPED_SIP]
        attr[Strings.Y_OPRATIONAL_STATE] = obj[Strings.Y_OPRATIONAL_STATE]
        attr[Strings.Y_LAYER_PROTO_NAME] = obj[Strings.Y_LAYER_PROTO_NAME]
        attr[Strings.Y_LIFE_CYCL_STATE]  = obj[Strings.Y_LIFE_CYCL_STATE]

        nep.properties = attr
        return nep


class JsonNode:

    @staticmethod
    def decodeme(obj):

        missingItems = MissingItemInList(obj, [
            Strings.Y_UUID,
            Strings.Y_NAME,
            Strings.Y_ADMIN_STATE,
            Strings.Y_OPRATIONAL_STATE,
            Strings.Y_LAYER_PROTO_NAME,
            Strings.Y_LIFE_CYCL_STATE,
            Strings.Y_OWNED_NEP]
                                         )

        if len(missingItems) > 0:
            raise Exception ('Json File: tag item is missing: ' + missingItems)


        nameDict = obj[Strings.Y_NAME]
        type = ''
        name = ''
        for names in nameDict:
            data = JsonName.decodeme (names)
            if data.valuename == Strings.Y_NODE_TYPE:
                type = data.value
            if data.valuename == Strings.Y_NAME:
                name = data.value

        if type == Strings.VTYPE_DEGREE:
            direction= Degree(name)
        elif type == Strings.VTYPE_ILA:
            direction = Ila(name)
        else:
            raise Exception ("correct NODE type is not given in the request")

        print("Type=" + type + " direction=" + type)
        attr = {}
        attr[Strings.Y_ADMIN_STATE]      = obj[Strings.Y_ADMIN_STATE]
        attr[Strings.Y_OPRATIONAL_STATE] = obj[Strings.Y_OPRATIONAL_STATE]
        attr[Strings.Y_LAYER_PROTO_NAME] = obj[Strings.Y_LAYER_PROTO_NAME]
        attr[Strings.Y_LIFE_CYCL_STATE]  = obj[Strings.Y_LIFE_CYCL_STATE]

        direction.properties = attr

        neps: List[NodeEdgePoint] = []
        for nepid in obj[Strings.Y_OWNED_NEP]:
                neps.append(JsonNep.decodeme(nepid))

        direction.neps = neps
        return direction


class JsonLink:

    def __init__(self):
        pass

    @staticmethod
    def decodeme(obj):

        missingItem = MissingItemInList(obj, [
            Strings.Y_UUID,
            Strings.Y_NAME,
            Strings.Y_ADMIN_STATE,
            Strings.Y_OPRATIONAL_STATE,
            Strings.Y_LAYER_PROTO_NAME,
            Strings.Y_LIFE_CYCL_STATE,
            Strings.Y_LINK_NEP_ENDS,
            Strings.Y_LINK_NODE])

        if len(missingItem) > 0:
            raise Exception ('Json File: tag is missing: ' + missingItem)
        

        attr = {}
        neps = list(obj[Strings.Y_LINK_NEP_ENDS])
        attr[Strings.Y_ADMIN_STATE]      = obj[Strings.Y_ADMIN_STATE]
        attr[Strings.Y_OPRATIONAL_STATE] = obj[Strings.Y_OPRATIONAL_STATE]
        attr[Strings.Y_LAYER_PROTO_NAME] = obj[Strings.Y_LAYER_PROTO_NAME]
        attr[Strings.Y_LIFE_CYCL_STATE]  = obj[Strings.Y_LIFE_CYCL_STATE]
        
        link = Link( neps[0], neps[1], obj[Strings.Y_NAME])
        link.properties = attr
        return link


class JsonTopology():
    nodeList: list
    linkList: list
    mydict: dict
    def __init__(self):
        print ('empty call')
        self.nodeList = []
        self.linkList = []

    @staticmethod
    def decodeme (obj):
        topo: JsonTopology = JsonTopology()
        if 'node' in obj:
            for nodes in obj['node']:
                topo.nodeList.append(JsonNode.decodeme(nodes))
        else:
            raise Exception("Node error")

        if 'link' in obj:
            for link in obj['link']:
                topo.linkList.append(JsonLink.decodeme(link))
        else:
            raise Exception("Link error. Links are not given in the topology")
                
        return topo
