from common.Connection import Nmc as Nmc
from common.Connection import NmcA as NmcA
from common.Connection import Smc as Smc
from common.Connection import SmcA as SmcA

class Csep :
    def __init__(self, name, startsip, endsip, lf, uf):
        self.startsip = startsip
        self.endsip = endsip
        self.uf = uf
        self.lf = lf
        self.name = name

class MediaChannel:
    def __init__(self, qfr, useLink, csep:Csep):
        self.servicelayer = 'PHONONIC_MEDIA'
        self.slQualifier = qfr
        self.svcType = 'PointToPoint'
        self.direction = 'BD'
        self.UseLink = useLink
        self.csep = csep

class C1:
    def __init__(self, name):
        self.uuid = name
        self.name = name
        self.smca:MediaChannel = None
        self.nmca:MediaChannel = None
        self.smc:MediaChannel = []
        self.nmc:MediaChannel = []

    def AddSmcA(self, smca: MediaChannel):
        self.smca = smca

    def AddSmc(self, smc: MediaChannel):
        self.smca.append(smc)

    def AddNmcA(self, nmca: MediaChannel):
        self.nmca = nmca

    def AddNmc(self, nmc: MediaChannel):
        self.nmc.append(nmc)
