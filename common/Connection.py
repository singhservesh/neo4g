from common.CommonStrings import CommonStrings as Strings
from common.GraphVertex import GraphVertex as vertex



from common.Node import Roadm as Roadm
from common.Topology import Topology as Topology
from common.GraphVertex import GraphVertex as Vertex
from common.Node import Degree as degree
from common.Node import Ila as Ila
from common.tls import TLS as TLS
from common.NodeEdgePoint import NodeEdgePoint as Nep
from common.Node import Node as node
from neo4j import exceptions as neo4jexceptions
from common.pcsmInfo import PcsmState as PcsmState
from common.pcsmInfo import GPcsmInfo as GPcsmInfo
from common.tlsstate import TlsState as TlsState
from common.pcsmInfo import PcsmInfo as Pcsm


class MediaChannel (vertex):
    def __init__(self, type, name):
        super().__init__(type, name)
        self.setproperty('service-layer','PHOTONIC-MEDIA')
        self.setproperty('service-layer-qualifier', 'PHOTONIC_LAYER_QUALIFIER_' + type)
        self.setproperty('service-type', 'POINT_TO_POINT_CONNECTIVITY')
        self.setproperty('connectivity-direction', 'UNIDIRECTION')

    def addUserLink(self,link):
        self.setproperty('userlink', link)


class Connection (vertex):
    def __init__(self):
        super().__init__('connection', 'conn-uid')
        print("connection created")


class Smc(MediaChannel):
    def __init__(self, name, lf="0", uf="0"):
        super().__init__(Strings.VTYPE_SMC, name)
        self.setproperty(Strings.VPROP_UPPERFQ, uf)
        self.setproperty(Strings.VPROP_LOWERFQ, lf)


    @property
    def lf(self):
        return self.getproperty(Strings.VPROP_LOWERFQ)

    @lf.setter
    def lf(self,lf):
        self.setproperty(Strings.VPROP_LOWERFQ, lf)

    @property
    def uf(self):
        return self.getproperty(Strings.VPROP_UPPERFQ)

    @uf.setter
    def uf(self, uf):
        self.setproperty(Strings.VPROP_UPPERFQ, uf)

    def setluf(self, lf, uf):
        self.setproperty(Strings.VPROP_UPPERFQ, uf)
        self.setproperty(Strings.VPROP_LOWERFQ, lf)


class SmcA(MediaChannel):
    def __init__(self, name):
        super().__init__(Strings.VTYPE_SMCA, name)


class Nmc(MediaChannel):
    def __init__(self, name, lf="0", uf="0"):
        super().__init__(Strings.VTYPE_NMC, name)
        self.setproperty(Strings.VPROP_UPPERFQ, uf)
        self.setproperty(Strings.VPROP_LOWERFQ, lf)

    @property
    def lf(self):
        return self.getproperty(Strings.VPROP_LOWERFQ)

    @lf.setter
    def lf(self, lf):
        self.setproperty(Strings.VPROP_LOWERFQ, lf)

    @property
    def uf(self):
        return self.getproperty(Strings.VPROP_UPPERFQ)

    @uf.setter
    def uf(self, uf):
        self.setproperty(Strings.VPROP_UPPERFQ, uf)

    def setluf(self, lf, uf):
        self.setproperty(Strings.VPROP_UPPERFQ, uf)
        self.setproperty(Strings.VPROP_LOWERFQ, lf)

class NmcA(MediaChannel):
    def __init__(self, name):
        super().__init__(Strings.VTYPE_NMCA, name)


class Sip(Vertex):
    def __init__(self, name):
        super().__init__(Strings.VTYPE_SIP, name)

