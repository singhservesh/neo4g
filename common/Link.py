from common.GraphVertex import GraphVertex as GraphVertex
from common.CommonStrings import CommonStrings as Strings


class Link (GraphVertex):
    __src: str
    __dst: str

    def __init__(self,  srcNep, destNep, linkName: str):
        super().__init__(Strings.VTYPE_LINK, linkName)
        self.__src = srcNep
        self.__dst = destNep

    @property
    def src(self):
        return self.__src

    @src.setter
    def src(self, src):
        self.__src = src

    @property
    def dst(self):
        return self.__dst

    @dst.setter
    def dst(self, dst):
        self.__dst = dst

