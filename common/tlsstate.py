from common.GraphVertex import GraphVertex as Vertex
from common.Direction import Direction as Direction
from common.Node import Ila as Ila
from common.Node import Degree as degree
from common.CommonStrings import CommonStrings as Strings

class TlsState ( Vertex):
    def __init__(self, direction, name):
        super().__init__(Strings.VTYPE_TLSSTATE, name)
        if direction is not Strings.V_EGRESS and direction is not Strings.V_INGRESS:
            raise Exception('wrong direction: {' + direction + '} use ingress or egress')
        self.dir = direction
        self.setproperty("Direction", direction)

