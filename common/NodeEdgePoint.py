from common.GraphVertex import GraphVertex as Vertex
from common.CommonStrings import CommonStrings as Strings


class NodeEdgePoint(Vertex):
    direction: str
    def __init__(self, name='1-A-3', direction=Strings.Y_TXDIRECTION):
        super().__init__(Strings.VTYPE_NEP, name)
        self.direction = direction

    @property
    def direction(self):
        return self.getproperty(Strings.Y_PORT_DIRECTION)

    @direction.setter
    def direction(self, direction):
        self.setproperty( Strings.Y_PORT_DIRECTION, direction)
