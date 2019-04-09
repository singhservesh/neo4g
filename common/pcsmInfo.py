from common.GraphVertex import GraphVertex as Vertex
from common.CommonStrings import CommonStrings as Strings
from common.controlinfo import ControlInfo as ControlInfo

class PcsmInfo:
    def __init__(self, type, name):
        self.pcsmName = name
        self.pcsmInfo = PcsmState
        self.pcsmType = type

class PcsmState:
    def __init__(self):
        self._lband = 'BLOCKED'
        self._cband = 'BLOCKED'
        self._name = "name" #name may not be needed, same as PcsmInfo

    @property
    def lbandState(self):
        return self._lband

    @lbandState.setter
    def lbandState(self,lband):
        self._lband = lband

    @property
    def cbandState(self):
        return self._lband

    @lbandState.setter
    def cbandState(self, lband):
        self._lband = lband

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

class GPcsmInfo( Vertex):
#How is SMC tied with PCSM info.

    def __init__(self, pcsmtype, pcsmid, lstate='BLOCKED', cstate='BLOCKED'):
        super().__init__(Strings.VTYPE_PCSMINFO, pcsmid)
        self.setproperty(Strings.G_LBAND_STATE, lstate)
        self.setproperty(Strings.G_CBAND_STATE, cstate)
        self.setproperty(Strings.G_PCSM_TYPE, pcsmtype)
        self.setproperty(Strings.G_PCSM_OWNER, "self")
        if cstate is not lstate:
            self.setproperty(Strings.G_PCSM_STATE, 'BLOCKED')

    @property
    def owner(self):
        return self.getproperty(Strings.G_PCSM_OWNER)

    @owner.setter
    def owner (self, owner):
        self.setproperty(Strings.G_PCSM_OWNER, owner)

    @property
    def lband(self):
        return self.getproperty(Strings.G_CBAND_STATE)

    @lband.setter
    def lband(self, lbandstate):
        self.setproperty(Strings.G_LBAND_STATE, lbandstate)
        cbandstate = self.getproperty(Strings.G_CBAND_STATE)
        if lbandstate is 'READY' and cbandstate is 'READY':
            self.setproperty(Strings.G_PCSM_STATE, 'READY')
        else:
            self.setproperty(Strings.G_PCSM_STATE, 'BLOCKED')

    @property
    def cband(self):
        return self.getproperty(Strings.G_CBAND_STATE)

    @cband.setter
    def lband(self, cbandstate):
        self.setproperty(Strings.G_CBAND_STATE, cbandstate)
        lbandstate = self.getproperty(Strings.G_LBAND_STATE)
        if lbandstate is 'READY' and cbandstate is 'READY':
            self.setproperty(Strings.G_PCSM_STATE, 'READY')
        else:
            self.setproperty(Strings.G_PCSM_STATE, 'BLOCKED')


    @property
    def state(self):
       return self.getproperty(Strings.G_PCSM_STATE)
