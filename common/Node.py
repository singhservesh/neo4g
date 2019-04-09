from common.GraphVertex import GraphVertex as Vertex
from common.Direction import Direction as Direction
from common.CommonStrings import CommonStrings as Strings

class Node(Direction):
    def __init__(self, nodetype, name):
        super().__init__(nodetype, name)

    def __str__(self):
        return self.dump()

    def dump(self):
        return "Name = " + self.type + '   ' + 'UUID = ' + self.uuid

class Roadm (Node):
    def __init__(self, name):
        super().__init__(Strings.VTYPE_ROADM, name)


class Ila(Node):
    def __init__(self, name):
        super().__init__(Strings.VTYPE_ILA, name)

    def __str__(self):
        return super().__str__()

class VNode(Node):
    def __init__(self, name):
        super().__init__(Strings.VTYPE_VNODE, name)

    def __str__(self):
        return super().__str__()

class AdjNode(Node):
    def __init__(self, name):
        super().__init__(Strings.VTYPE_ADJROADM, name)

    def __str__(self):
        return super().__str__()


class Degree(Node):
    def __init__(self, name):
        super().__init__(Strings.VTYPE_DEGREE, name)


    def __str__(self):
        return super().__str__()