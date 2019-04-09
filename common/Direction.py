
from common.CommonStrings import CommonStrings as Strings
from common.GraphVertex import GraphVertex as Vertex

from typing import List

class Direction(Vertex):

    _txnep: list
    _rxnep: list

    def __init__(self, vertexType, name):
        super().__init__(vertexType, name)
        self._txnep = []
        self._rxnep = []

    def __str__(self):
        return " Card-UUID = "

    @property
    def txnep (self):
        return self._txnep

    @txnep.setter
    def txnep (self, txnep: list):
        self._txnep.clear()
        for nep in txnep:
            nep
            self._txnep.append(nep)

    @property
    def rxnep(self):
        return self._rxnep

    @rxnep.setter
    def rxnep(self, rxnep: list):
        self._rxnep.clear()
        for nep in rxnep:
            self._rxnep.append(nep)

    @property
    def neps(self):
        neplist = []
        for nep in self._txnep:
            neplist.append(nep)
        for nep in self._rxnep:
            neplist.append(nep)
        return neplist

    @neps.setter
    def neps(self, neplist: List):
        for nep in neplist:
            if nep.direction == Strings.Y_TXDIRECTION:
                self._txnep.append(nep)
            else:
                self._rxnep.append(nep)


a = Direction( "Roadm","Roadm")
print(a)


