from __future__ import annotations
from .browsedirection import BrowseDirection
from .nodeclassmask import NodeClassMask
from .epmobject import EpmObject
import collections

from typing import List, OrderedDict

class EpmModelObject(EpmObject):
    """
    Class representing an EPM Model Object.
    """

    def __init__(self, epmConnection, itemPath, path, name, type = ''):
        super().__init__(epmConnection, itemPath, path, name, type)

    # Public Methods
    def getParent(self) -> EpmModelObject:

        from .epmnodeids import EpmNodeIds
        from .itempathjson import ItemPathJSON
        parentObjects = collections.OrderedDict()
        hasComponentResult = self._epmConnection._browse([self._itemPath], EpmNodeIds.HasComponent.value, NodeClassMask.Object, BrowseDirection.Inverse).references()[0]
        #organizesResult = self._epmConnection._browse([self._itemPath], EpmNodeIds.Organizes.value).references()[0]
        result = hasComponentResult[0] #+ organizesResult
        #if len(result) < 1:
        #    return None
        
        #identities = [ItemPathJSON('OPCUA.NodeId', '', item._identity) for item in hasComponentResult]
        identity = ItemPathJSON('OPCUA.NodeId', '', result._identity)
        typesResults = self._epmConnection._browse([identity], EpmNodeIds.HasTypeDefinition.value).references()

        #for index in range(0, len(hasComponentResult)):
        if result._nodeClass == 4:  # Method is ignored
            return None
        return EpmModelObject(self._epmConnection, identity,
                                                    self._path + '/' + result._displayName, result._displayName,
                                                    typesResults[0][0]._displayName)

        return parentObjects



    def enumObjects(self) -> collections.OrderedDict:
        """
        :return: An Ordered Dictionary with all child objects from this object.
        :rtype: collections.OrderedDict[EpmModelObject]
        """
        from .epmnodeids import EpmNodeIds
        from .itempathjson import ItemPathJSON
        childObjects = collections.OrderedDict()
        hasComponentResult = self._epmConnection._browse([self._itemPath], EpmNodeIds.HasComponent.value).references()[0]
        organizesResult = self._epmConnection._browse([self._itemPath], EpmNodeIds.Organizes.value).references()[0]
        result = hasComponentResult + organizesResult
        if len(result) < 1:
            return childObjects
        
        identities = [ItemPathJSON('OPCUA.NodeId', '', item._identity) for item in result]
        typesResults = self._epmConnection._browse(identities, EpmNodeIds.HasTypeDefinition.value).references()

        for index in range(0, len(result)):
            if result[index]._nodeClass == 4:  # Method is ignored
                continue
            childObjects[result[index]._displayName] = EpmModelObject(self._epmConnection, identities[index],
                                                        self._path + '/' + result[index]._displayName, result[index]._displayName,
                                                        typesResults[index][0]._displayName)

        return childObjects


    def addInstances(self, names:List[str], objTypes:List[str]) -> OrderedDict[str, EpmObject]:
        """
        Adds new instances to the current object.

        :param names: A List with new instance names.
        :type names: List[str]
        :param objTypes: A List with object types.
        :type objTypes: List[str]
        :return: An Ordered Dictionary with all objects created.
        :rtype: collections.OrderedDict[EpmObject]
        """
        splitPath = self._path.split("/")

        if splitPath[0] == "":
            addPath = "/".join(splitPath[3:])
        else:
            addPath = "/".join(splitPath[2:])

        return self._epmConnection._addInstancesEpmModel(addPath, names, objTypes)

    def addReference(self, obj:EpmObject) -> bool:
        """
        Adds object reference to the current object.

        :param obj: The object to be referenced.
        :type obj: EpmObject
        :return: True / False depending of the operation result.
        :rtype: bool
        """
        splitPath = self._path.split("/")

        if splitPath[0] == "":
            addPath = "/".join(splitPath[3:])
        else:
            addPath = "/".join(splitPath[2:])

        return self._epmConnection._addReferencesEpmModel(addPath, obj)

    def removeInstance(self, name:str):
        """
        Removes a child object from this object.

        :param name: Name of an object to remove.
        :type name: str
        """
        splitPath = self._path.split("/")

        if splitPath[0] == "":
            removePath = "/".join(splitPath[3:]) + "/" + name
        else:
            removePath = "/".join(splitPath[2:]) + "/" + name

        if removePath[0] == "/":
            removePath = removePath[1:]

        self._epmConnection._removeInstanceEpmModel(removePath)


    def setBindedVariables(self, aliasProperties:List[str], variablesNames:List[str]):
        """
        Sets the bind variable from a list of Alias Properties.

        :param aliasProperties: List with Alias Properties.
        :type aliasProperties: List[str]
        :param variablesNames: List of Data Objects to bind.
        :type variablesNames: List[str]
        """
        splitPath = self._path.split("/")

        if splitPath[0] == "":
            objectPath = "/".join(splitPath[3:])
        else:
            objectPath = "/".join(splitPath[2:])

        self._epmConnection._setBindedVariables(objectPath, aliasProperties, variablesNames, True)


class ObjectDependenciesException(Exception):
    pass


class InstanceNameDuplicatedException(Exception):
    pass


class InvalidObjectNameException(Exception):
    pass


class InvalidSourceVariableException(Exception):
    pass


class InvalidObjectTypeException(Exception):
    pass


class InvalidObjectPropertyException(Exception):
    pass
