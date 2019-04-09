from common.GraphVertex import GraphVertex as GrVtx
from common.CommonStrings import CommonStrings as Strings

class ControlInfo (GrVtx):
    def __init__(self, ctrlname):
        super().__init__(Strings.VTYPE_CONTROLINFO, ctrlname)


