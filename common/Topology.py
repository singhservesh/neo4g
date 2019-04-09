from common.Node import Roadm as Roadm
from common.Node import Node as Node
from common.Node import Ila as Ila
from common.Node import VNode as VNode
from common.CommonStrings import CommonStrings as Strings
from common.GraphVertex import GraphVertex as Vertex


class Topology(Vertex):
    def __init__(self, name):
        super().__init__(Strings.VTYPE_TOPOLOGY, name)
        self.nodeCount=0
        self.roadmCount = 0
        self.ilaCount = 0
        self.vnodeCount = 0
        self.link = []
        self.node = []

    def addRoadmNode(self, node: Roadm):
        self.addNode(node)

    def addVNode(self, node: VNode):
        self.addNode(node)

    def addIlaNode ( self, node:Ila):
        self.addNode(Ila)

    def addNode(self, node:Node ):

        if node.type == Strings.VTYPE_ROADM:
            if self.roadmCount == 1:
                raise Exception ("A topology cannot have more that one roadm node.")
            self.roadmCount += 1

        elif node.type is Strings.VTYPE_ILA:
            self.ilaCount += 1
        elif node.type is Strings.VTYPE_VNODE:
            self.vnodeCount += 1
        else:
            raise Exception("Please use only ILA or ROAD nodes only.")
        self.node.append(node)

    def __str__(self):
        return super().__str__() + "," + str(self.ilaCount) + str(self.roadmCount)

    def getNodeCount(self):
        return "" + str(self.roadmCount) + str(self.ilaCount)

a = Topology("TopologyroadmName")
roadm = Roadm('SunnyVale')
ila = Ila('SunnyVale-2')
a.addNode( roadm )
a.addNode( ila )
a.addVNode( VNode("virtual-node-added"))
node2 = Ila ('ilaNode')
a.addNode(node2)
print (a.getNodeCount())
print(a)

