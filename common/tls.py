from common.GraphVertex import GraphVertex as Vertex
from common.Direction import Direction as Direction
from common.Node import Ila as Ila
from common.Node import Degree as degree
from common.Node import AdjNode as AdjRoadm
from common.CommonStrings import CommonStrings as Strings


class TLS (Vertex):


    def __init__(self, name):
        super().__init__(Strings.VTYPE_TLS, name)
        self.ila = []
        self.degree: degree = None
        self.adj: AdjRoadm = None

    def addILA(self, node: Ila):
        self.ila.append(node)

    def addDegree(self, node: degree):
        if self.degree is None:
            self.degree = node

    def addAdjacentRoadm(self, node:AdjRoadm):
        if self.adj is None:
            self.adj = node

    def getAdjacentRoadm(self):
        return self.adj


    def getIlaList(self):
        return self.ila


    def getDegree(self):
        return self.degree