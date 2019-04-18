from common.GraphVertex import GraphVertex as Vertex
from common.Connection import Connection as Connection
from common.CommonStrings import CommonStrings as Strings



class ServiceRequest:
    def __init__(self, name, uuid='name'):
        self.name = name
        self.uuid = uuid
        self.smcs = []
        self.nmcs = []
        self.smca = None
        self.nmcas = []
        self.smcRel = []
        self.nmcRel = []
        self.tc  = []
        self.a = None
        self.z = None


class ConnectivityService (Vertex):
    __src: str
    __dst: str #TODO can be dict
    __connection: Connection
    def __init__(self, name):
        super().__init__(Strings.VTYPE_SERVICE, name)
        self.__connection = []
        print( "connection created")

    @property
    def connection(self):
        return self.__connection

    @connection.setter
    def connection(self, con):
        self.__connection.clear()
        for c in con:
            self.__connection.append(c)

    @property
    def source(self):
        return self.__src

    @source.setter
    def source(self, src):
        self.__src = src

    @property
    def destination(self):
        return self.__dst

    @source.setter
    def destination(self, dst):
        self.__dst = dst


class DirectedService ( Vertex):
    def __init__(self, name, source_sip):
        super().__init__(Strings.VTYPE_DIRSERVICE, name)
        self.setproperty(Strings.VPROP_SRCSIP, source_sip)
