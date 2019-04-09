import copy


class GraphVertex:
    __type: str
    __name: str
    __properties: dict
    __uuid: str

    def __init__(self, vertextype, name):
        self.__type = vertextype
        self.__name =  name
        self.__uuid = name
        self.__properties = {}

    @property
    def uuid(self):
        return self.__uuid

    @uuid.setter
    def uuid (self, uuid):
        self.__uuid = uuid

    @property
    def type(self):
        return self.__type


    @property
    def label(self):
        return self.__type

    @property
    def name(self):
        return self.__name

    def setproperty(self, key: str, value: str):
        self.__properties[key] = value

    def getproperty(self, key):
        if key in self.__properties:
            return self.__properties[key]
        else:
            return None
    @property
    def properties(self):
        self.__properties['name'] = self.name
        self.__properties['uuid'] = self.uuid
        return self.__properties

    @properties.setter
    def properties(self, propertylist: dict):
        self.__properties = copy.deepcopy(propertylist)
        #Make sure that name and uuid is not changed
        self.__properties['name'] = self.name
        self.__properties['uuid'] = self.uuid

test = GraphVertex('ne', "NEW")
print(test)
