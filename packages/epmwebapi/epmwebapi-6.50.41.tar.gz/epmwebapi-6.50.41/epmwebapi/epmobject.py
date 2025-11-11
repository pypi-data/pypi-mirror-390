from .epmdataobject import EpmDataObject
from .itempathjson import ItemPathJSON
from .epmproperty import EpmProperty
from .epmnodeids import EpmNodeIds

import collections

from typing import OrderedDict


class EpmObject(object):
    """
    Class representing an EPM Object.
    """

    def __init__(self, epmConnection, itemPath, path, name, type = ''):
        self._epmConnection = epmConnection
        self._itemPath = itemPath
        self._path = path
        self._type = type
        self._name = name

    # Public Methods
    def enumObjects(self) -> collections.OrderedDict:
        """
        :return: An Ordered Dictionary with all child objects from this object.
        :rtype: collections.OrderedDict[EpmObject]
        """
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
            childObjects[result[index]._displayName] = EpmObject(self._epmConnection, identities[index],
                                                        self._path + '/' + result[index]._displayName, result[index]._displayName,
                                                        typesResults[index][0]._displayName)

        return childObjects

    def enumProperties(self) -> OrderedDict[str, EpmProperty]:
        """
        :return: An Ordered Dictionary with all Properties from this object.
        :rtype: collections.OrderedDict[EpmProperty]
        """
        result = self._epmConnection._browse([ self._itemPath ], EpmNodeIds.HasProperty.value)
        childProperties = collections.OrderedDict()
        for item in result.references()[0]:
            childProperties[item._displayName] = EpmProperty(self._epmConnection, item._displayName, self._path + '/' + item._displayName, ItemPathJSON('OPCUA.NodeId', '', item._identity))
        return childProperties

    # Public Properties

    @property
    def name(self) -> str:
        """
        :return: Name of this object.
        :rtype: str
        """
        return self._name

    @property
    def path(self) -> str:
        """
        :return: Path of this object.
        :rtype: str
        """
        return self._path

    @property
    def itemPath(self) -> ItemPathJSON:
        """
        :return: ItemPath of this object.
        :rtype: ItemPathJSON
        """
        return self._itemPath

    @property
    def type(self) -> str:
        """
        Returns or sets the type of this object.

        :param value: Name for the type of this object.
        :type value: str
        """
        return self._type

    @type.setter
    def type(self, value:str):
        self._type = value

