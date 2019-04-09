from common.GraphVertex import GraphVertex as vertex
#from common.CommonStrings import CommonStrings as Strings


class GraphEdge:
    _label: str
    _type: str
    properties: dict
    _outvertex: vertex
    _invertextype: str
    _invertexkey: str
    _invertexkeyvalue: str
    _overtextype: str
    _overtexkey: str
    _overtexkeyvalue: str

    def __init__(self, label, out: vertex, itype, ikey, ivalue):
        self._outvertex = out
        self._invertexkey = ikey
        self._invertextype = itype
        self._invertexkeyvalue = ivalue
        self._label = ""
        self.properties = {}

    def __init__(self, label, otype, okey, ovalue, itype, ikey, ivalue):
        self._invertexkey = ikey
        self._invertextype = itype
        self._invertexkeyvalue = ivalue
        self._overtexkey = okey
        self._overtextype = otype
        self._overtexkeyvalue = ovalue
        self._label = ""
        self.properties = {}

    @property
    def invertexkey(self):
        return self._invertexkey

    @property
    def invertexkeyvalue(self):
        return self._invertexkeyvalue

    @property
    def invertextype(self):
        return self._invertextype

    @property
    def overtexkey(self):
        return self._overtexkey

    @property
    def overtexkeyvalue(self):
        return self._overtexkeyvalue

    @property
    def overtextype(self):
        return self._overtextype


test = GraphEdge('newEdge', 'degree', 'name', 'degree-1', 'ila', 'uuid', '32332')
print(test)
print(test.invertextype + " \n " + test.invertexkey + " \n " + test.invertexkeyvalue)
print(test.overtextype + " \n " + test.overtextype + " \n " + test.overtexkeyvalue)
print(test.properties)
