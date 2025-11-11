import ctypes
from logging import root
import os
from urllib import response

import numpy as np
import requests
import json

from .typeevent import TypeEvent
from .advancedevent import AdvancedEvent

from .simpleattributeoperand import SimpleAttributeOperand

from .eventfiltermodel import EventFilterModel
from .historyeventmodeljson import HistoryEventModelJSON

from .elementoperand import ElementOperand

from .queryfiltercontent import QueryFilterContent

from .epmmodelobject import EpmModelObject, ObjectDependenciesException, InstanceNameDuplicatedException, InvalidObjectNameException, InvalidSourceVariableException, InvalidObjectTypeException, InvalidObjectPropertyException
from .epmproperty import EpmProperty
from .queryperiod import QueryPeriod
from .aggregatedetails import AggregateDetails
from .aggregatedetails import AggregateType
from .datavaluejson import DataValueJSON
from .annotationvaluejson import AnnotationValueJSON
from .itempathjson import ItemPathJSON
from .browsemodeljson import BrowseModelJSON
from .browseresultmodeljson import BrowseResultModelJSON
from .browseitemmodeljson import BrowseItemModelJSON
from .browseresultitemmodeljson import BrowseResultItemModelJSON
from .historyupdatedatamodeljson import HistoryUpdateDataModelJSON
from .historyupdatedataitemmodeljson import HistoryUpdateDataItemModelJSON
from .readitemmodeljson import ReadItemModelJSON
from .readmodeljson import ReadModelJSON
from .readresultitemmodeljson import ReadResultItemModelJSON
from .readresultmodeljson import ReadResultModelJSON
from .epmdataobject import EpmDataObject, EpmDataObjectPropertyNames, EpmDataObjectAttributeIds, getDiscreteValue, \
    getDomainValue
from .epmobject import EpmObject
from .basicvariable import BasicVariable, BasicVariableAlreadyExistsException, BasicVariableInvalidNameException, \
    StorageSetDoesNotExistException, InterfaceDoesNotExistException
from .writeitemmodeljson import WriteItemModelJSON
from .writemodeljson import WriteModelJSON
from .itempathandcontinuationpointjson import ItemPathAndContinuationPointJSON
from .historyrawmodeljson import HistoryRawModelJSON
from .numpyextras import NumpyExtras
from .historyprocessedmodeljson import HistoryProcessedModelJSON
from .authorizationservice import AuthorizationService
from .querymodeljson import QueryModelJSON
from .querymodelfilterJSON import QueryModelFilterJSON
from .queryresultmask import QueryResultMask
from .queryresultitemmodeljson import QueryResultItemModelJSON
from .diagnosticmodeljson import DiagnosticModelJSON
from .dataobjectattributes import DataObjectAttributes
from .epmnodeids import EpmNodeIds
from .nodeclassmask import NodeClassMask
from .browsedirection import BrowseDirection
from .dataobjectsfilter import DataObjectsFilterType, DataObjectsFilter
from .domainfilter import DomainFilter
from .nodeattributes import NodeAttributes
from .portalresources import PortalResources
from .processorresources import ProcessorResources
from .historyupdatetype import HistoryUpdateType
from .customtypedefinition import CustomTypeDefinition, SimpleProperty, ObjectProperty, \
    CustomTypeAlreadyExistsException, InvalidCustomTypeNameException, CustomTypeDependenciesException, \
    InvalidIconException, DuplicatedPropertiesNamesException, DuplicatedPropertiesTypeException, \
    InvalidPropertyNameException, MissingPropertyNameException, InvalidPropertyTypeException
from .datasetconfig import DatasetConfig, DatasetConfigLocal, DatasetConfigServer
from enum import Enum
import collections
from .epmconnectioncontext import EpmConnectionContext
from .basicvariable import TagType
from .epmvariable import EpmVariable
import datetime as dt

from typing import Any, Union, List, OrderedDict, Tuple


class ImportMode(Enum):
    """
    Enumeration with all types of import modes.
    """
    OnlyAdd = 0
    OnlyEdit = 1
    AddAndEdit = 2


class EpmConnection(object):
    """
    Class representing an **EPM** Connection.
    """

    def __init__(self, authServer:str=None, webApi:str=None, userName:str=None, password:str=None, clientId:str='EpmRestApiClient',
                 programId:str='B39C3503-C374-3227-83FE-EEA7A9BD1FDC', connectionContext:EpmConnectionContext=None):
        """
        Class constructor.

        :param authServer: An optional URL to an authorization server. Default is **None**.
        :type authServer: str
        :param webApi: An optional URL to a Web API. Default is **None**.
        :type webApi: str
        :param userName: An optional name of a user to access an **EPM Server**. Default is **None**.
        :type userName: str
        :param password: An optional password of a user to access an **EPM Server**. Default is **None**.
        :type password: str
        :param clientId: An optional client identity to access an **EPM Server**. Default is `EpmRestApiClient`.
        :type clientId: str
        :param programId: An optional program identity to access an **EPM Server**. Default is `B39C3503-C374-3227-83FE-EEA7A9BD1FDC`.
        :type programId: str
        :param connectionContext: An optional `epmwebapi.epmconnectioncontext.EpmConnectionContext` to create a new Connection. Default is **None**.
        :type connectionContext: epmwebapi.epmconnectioncontext.EpmConnectionContext
        """
        self._dataObjectsCache = {}
        if connectionContext is not None:
          self._webApi = connectionContext.getWebApi()
          self._authorizationService = AuthorizationService(connectionContext)
        else:
          self._webApi = webApi
          from .epmconnectioncontext import EpmConnectionContext
          self._authorizationService = AuthorizationService(EpmConnectionContext(authServer, webApi, clientId, programId, userName, password))

    # Public Methods
    def getPortalResourcesManager(self) -> PortalResources:
        """
        Gets an `epmwebapi.portalresources.PortalResources` object to manage resources from **EPM Portal**.

        :return: A class representing an **EPM Portal** Resources Manager.
        :rtype: epmwebapi.portalresources.PortalResources
        """
        return PortalResources(self._authorizationService, self._webApi)

    def getProcessorResourcesManager(self) -> ProcessorResources:
        """
        Gets an `epmwebapi.processorresources.ProcessorResources` object to manage resources from **EPM Processor**.

        :return: A class representing an **EPM Processor** Resources Manager.
        :rtype: epmwebapi.processorresources.ProcessorResources
        """
        return ProcessorResources(self._authorizationService, self._webApi)

    def getDataObjects(self, names:str=None, attributes:DataObjectAttributes=DataObjectAttributes.Unspecified) -> OrderedDict[str, EpmDataObject]:
        """
        Returns an Ordered Dictionary (`collections.OrderedDict`) object with one or more Data Objects. If a name does not exist, this function returns **None** as the Data Object's value.

        :param names: Names of Data Objects. Default is **None**.
        :type names: str
        :param attributes: Attributes to return from Data Objects. Default is `epmwebapi.dataobjectattributes.DataObjectAttributes.Unspecified`.
        :type attributes: epmwebapi.dataobjectattributes.DataObjectAttributes
        :return: An Ordered Dictionary (`collections.OrderedDict`) object with all Data Objects found on an **EPM Server** with the specified attributes.
        :rtype: collections.OrderedDict
        """
        if names is None:
            return self._getAllDataObjects(attributes, EpmNodeIds.HasComponent)
        else:
            return self._getDataObjects(names, attributes)

    def getBasicVariables(self, names:str=None, attributes:DataObjectAttributes=DataObjectAttributes.Unspecified) -> OrderedDict[str, EpmDataObject]:
        """
        Returns an Ordered Dictionary (`collections.OrderedDict`) object with one or more Basic Variables. If a name does not exists, this function returns **None** as the Basic Variable's value.

        :param names: Names of Basic Variables.
        :type names: str
        :param attributes: Attributes to return from Basic Variables. Default is `epmwebapi.dataobjectattributes.DataObjectAttributes.Unspecified`.
        :type attributes: epmwebapi.dataobjectattributes.DataObjectAttributes.Unspecified
        :return: An Ordered Dictionary (`collections.OrderedDict`) object with all Basic Variables found on an **EPM Server** with the specified attributes.
        :rtype: collections.OrderedDict
        """
        if names is None:
            return self._getAllDataObjects(attributes, EpmNodeIds.HasTags, '/1:BasicVariables')
        else:
            return self._getDataObjects(names, attributes, '/1:BasicVariables')

    def getExpressionVariables(self, names:str=None, attributes:DataObjectAttributes=DataObjectAttributes.Unspecified) -> OrderedDict[str, EpmDataObject]:
        """
        Returns an Ordered Dictionary (`collections.OrderedDict`) object with one or more Expression Variables. If a name does not exist, this function returns **None** as the Expression Variable's object.

        :param names: Names of Expression Variables.
        :type names: str
        :param attributes: Attributes to return from Expression Variables. Default is `epmwebapi.dataobjectattributes.DataObjectAttributes.Unspecified`.
        :type attributes: epmwebapi.dataobjectattributes.DataObjectAttributes.Unspecified
        :return: An Ordered Dictionary (`collections.OrderedDict`) object with all Expression Variables found on an **EPM Server** with the specified attributes.
        :rtype: collections.OrderedDict
        """
        if names is None:
            return self._getAllDataObjects(attributes, EpmNodeIds.HasComponent, '/1:ExpressionVariables')
        else:
            return self._getDataObjects(names, attributes, '/1:ExpressionVariables')

    def createBasicVariable(self, name:str, description:str=None, tagType:Union[str,TagType]=None, realTimeEnabled:bool=None, deadBandFilter:float=None,
                            deadBandUnit:str=None,
                            eu:str=None, lowLimit:float=None, highLimit:float=None, scaleEnable:bool=None, inputLowLimit:float=None,
                            inputHighLimit:float=None, clamping:str=None,
                            domain:str=None, interface:str=None, ioTagAddress:str=None, processingEnabled:bool=None, isRecording:bool=None,
                            isCompressing:bool=None,
                            storeMillisecondsEnabled:bool=None, storageSet:bool=None) -> BasicVariable:
        """
        Creates a Basic Variable on an **EPM Server**.

        :param name: Optional parameter indicating a name for this Basic Variable. Default is **None**.
        :type name: str
        :param description: Optional parameter indicating a description for this Basic Variable. Default is **None**.
        :type description: str
        :param tagType: Optional parameter indicating a type of Tag of a Basic Variable. Possible values are **SourceType**, **Bit**, **Int**, **UInt**, **Float**, **Double**, **String**, or **DateTime**. Default is **None**.
        :type tagType: Union[str, epmwebapi.basicvariable.TagType]
        :param realTimeEnabled: Optional parameter indicating whether real-time is enabled. Default is **None**.
        :type realTimeEnabled: bool
        :param deadBandFilter: Optional parameter indicating a dead band value. Default is **None**.
        :type deadBandFilter: float
        :param deadBandUnit: Optional parameter indicating a dead band unit. Default is **None**.
        :type deadBandUnit: str
        :param eu: Optional parameter indicating an engineering unit. Default is **None**.
        :type eu: str
        :param lowLimit: Optional parameter indicating a low limit. Default is **None**.
        :type lowLimit: float
        :param highLimit: Optional parameter indicating a high limit. Default is **None**.
        :type highLimit: float
        :param scaleEnable: Optional parameter indicating whether scale is enabled or not. Default is **None**.
        :type scaleEnable: bool
        :param inputLowLimit: Optional parameter indicating an input low limit. Default is **None**.
        :type inpuLowLimit: float
        :param inputRightLimit: Optional parameter indicating an input right limit. Default is **None**.
        :type inputRightLimit: float
        :param clamping: Optional parameter indicating a type of clamping. Possible values are *ClampToRange* or *Discard*. Default is **None**.
        :type clamping: str
        :param domain: Optional parameter indicating a domain from a variable. Possible values are **Continuous** or **Discrete**. Default is **None**.
        :type domain: str
        :param interface: Optional parameter indicating the name of an Interface, in the format **InterfaceServerName\\interfacename**. Default is **None**.
        :type interface: str
        :param ioTagAddress: Optional parameter indicating the Interface's source path. Default is **None**.
        :type ioTagAddress: str
        :param processingEnabled: Optional parameter indicating whether scale is enabled or not. Default is **None**.
        :type processingEnabled: bool
        :param isRecording: Optional parameter indicating whether recording values is enabled or not. Default is **None**.
        :type isRecording: bool
        :param isCompressing: Optional parameter indicating whether compression values is enabled or not. Default is **None**.
        :type isCompressing: bool
        :param storeMillisecondsEnabled: Optional parameter indicating whether storing milliseconds from timestamp values is enabled or not. Default is **None**.
        :type storeMillisecondsEnabled: bool
        :param storageSet: Optional Storage Set name. Default is **None**.
        :type storageSet: bool
        :return: An `epmwebapi.basicvariable.BasicVariable` object.
        :rtype: epmwebapi.basicvariable.BasicVariable
        :raises: Basic Variable already exists.
        :raises: Basic Variable contains an invalid name.
        :raises: Storage Set does not exist.
        :raises: Interface does not exist.
        """

        url = self._webApi + '/epm/v1/BV'

        discrete = getDiscreteValue(domain)

        bvType = None
        if tagType is not None:
            bvType = tagType if isinstance(tagType, str) else tagType.name if isinstance(tagType, TagType) else TagType(tagType).name

        jsonRequest = {'Items': [{'name': name, 'description': description if description is not None else '',
                                  'tagType': bvType, 'realTimeEnabled': realTimeEnabled,
                                  'eu': eu, 'lowLimit': lowLimit, 'highLimit': highLimit, 'scaleEnable': scaleEnable,
                                  'inputLowLimit': inputLowLimit, 'inputHighLimit': inputHighLimit,
                                  'rangeClamping': clamping,
                                  'discrete': discrete, 'interface': interface, 'ioTagAddress': ioTagAddress,
                                  'processingEnabled': processingEnabled,
                                  'isRecording': isRecording, 'isCompressing': isCompressing,
                                  'storeMillisecondsEnabled': storeMillisecondsEnabled,
                                  'storageSet': storageSet, 'deadBandFilter': deadBandFilter,
                                  'deadBandUnit': deadBandUnit}]}

        session = self._authorizationService.getEpmSession()
        response = session.post(url, json=jsonRequest, verify=False)
        if response.status_code != 200:
            if response.status_code == 400:
                if 'EpmErrorTagAlreadyExists' in response.text:
                    raise BasicVariableAlreadyExistsException('BasicVariable ' + name + ' already exists')
                if 'Invalid format Name' in response.text:
                    raise BasicVariableInvalidNameException('BasicVariable ' + name + ' has an invalid format')
                if 'Invalid StorageSet name' in response.text:
                    raise StorageSetDoesNotExistException('StorageSet ' + str(storageSet) + ' does not exists')
                if 'Invalid Interface name' in response.text:
                    raise InterfaceDoesNotExistException('Interface path ' + str(interface) + ' does not exists')
            raise Exception(
                "CreateBasicVariable call error + '" + str(response.status_code) + "'. Reason: " + response.reason)

        json_result = json.loads(response.text)

        bvInfo = json_result['items'][0]

        itemPath = ItemPathJSON('OPCUA.NodeId', None, 'ns=1;i=' + str(bvInfo['id']))

        bv = BasicVariable(self, itemPath=itemPath, name=bvInfo['name'], description=bvInfo['description'],
                           deadBandFilter=bvInfo['deadBandFilter'], deadBandUnit=bvInfo['deadBandUnit'],
                           eu=bvInfo['eu'], lowLimit=bvInfo['lowLimit'], highLimit=bvInfo['highLimit'],
                           tagType=bvInfo['tagType'], realTimeEnabled=bvInfo['realTimeEnabled'],
                           scaleEnable=bvInfo['scaleEnable'],
                           inputLowLimit=bvInfo['inputLowLimit'], inputHighLimit=bvInfo['inputHighLimit'],
                           clamping=bvInfo['rangeClamping'],
                           domain=getDomainValue(bvInfo['discrete']), interface=bvInfo['interface'],
                           ioTagAddress=bvInfo['ioTagAddress'],
                           processingEnabled=bvInfo['processingEnabled'], isRecording=bvInfo['isRecording'],
                           isCompressing=bvInfo['isCompressing'],
                           storeMillisecondsEnabled=bvInfo['storeMillisecondsEnabled'], storageSet=bvInfo['storageSet'])

        return bv

    def updateBasicVariable(self, name:str, newName:str=None, description:str=None, tagType:Union[str,TagType]=None, realTimeEnabled:bool=None, deadBandFilter:float=None,
                            deadBandUnit:str=None,
                            eu:str=None, lowLimit:float=None, highLimit:float=None, scaleEnable:bool=None, inputLowLimit:float=None,
                            inputHighLimit:float=None, clamping:str=None,
                            domain:str=None, interface:str=None, ioTagAddress:str=None, processingEnabled:bool=None, isRecording:bool=None,
                            isCompressing:bool=None,
                            storeMillisecondsEnabled:bool=None, storageSet:bool=None):
        """
        Updates a Basic Variable. Parameters set as **None** are not updated.

        :param name: Name of a Basic Variable to update.
        :type name: str
        :param newName: An optional new name for a Basic Variable.
        :type newName: str
        :param description: An optional description to update.
        :type description: str
        :param tagType: An optional type of Tag to update. Possible values are **SourceType**, **Bit**, **Int**, **UInt**, **Float**, **Double**, **String**, or **DateTime**. Default is **None**.
        :type tagType: epmwebapi.basicvariable.TagType
        :param realtimeEnabled: Optional parameter indicating whether real-time is enabled or not. Default is **None**.
        :type realtimeEnabled: bool
        :param deadBandFilter: Optional parameter indicating a dead band value. Default is **None**.
        :type deadBandFilter: float
        :param deadBandUnit: Optional parameter indicating a dead band unit. Possible values are **Absolute**, **PercentOfEURange**, or **PercentOfValue**. Default is **None**.
        :type deadBandUnit: str
        :param eu: Optional parameter indicating an engineering unit for the Basic Variable. Default is **None**.
        :type eu: str
        :param lowLimit: Optional parameter indicating a low limit. Default is **None**.
        :type lowLimit: float
        :param highLimit: Optional parameter indicating a high limit. Default is **None**.
        :type highLimit: float
        :param scaleEnable: Optional parameter indicating whether a scale is enabled. Default is **None**.
        :type scaleEnable: bool
        :param inputLowLimit: Optional parameter indicating an input low limit. Default is **None**.
        :type inputLowLimit: float
        :param inputHighLimit: Optional parameter indicating an input high limit. Default is **None**.
        :type inputHighLimit: float
        :param clamping: Optional parameter indicating a type of clamping. Possible values are **ClampToRange** or **Discard**. Default is **None**.
        :type clamping: str
        :param domain: Optional parameter indicating a domain from a variable. Possible values are **Continuous** or **Discrete**. Default is **None**.
        :type domain: str
        :param interface: Optional parameter indicating an Interface name, in the format **interfaceServerName\\interfaceName**. Default is **None**.
        :type interface: str
        :param ioTagAddress: Optional parameter indicating  the Interface's source path. Default is **None**.
        :type ioTagAddress: str
        :param processingEnabled: Optional parameter indicating whether a scale is enabled. Default is **None**.
        :type processingEnabled: bool
        :param isRecording: Optional parameter indicating whether recording values is enabled or not. Default is **None**.
        :type isRecording: bool
        :param isCompressing: Optinal parameter indicating whether compressing values is enabled or not. Default is **None**.
        :type isCompressing: bool
        :param storeMillisecondsEnabled: Optional parameter indicating whether storing milliseconds from timestamp values. Default is **None**.
        :type storeMillisecondsEnabled: bool
        :param storageSet: Optional Storage Set name. Default is **None**.
        :type storageSet: bool
        :raises: Basic Variable already exists.
        :raises: Invalid name of Basic Variable.
        :raises: Storage Set does not exist.
        :raises: Interface does not exist.
        """

        url = self._webApi + '/epm/v1/BV'

        discrete = getDiscreteValue(domain)

        jsonRequest = {'Items': [{'name': name, 'newName': newName, 'description': description,
                                  'tagType': tagType, 'realTimeEnabled': realTimeEnabled,
                                  'eu': eu, 'lowLimit': lowLimit, 'highLimit': highLimit, 'scaleEnable': scaleEnable,
                                  'inputLowLimit': inputLowLimit, 'inputHighLimit': inputHighLimit,
                                  'rangeClamping': clamping,
                                  'discrete': discrete, 'interface': interface, 'ioTagAddress': ioTagAddress,
                                  'processingEnabled': processingEnabled,
                                  'isRecording': isRecording, 'isCompressing': isCompressing,
                                  'storeMillisecondsEnabled': storeMillisecondsEnabled,
                                  'storageSet': storageSet, 'deadBandFilter': deadBandFilter,
                                  'deadBandUnit': deadBandUnit}]}

        session = self._authorizationService.getEpmSession()
        response = session.patch(url, json=jsonRequest, verify=False)
        if response.status_code != 200:
            if response.status_code == 400:
                if 'EpmErrorTagAlreadyExists' in response.text:
                    raise BasicVariableAlreadyExistsException('BasicVariable ' + name + ' already exists')
                if 'Invalid format Name' in response.text:
                    raise BasicVariableInvalidNameException('BasicVariable ' + name + ' has an invalid format')
                if 'Invalid StorageSet name' in response.text:
                    raise StorageSetDoesNotExistException('StorageSet ' + str(storageSet) + ' does not exists')
                if 'Invalid Interface name' in response.text:
                    raise InterfaceDoesNotExistException('Interface path ' + str(interface) + ' does not exists')
            raise Exception(
                "UpdateBasicVariable call error + '" + str(response.status_code) + "'. Reason: " + response.reason)

    def deleteBasicVariable(self, names:List[str]) -> Union[bool,List[bool]]:
        """
        Deletes one or more Basic Variables.

        :param names: A list of Basic Variables to delete.
        :type names: List[str]
        :return: `True` if the Basic Variables were deleted.
        :rtype: Union[bool,List[bool]]
        """

        url = self._webApi + '/epm/v1/BV'

        jsonRequest = {'Items': names}

        session = self._authorizationService.getEpmSession()
        response = session.delete(url, json=jsonRequest, verify=False)
        if response.status_code != 200:
            raise Exception(
                "DeleteBasicVariable call error + '" + str(response.status_code) + "'. Reason: " + response.reason)

        json_result = json.loads(response.text)

        if 'diagnostics' in json_result:
            return [True if item == 1 else False for item in json_result['diagnostics']]
        else:
            return True

    def getAllCustomTypes(self) -> List[str]:
        """
        Returns all existing custom types on an **EPM Server**.

        :return: A list of all custom types of an **EPM Server**.
        :rtype: List[str]
        :raises: A call error.
        """
        url = self._webApi + '/epm/v1/usertypes'

        session = self._authorizationService.getEpmSession()
        response = session.get(url, verify=False)

        if response.status_code != 200:
            raise Exception("GetAllCustomTypes call error '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        types_list = json.loads(response.text)

        return types_list

    def getCustomType(self, name:str) -> CustomTypeDefinition:
        """
        Returns a specific custom type.

        :param name: Name of a custom type.
        :type name: str
        :return: An `epmwebapi.customtypedefinition.CustomTypeDefinition` object.
        :rtype: epmwebapi.customtypedefinition.CustomTypeDefinition
        :raises: Invalid custom type name.
        :raises: Bad argument.
        :raises: Custom type not found.
        :raises: Cannot parse a path with informed name.
        """
        url = self._webApi + '/epm/v1/usertypes/' + name

        session = self._authorizationService.getEpmSession()
        response = session.get(url, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2158690304:
                    raise InvalidCustomTypeNameException('Custom type ' + name + ' not found')
                elif responseCode == 2151022592:
                    raise BadArgumentException('Cannot parse path with name ' + name)
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("GetCustomType call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        json_response = json.loads(response.text)['item']

        icon = json_response["icon"]

        aliasProperties = []
        for dic in json_response["aliasProperties"]:
            aliasProperties.append(dic.get('name'))

        simpleProperties = []
        for dic in json_response["simpleProperties"]:
            simple = SimpleProperty(dic.get('name'), dic.get('initialValue'))
            simpleProperties.append(simple)

        objectProperties = []
        for dic in json_response["objectProperties"]:
            obj = ObjectProperty(dic.get('name'), dic.get('type'))
            objectProperties.append(obj)

        placeHolderTypes = []
        for dic in json_response["placeHolderProperties"]:
            placeHolder = dic.get('type')
            placeHolderTypes.append(placeHolder)

        return CustomTypeDefinition(self, name, icon, aliasProperties, simpleProperties, objectProperties,
                                    placeHolderTypes)

    def createCustomType(self, name:str, propertiesFilePath:str=None) -> CustomTypeDefinition:
        """
        Creates a new custom type.

        :param name: Name of a new custom type.
        :type name: str
        :param propertiesFilePath: Optional parameter indicating a file with custom type configurations. Default is **None**.
        :type propertiesFilePath: str
        :return: An `epmwebapi.customtypedefinition.CustomTypeDefinition` object.
        :rtype: epmwebapi.customtypedefinition.CustomTypeDefinition
        :raises CustomTypeDependenciesException: Object properties or placeholder dependencies do not exist.
        :raises CustomTypeAlreadyExistsException: Custom type already exists.
        :raises DuplicatedPropertiesNamesException: Duplicated property names.
        :raises InvalidCustomTypeNameException: Invalid custom type name.
        :raises InvalidPropertyNameException: Invalid property name.
        :raises DuplicatedPropertiesTypeException: Duplicated property type.
        :raises MissingPropertyNameException: Missing property name.
        :raises InvalidPropertyTypeException: Invalid object or placeholder property type.
        :raises InvalidIconException: Invalid icon.
        """
        url = self._webApi + '/epm/v1/usertypes'
        customTypes = self.getAllCustomTypes()

        if propertiesFilePath is None:
            jsonRequest = {'name': name, 'icon': "", 'aliasProperties': [],
                           'simpleProperties': [], 'objectProperties': [],
                           'placeHolderProperties': []}
        else:
            with open(propertiesFilePath) as json_file:
                properties = json.load(json_file)

            for obj in properties['objectProperties']:
                if obj["type"] not in customTypes:
                    raise CustomTypeDependenciesException("Object properties dependencies does not exist")

            for placeHolder in properties['placeHolderProperties']:
                if placeHolder["type"] not in customTypes:
                    raise CustomTypeDependenciesException("PlaceHolder dependencies does not exist")

            jsonRequest = {'name': name, 'icon': properties['icon'],
                           'aliasProperties': properties['aliasProperties'],
                           'simpleProperties': properties['simpleProperties'],
                           'objectProperties': properties['objectProperties'],
                           'placeHolderProperties': properties['placeHolderProperties']}

        session = self._authorizationService.getEpmSession()
        response = session.post(url, json=jsonRequest, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2153840640:
                    if 'There is already a type with the same name!' in response.json()["message"]:
                        raise CustomTypeAlreadyExistsException('Custom type ' + name + ' already exists')
                    else:
                        raise DuplicatedPropertiesNamesException('Duplicated properties names provided')
                elif responseCode == 2153775104:
                    if 'BadBrowseNameInvalid' in response.json()["message"]:
                        raise InvalidCustomTypeNameException('Invalid custom type name')
                    else:
                        raise InvalidPropertyNameException('Invalid property format name provided')
                elif responseCode == 2152923136:
                    raise DuplicatedPropertiesTypeException('Duplicated PlaceHolder types provided')
                elif responseCode == 2147549184:
                    raise MissingPropertyNameException('Missing property name')
                elif responseCode == 2160590848:
                    if 'PlaceHolder' in response.json()["message"]:
                        raise InvalidPropertyTypeException('Invalid or missing PlaceHolder property type')
                    else:
                        raise InvalidPropertyTypeException('Invalid or missing object property type')
                elif responseCode == 2158690304:
                    raise InvalidIconException('Invalid icon string')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("CreateCustomType call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        return self.getCustomType(name)

    def _updateCustomType(self, propertiesJson):
        url = self._webApi + '/epm/v1/usertypes'

        jsonRequest = propertiesJson

        session = self._authorizationService.getEpmSession()
        response = session.patch(url, json=jsonRequest, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2158690304:
                    if 'Unknown type name' in response.json()["message"]:
                        raise InvalidCustomTypeNameException('Custom type ' + jsonRequest['name'] + ' not found')
                    else:
                        raise InvalidIconException('Invalid icon string')
                elif responseCode == 2153840640:
                    raise DuplicatedPropertiesNamesException('Duplicated properties names provided')
                elif responseCode == 2153775104:
                    raise InvalidPropertyNameException('Invalid property format name provided')
                elif responseCode == 2152923136:
                    raise DuplicatedPropertiesTypeException('Duplicated PlaceHolder types provided')
                elif responseCode == 2147549184:
                    raise MissingPropertyNameException('Missing property name')
                elif responseCode == 2160590848:
                    if 'PlaceHolder' in response.json()["message"]:
                        raise InvalidPropertyTypeException('Invalid or missing PlaceHolder property type')
                    else:
                        raise InvalidPropertyTypeException('Invalid or missing object property type')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("UpdateCustomType call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

    def deleteCustomType(self, name:str):
        """
        Deletes a custom type.

        :param name: Name of a custom type to delete.
        :type: str
        :raises InvalidCustomTypeNameException: Invalid custom type name.
        :raises Exception: Custom type not found.
        """
        url = self._webApi + '/epm/v1/usertypes/' + name

        session = self._authorizationService.getEpmSession()
        response = session.delete(url, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2158690304:
                    raise InvalidCustomTypeNameException('Custom type ' + name + ' not found')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("DeleteCustomType call error '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

    def exportCustomTypes(self, fileName:str, pathName:str=None):
        """
        Exports custom types to a file in **JSON** format.

        :param fileName: Name of a file to save custom types.
        :type fileName: str
        :param pathName: Path where `fileName` must be saved. Default is **None**, that is, saves to the current directory.
        """
        typesJson = []
        typesNames = self.getAllCustomTypes()
        if typesNames is not None:
            for typeName in typesNames:
                customType = self.getCustomType(typeName)
                typesJson.append(customType.exportJSON())

        jsonText = {'Items': typesJson}

        if pathName is None:
            pathName = os.getcwd()
        fileName = fileName + ".json"
        with open(os.path.join(pathName, fileName), 'w') as outfile:
            json.dump(jsonText, outfile)

    def importCustomTypes(self, filePath:str, importMode:ImportMode=ImportMode.OnlyAdd):
        """
        Imports definitions of custom types from a file to an **EPM Server**.

        :param filePath: Path to a file with custom type configurations.
        :type filePath: str
        :param importMode: Optional parameter indicating a type of import. Default is `ImportMode.OnlyAdd`.
        :type importMode: ImportMode
        :raises BadArgumentException: Invalid `importMode` parameter.
        :raises CustomTypeDependenciesException: Custom type dependencies already exist.
        """
        if importMode != ImportMode.OnlyAdd:
            raise BadArgumentException("Invalid ImportMode argument")

        with open(filePath) as json_file:
            jsonItems = json.load(json_file)

        customTypes = jsonItems['Items']
        customTypesPrev = self.getAllCustomTypes()

        for customType in customTypes:
            if customType['name'] in customTypesPrev:
                raise CustomTypeDependenciesException("Custom types dependencies already exists")

            for obj in customType['objectProperties']:
                if obj['type'] in customTypesPrev:
                    raise CustomTypeDependenciesException("Custom types dependencies already exists")

            for placeHolder in customType['placeHolderProperties']:
                if placeHolder['type'] in customTypesPrev:
                    raise CustomTypeDependenciesException("Custom types dependencies already exists")

        customTypesDefs = []
        itemsObjectProperties = []
        itemsPlaceHolderProperties = []
        for customType in customTypes:
            self.createCustomType(customType['name'])
            customTypeDef = CustomTypeDefinition(self, name=customType['name'], icon=customType['icon'])

            for aliasProperty in customType['aliasProperties']:
                customTypeDef.addAliasProperty(aliasProperty['name'])

            for simpleProperty in customType['simpleProperties']:
                customTypeDef.addSimpleProperty(simpleProperty['name'], simpleProperty['initialValue'])

            itemsObjectProperties.append(customType['objectProperties'])

            itemsPlaceHolderProperties.append(customType['placeHolderProperties'])

            customTypesDefs.append(customTypeDef)

        for customTypeDef in customTypesDefs:
            customTypeDef.save()

        for (customTypeDef, objectProperties, placeHolderProperties) in zip(customTypesDefs, itemsObjectProperties,
                                                                            itemsPlaceHolderProperties):
            for objectProperty in objectProperties:
                customTypeDef.addObjectProperty(objectProperty['name'], objectProperty['type'])

            for placeHolderType in placeHolderProperties:
                customTypeDef.addPlaceHolderType(placeHolderType['type'])

        for customTypeDef in customTypesDefs:
            customTypeDef.save()

        # Pode ocorrer ordem diferente de processamento no Server

    def filterModel(self, startObjects:List[EpmModelObject], nameFilter:str="*", objectType:str=None, filter:ElementOperand=None)-> OrderedDict[str,EpmModelObject]:
        """
        Returns all objects that satisfy the specified filter on the `startedObjects` list.

        :param startObjects: The nodes where a search starts.
        :type startObjects: List[EpmModelObject]
        :param nameFilter: An optional parameter indicating a name to an Object Instance Filter. Use `*` for **All**. Default is **None**.
        :type namefilter: string
        :param objectType: A string value indicating the `UserType` to search on **Elipse Data Model**. Default is **None**.
        :type objectType: string
        :param filter: An `ElementOperand` describing a filter to apply to `objectType` result nodes. Default is **None**.
        :type filter: ElementOperand. 
        :return: An Ordered Dictionary with all objects found.
        :rtype: OrderedDict[str, EpmModelObject]

        Examples
        --------
        The following examples show how to use the **filterModel** function.

        + Creates a filter looking for all items on the `CityA` object that have "PUMP" in their names:

        .. code-block:: python

            obj = connection.getElipseDataModelObjects('water/CityA')['water/CityA']
            result = filterModel([obj], '*PUMP*')

        + Creates a filter looking for all Pumps on the `CityA` object that have "302" in their names:

        .. code-block:: python

            obj = connection.getElipseDataModelObjects('water/CityA')['water/CityA']
            result = filterModel([obj], '*302*', 'PUMP')

        + Creates a filter looking for all items on the `CityA` object with type **WaterStation** that have the **ShortName** property equal to "PCP_Name1":

        .. code-block:: python

            from epmwebapi.elementoperand import ElementOperand, Operator
            from epmwebapi.literaloperand import LiteralOperand
            from epmwebapi.simpleattributeoperand import SimpleAttributeOperand

            obj = connection.getElipseDataModelObjects('water/CityA')['water/CityA']
            filter = ElementOperand(Operator.Equals, [SimpleAttributeOperand('ShortName'), LiteralOperand('PCP_Name1')])
            objects = connection.filterModel([obj], '*', 'WaterStation', filter)

        + Creates a filter looking for all Pumps on the `CityA` object that have the **Temperature1** property greater than the **Temperature2** property:

        .. code-block:: python

            from epmwebapi.elementoperand import ElementOperand, Operator
            from epmwebapi.literaloperand import LiteralOperand
            from epmwebapi.simpleattributeoperand import SimpleAttributeOperand

            cityA = connection.getElipseDataModelObjects('water/CityA')['water/CityA']
            filter = ElementOperand(Operator.GreaterThan, [SimpleAttributeOperand('Temperature1'), SimpleAttributeOperand('Temperature2')])
            objects = connection.filterModel([cityA], '*', 'PUMP', filter)

        + Creates a filter looking for all Pumps on `CityA` and `CityB` objects in which temperature is greater than 15 degrees:

        .. code-block:: python

            from epmwebapi.elementoperand import ElementOperand, Operator
            from epmwebapi.literaloperand import LiteralOperand
            from epmwebapi.simpleattributeoperand import SimpleAttributeOperand

            cityA = connection.getElipseDataModelObjects('water/CityA')['water/CityA']
            cityB = connection.getElipseDataModelObjects('water/CityB')['water/CityB']

            filter = ElementOperand(Operator.GreaterThan, [SimpleAttributeOperand('Temperature'), LiteralOperand(15)])
            result = filterModel([cityA, cityB], '*', 'PUMP', filter)
        """
        startNodes = [object.itemPath for object in startObjects]
        filterType = None
        if objectType != None:
            filterType = ItemPathJSON('OPCUA.BrowsePath', '', '/1:UserTypes/1:' + objectType)
        if nameFilter == None or nameFilter == '':
            nameFilter = '*'
        return self._queryModel(startNodes, nameFilter, filterType, filter)

    def filterDataModel(self, nameFilter:str=None, objectType:str=None, filter:ElementOperand=None) -> OrderedDict[str,EpmModelObject]:
        """
        Returns all objects that satisfy the specified filter in **Elipse Data Model** tree.

        :param nameFilter: An optional parameter indicating a name to an Object Instance Filter. Use `*` for **All**. Default is **None**.
        :type namefilter: string
        :param objectType: A string value indicating the `UserType` to search on **Elipse Data Model**. Default is **None**.
        :type objectType: string
        :param filter: An `ElementOperand` describing a filter to apply to `objectType` result nodes. Default is **None**.
        :type filter: ElementOperand. 
        :return: An Ordered Dictionary with all objects found.
        :rtype: OrderedDict[str, EpmModelObject]

        Examples
        --------
        The following examples show how to use the **filterDataModel** function.
        
        + Creates a filter looking for all items on the **ElipseDataModel** folder that have "PUMP" in their names:

        .. code-block:: python

            result = filterDataModel('*PUMP*')

        + Creates a filter looking for all Pumps on the **ElipseDataModel** folder that have "302" in their names:

        .. code-block:: python

            result = filterDataModel('*302*', 'PUMP')

        + Creates a filter looking for all Pumps on the **ElipseDataModel** folder in which temperature is greater than 15 degrees:


        .. code-block:: python

            from epmwebapi.elementoperand import ElementOperand, Operator
            from epmwebapi.literaloperand import LiteralOperand
            from epmwebapi.simpleattributeoperand import SimpleAttributeOperand

            filter = ElementOperand(Operator.GreaterThan, [SimpleAttributeOperand('Temperature'), LiteralOperand(15)])
            result = filterDataModel('*', 'PUMP', filter)
        """
        startNode = ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.ElipseDataModel.value)
        filterType = None
        if objectType is not None:
            filterType = ItemPathJSON('OPCUA.BrowsePath', '', '/1:UserTypes/1:' + objectType)
        if nameFilter == None or nameFilter == '':
            nameFilter = '*'
        objects = self._queryModel([startNode], nameFilter, filterType, filter)
        return objects

    def filterEpmModel(self, nameFilter:str=None, objectType:str=None, filter:ElementOperand=None) -> OrderedDict[str,EpmModelObject]:
        """
        Returns all objects that satisfy the specified filter in **EPM Model** tree.

        :param nameFilter: An optional parameter indicating a name to an Object Instance Filter. Use `*` for **All**. Default is **None**.
        :type namefilter: string
        :param objectType: A string value indicating the `UserType` to search on **Elipse Data Model**. Default is **None**.
        :type objectType: string
        :param filter: An `ElementOperand` describing a filter to apply to `objectType` result nodes. Default is **None**.
        :type filter: ElementOperand. 
        :return: An Ordered Dictionary with all objects found.
        :rtype: OrderedDict[str, EpmModelObject]

        Examples
        --------
        The following examples show how to use the **filterEpmModel** function.

        + Creates a filter looking for all items on the **EPMModel** folder that have "PUMP" in their names:

        .. code-block:: python

            result = filterEpmModel('*PUMP*')

        + Creates a filter looking for all Pumps on the **EPMModel** folder that have "302" in their names:

        .. code-block:: python

            result = filterEpmModel('*302*', 'PUMP')

        + Creates a filter looking for all Pumps on the **EPMModel** folder in which temperature is greater than 15 degrees:

        .. code-block:: python

            from epmwebapi.elementoperand import ElementOperand, Operator
            from epmwebapi.literaloperand import LiteralOperand
            from epmwebapi.simpleattributeoperand import SimpleAttributeOperand

            filter = ElementOperand(Operator.GreaterThan, [SimpleAttributeOperand('Temperature'), LiteralOperand(15)])
            result = filterEpmModel('*', 'PUMP', filter)
        """
        startNode = ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.EpmModel.value)
        filterType = None
        if objectType is not None:
            filterType = ItemPathJSON('OPCUA.BrowsePath', '', '/1:UserTypes/1:' + objectType)
        if nameFilter == None or nameFilter == '':
            nameFilter = '*'
        objects = self._queryModel([startNode], nameFilter, filterType, filter)
        return objects

    def filterDataObjects(self, filter:DataObjectsFilter=None, attributes:DataObjectAttributes=DataObjectAttributes.Unspecified) -> OrderedDict[str,Union[EpmDataObject ,BasicVariable]]:
        """
        Returns all Data Objects that satisfy the specified filter.

        :param filter: An `epmwebapi.dataobjectsfilter.DataObjectsFilter` object defining a search. Default is **None**.
        :type filter: epmwebapi.dataobjectsfilter.DataObjectsFilter
        :param attributes: An `epmwebapi.dataobjectattributes.DataObjectAttributes` value indicating the attributes to read from Data Objects. Default is `epmwebapi.dataobjectattributes.DataObjectAttributes.Unspecified`.
        :type attributes: epmwebapi.dataobjectattributes.DataObjectAttributes
        :return: An Ordered Dictionary with all Data Objects found.
        :rtype: OrderedDict[str, Union[EpmDataObject,BasicVariable]]
        """

        if filter is None:
            filter = DataObjectsFilter()

        typesFilter = []
        if DataObjectsFilterType.BasicVariable in filter.type:
            typesFilter.append(ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.BasicVariableType.value))
        if DataObjectsFilterType.ExpressionVariable in filter.type:
            typesFilter.append(ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.ExpressionVariableType.value))

        dataObjects = self._query(filter.name, filter.description, filter.eu, filter.domain, typesFilter)

        self._fillDataObjectsAttributes(list(dataObjects.values()), attributes)

        return dataObjects

    def _getObjectPath(self, itemPath, name):
        currentItemPath = itemPath
        path = name
        while currentItemPath is not None:
            references = self._browse([currentItemPath], EpmNodeIds.HasComponent.value, browseDirection=BrowseDirection.Inverse).references()
            if len(references) < 1 or len(references[0]) < 1:
                references = self._browse([currentItemPath], EpmNodeIds.Organizes.value, browseDirection=BrowseDirection.Inverse).references()
                if len(references) < 1 or len(references[0]) < 1:
                    break
            currentItemPath = ItemPathJSON('OPCUA.NodeId', None, references[0][0]._identity)
            path = references[0][0]._displayName + '/' + path
        return path

    def getObjectsFromType(self, typeName:str, discoverInstancePaths:bool=True) -> List[EpmObject]:
        """
        Returns all instances from the specified type name.

        :param typeName: A type to search for.
        :type typeName: str
        :param discoverInstancePaths: An optional parameter indicating whether to retrieve the address space path for each instance or not. Default is `True`.
        :return: A list of all instances found.
        :rtype: list[EpmObject]
        """
        typePath = 'UserTypes/' + typeName
        browsePaths = []
        browsePath = self._translatePathToBrowsePath(typePath)
        browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))

        browseRequest = self._browse(browsePaths, EpmNodeIds.HasTypeDefinition.value, browseDirection=BrowseDirection.Inverse).references()
        objs = []
        for reference in browseRequest:
            if reference is None:
                continue
            identities = [ItemPathJSON('OPCUA.NodeId', None, item._identity) for item in reference]
            names = [item._displayName for item in reference]
            for index in range(0, len(identities)):
                path = ''
                if discoverInstancePaths:
                    path = self._getObjectPath(identities[index], names[index])
                objs.append(EpmObject(self, identities[index], path, names[index], typeName))
        return objs

    def _getObjectsFromItemPaths(self, browsePaths:List[ItemPathJSON], paths:List[str]) -> OrderedDict[str,EpmModelObject]:
        # Verifica se todos os itens existem
        readRequest = self._read(browsePaths, [NodeAttributes.NodeId.value] * len(browsePaths)).items()

        objs = collections.OrderedDict()

        existentPaths = []
        identities = []

        index = 0
        for item in readRequest:
            if item[1].code != 0:
                objs[paths[index]] = None
            else:
                existentPaths.append(paths[index])
                identities.append(ItemPathJSON('OPCUA.NodeId', None, item[0]._identity))
            index = index + 1

        if len(identities) < 1:
            return objs

        typesResults = self._browse(identities, EpmNodeIds.HasTypeDefinition.value).references()

        for index in range(0, len(existentPaths)):
            if typesResults[index][0]._displayName == "PropertyType":
                objs[existentPaths[index]] = EpmProperty(self, existentPaths[index].split('/')[-1], existentPaths[index],
                                                        identities[index])
            else:
                objs[existentPaths[index]] = EpmModelObject(self, identities[index], existentPaths[index],
                                                            existentPaths[index].split('/')[-1],
                                                            typesResults[index][0]._displayName)

        return objs

    def getObjects(self, objectsPaths:Union[List[str],str]) -> OrderedDict[str,EpmModelObject]:
        """
        Returns all objects from specific address space paths.

        :param objectPaths: A list with all objects to return.
        :type objectPaths: List[str]
        :return: An Ordered Dictionary with all objects found or **None** if some paths were not found.
        :rtype: collections.OrderedDict[str]
        """
        paths = []
        browsePaths = []

        if type(objectsPaths) is str:
            paths.append(objectsPaths)
            browsePath = self._translatePathToBrowsePath(objectsPaths)
            browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))
        else:
            for path in objectsPaths:
                paths.append(path)
                browsePath = self._translatePathToBrowsePath(path)
                browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))

        # Verifica se todos os itens existem
        readRequest = self._read(browsePaths, [NodeAttributes.NodeId.value] * len(browsePaths)).items()

        objs = collections.OrderedDict()

        existentPaths = []
        identities = []

        index = 0
        for item in readRequest:
            if item[1].code != 0:
                objs[paths[index]] = None
            else:
                existentPaths.append(paths[index])
                identities.append(ItemPathJSON('OPCUA.NodeId', None, item[0]._identity))
            index = index + 1

        if len(identities) < 1:
            return objs

        typesResults = self._browse(identities, EpmNodeIds.HasTypeDefinition.value).references()
     
        for index in range(0, len(existentPaths)):
            if typesResults[index][0]._displayName == "PropertyType":
                objs[existentPaths[index]] = EpmProperty(self, existentPaths[index].split('/')[-1], existentPaths[index],
                                                        identities[index])
            else:
                objs[existentPaths[index]] = EpmModelObject(self, identities[index], existentPaths[index],
                                                            existentPaths[index].split('/')[-1],
                                                            typesResults[index][0]._displayName)

        return objs

    def getEpmModelObjects(self, objectsPaths:Union[List[str],str]) -> OrderedDict[str,EpmModelObject]:
        """
        Returns all objects from specific address space paths inside an **EPM Model** folder.

        :param objectsPaths: A list with all objects to return.
        :type: list[str]
        :return: An Ordered Dictionary with all objects found or **None** if some paths were not found.
        :rtype: collections.OrderedDict[str]
        """
        paths = []
        browsePaths = []
        resultPaths = []

        if type(objectsPaths) is str:
            resultPaths.append(objectsPaths)
            if objectsPaths == '' or objectsPaths[0] == '/':
                objectsPaths = '/Models/EPMModel' + objectsPaths
            else:
                objectsPaths = '/Models/EPMModel/' + objectsPaths
            paths.append(objectsPaths)
            browsePath = self._translatePathToBrowsePath(objectsPaths)
            browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))
        else:
            for path in objectsPaths:
                resultPaths.append(path)
                if path == '' or path[0] == '/':
                    path = '/Models/EPMModel' + path
                else:
                    path = '/Models/EPMModel/' + path
                paths.append(path)
                browsePath = self._translatePathToBrowsePath(path)
                browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))

        # Verifica se todos os itens existem
        readRequest = self._read(browsePaths, [NodeAttributes.NodeId.value] * len(browsePaths)).items()

        objs = collections.OrderedDict()

        existentPaths = []
        opcUaPaths = []
        identities = []

        index = 0
        for item in readRequest:
            if item[1].code != 0:
                objs[resultPaths[index]] = None
            else:
                existentPaths.append(resultPaths[index])
                opcUaPaths.append(paths[index])
                identities.append(ItemPathJSON('OPCUA.NodeId', None, item[0]._identity))
            index = index + 1

        if len(identities) < 1:
            return objs

        typesResults = self._browse(identities, EpmNodeIds.HasTypeDefinition.value).references()
     
        for index in range(0, len(existentPaths)):
            if typesResults[index][0]._displayName == "PropertyType":
                objs[resultPaths[index]] = EpmProperty(self, opcUaPaths[index].split('/')[-1], opcUaPaths[index],
                                                        identities[index])
            else:
                objs[resultPaths[index]] = EpmModelObject(self, identities[index], opcUaPaths[index],
                                                            opcUaPaths[index].split('/')[-1],
                                                            typesResults[index][0]._displayName)

        return objs

    def getElipseDataModelObjects(self, objectsPaths:Union[List[str],str]) -> OrderedDict[str,EpmModelObject]:
        """
        Returns all objects from specific address space paths inside an **Elipse Data Model** folder.

        :param objectsPath: List with all objects to return.
        :type objectsPath: list[str]
        :return: An Ordered Dictionary with all objects found or **None** if some paths were not found.
        :rtype: collections.OrderedDict[str]
        """
        paths = []
        browsePaths = []
        resultPaths = []

        if type(objectsPaths) is str:
            resultPaths.append(objectsPaths)
            if objectsPaths == '' or objectsPaths[0] == '/':
                objectsPaths = '/Models/ElipseDataModel' + objectsPaths
            else:
                objectsPaths = '/Models/ElipseDataModel/' + objectsPaths
            paths.append(objectsPaths)
            browsePath = self._translatePathToBrowsePath(objectsPaths)
            browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))
        else:
            for path in objectsPaths:
                resultPaths.append(path)
                if path == '' or path[0] == '/':
                    path = '/Models/ElipseDataModel' + path
                else:
                    path = '/Models/ElipseDataModel/' + path
                paths.append(path)
                browsePath = self._translatePathToBrowsePath(path)
                browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))

        # Verifica se todos os itens existem
        readRequest = self._read(browsePaths, [NodeAttributes.NodeId.value] * len(browsePaths)).items()

        objs = collections.OrderedDict()

        existentPaths = []
        opcUaPaths = []
        identities = []

        index = 0
        for item in readRequest:
            if item[1].code != 0:
                objs[resultPaths[index]] = None
            else:
                existentPaths.append(resultPaths[index])
                opcUaPaths.append(paths[index])
                identities.append(ItemPathJSON('OPCUA.NodeId', None, item[0]._identity))
            index = index + 1

        if len(identities) < 1:
            return objs
        
        typesResults = self._browse(identities, EpmNodeIds.HasTypeDefinition.value).references()

        for index in range(0, len(existentPaths)):
            if typesResults[index][0]._displayName == "PropertyType":
                objs[resultPaths[index]] = EpmProperty(self, opcUaPaths[index].split('/')[-1], opcUaPaths[index],
                                                        identities[index])
            else:
                objs[resultPaths[index]] = EpmModelObject(self, identities[index], opcUaPaths[index],
                                                            opcUaPaths[index].split('/')[-1],
                                                            typesResults[index][0]._displayName)
        return objs

    def _addInstancesEpmModel(self, path, names, objTypes):
        url = self._webApi + '/epm/v1/epmmodel/' + path
        paths = []
        objs = {}

        if type(names) is str:
            if type(objTypes) is not str:
                raise BadArgumentException("If names is a string ObjTypes must be a string too")
            jsonRequest = {'items': [{'name': names, 'type': objTypes}]}
            paths.append(path + "/" + names)
        else:
            if type(objTypes) is str:
                requestList = []
                for name in names:
                    requestList.append({'name': name, 'type': objTypes})
                    paths.append(path + "/" + name)
                jsonRequest = {'items': requestList}
            else:
                if len(names) != len(objTypes):
                    raise BadArgumentException("Names and ObjTypes must have the same size")
                requestList = []
                for (name, objType) in zip(names, objTypes):
                    requestList.append({'name': name, 'type': objType})
                    paths.append(path + "/" + name)
                jsonRequest = {'items': requestList}

        session = self._authorizationService.getEpmSession()
        response = session.post(url, json=jsonRequest, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2153840640:
                    raise InstanceNameDuplicatedException('Instance name duplicated')
                elif responseCode == 2154758144:
                    raise InvalidObjectNameException('EPM Model object not found')
                elif responseCode == 2153512960:
                    raise ObjectDependenciesException('Instance type creation not allowed')
                elif responseCode == 2158690304:
                    raise InvalidObjectTypeException('Invalid type name')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("AddInstanceEpmModel call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        for obj in self.getEpmModelObjects(paths).values():
            objs[obj.name] = obj

        return objs

    def _addReferencesEpmModel(self, path, obj):
        url = self._webApi + '/epm/v1/epmmodel/reference/' + path
        paths = []
        objs = {}

        if type(obj) is not EpmObject and type(obj) is not EpmModelObject:
           raise BadArgumentException("obj must be an EpmObject type!")
        jsonRequest = {'itemPath': obj._itemPath.toDict()}

        session = self._authorizationService.getEpmSession()
        response = session.post(url, json=jsonRequest, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2153840640:
                    raise InstanceNameDuplicatedException('Reference name duplicated')
                elif responseCode == 2154758144:
                    raise InvalidObjectNameException('EPM Model object not found')
                elif responseCode == 2153512960:
                    raise ObjectDependenciesException('Instance type creation not allowed')
                elif responseCode == 2158690304:
                    raise InvalidObjectTypeException('Invalid type name')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("AddReferenceEpmModel call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        return True

    def _removeInstanceEpmModel(self, path):
        url = self._webApi + '/epm/v1/epmmodel/' + path

        session = self._authorizationService.getEpmSession()
        response = session.delete(url, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('EPM Model object not found')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("RemoveInstanceEpmModel call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

    def getDataModelObjectProperties(self, objectPath:str) -> OrderedDict:
        """
        Returns all object properties from specific address space paths inside an **Elipse Data Model** folder.

        :param objectPath: Path to start after the **Elipse Data Model** node.
        :type objectPath: str
        :return: An Ordered Dictionary with all properties from the target object.
        :rtype: collections.OrderedDict[property]
        :raises InvalidObjectNameException: Object not found.
        """
        url = self._webApi + '/epm/v1/datamodel/' + objectPath

        session = self._authorizationService.getEpmSession()
        response = session.get(url, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object not found')
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("getDataModelObjectProperties call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        json_response = json.loads(response.text)

        properties = collections.OrderedDict()

        from .customtypedefinition import AliasProperty, ObjectProperty, SimpleProperty
        for dic in json_response['items']:
            if dic['type'] == "AliasProperty":
                if 'source' in dic:
                    properties[dic['name']] = AliasProperty(dic['name'], dic['source'])
                else:
                    properties[dic['name']] = AliasProperty(dic['name'], '')
            elif dic['type'] == "Property":
                properties[dic['name']] = SimpleProperty(dic['name'])
            else:
                properties[dic['name']] = ObjectProperty(dic['name'], dic['type'])
        
        return properties

    def getEpmModelObjectProperties(self, objectPath:str) -> OrderedDict:
        """
        Returns all object properties from specific address space paths inside an **EPM Model** folder.

        :param objectPath: Path to start searching after the **EPM Model** node.
        :type objectPath: str
        :return: An Ordered Dictionary with properties from the target object.
        :rtype: collections.OrderedDict[property]
        :raises InvalidObjectNameException: Object not found.
        """
        url = self._webApi + '/epm/v1/epmmodel/' + objectPath

        session = self._authorizationService.getEpmSession()
        response = session.get(url, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object not found')
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("getEpmModelObjectProperties call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        json_response = json.loads(response.text)

        properties = collections.OrderedDict()

        from .customtypedefinition import AliasProperty, ObjectProperty, SimpleProperty
        for dic in json_response['items']:
            if dic['type'] == "AliasProperty":
                if 'source' in dic:
                    properties[dic['name']] = AliasProperty(dic['name'], dic['source'])
                else:
                    properties[dic['name']] = AliasProperty(dic['name'], '')
            elif dic['type'] == "Property":
                properties[dic['name']] = SimpleProperty(dic['name'])
            else:
                properties[dic['name']] = ObjectProperty(dic['name'], dic['type'])
        
        return properties

    def _setBindedVariables(self, objectPath, aliasProperties, variablesNames, isEpmModel=True):
        if isEpmModel:
            url = self._webApi + '/epm/v1/epmmodel/' + objectPath
        else:
            raise BadArgumentException('Invalid isEpmModel argument')

        session = self._authorizationService.getEpmSession()
        response = session.get(url, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object not found')
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("SetBindedVariables call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        json_response = json.loads(response.text)

        if type(aliasProperties) is str:
            if type(variablesNames) is not str:
                raise BadArgumentException('aliasProperties and variablesNames must be the same size')
            counter = 1
            for dic in json_response['items']:
                if dic['name'] == aliasProperties and dic['type'] == 'AliasProperty':
                    counter = counter - 1
        else:
            if type(variablesNames) is str:
                raise BadArgumentException('aliasProperties and variablesNames must be the same size')
            if len(aliasProperties) != len(variablesNames):
                raise BadArgumentException('aliasProperties and variablesNames must be the same size')
            counter = len(aliasProperties)
            for dic in json_response['items']:
                if dic['name'] in aliasProperties and dic['type'] == 'AliasProperty':
                    counter = counter - 1

        if counter != 0:
            raise InvalidObjectPropertyException('Invalid alias property name')

        if type(aliasProperties) is str:
            jsonRequest = {'items': [{'propertyName': aliasProperties, 'value': variablesNames}]}
        else:
            itemsList = []
            for (aliasProperty, variableName) in zip(aliasProperties, variablesNames):
                itemsList.append({'propertyName': aliasProperty, 'value': variableName})
            jsonRequest = {'items': itemsList}

        response = session.patch(url, json=jsonRequest, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object not found')
                elif responseCode == 2153775104:
                    raise InvalidSourceVariableException('Invalid source variable provided')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("SetBindedVariables call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

    def exportEpmModel(self, fileName:str, pathName:str=None):
        """
        Exports an **EPM Model** configuration to a file in **JSON** format.

        :param fileName: Name of a file to save the **EPM Model**.
        :type fileName: str
        :param pathName: An optional path where `fileName` is located. Default is **None**, that is, searches the current directory.
        :type pathName: str
        """
        items = self._epmModelInstancesToJson('')
        jsonWrite = {'items': items}

        if pathName is None:
            pathName = os.getcwd()
        fileName = fileName + ".json"
        with open(os.path.join(pathName, fileName), 'w') as outfile:
            json.dump(jsonWrite, outfile)

    def importEpmModel(self, filePath:str, importMode:ImportMode=ImportMode.OnlyAdd):
        """
        Imports an **EPM Model** configuration saved to a file in **JSON** format to **EPM Model**.

        :param filePath: Path to a configuration file.
        :type filePath: str
        :param importMode: Optional parameter indicating how to import data. Default is `ImportMode.OnlyAdd`.
        :rtype: ImportMode.OnlyAdd
        """
        with open(filePath) as json_file:
            jsonRead = json.load(json_file)

        self._jsonToEpmModelInstances(jsonRead['items'], '', importMode)

    def _epmModelInstancesToJson(self, path):
        url = self._webApi + '/epm/v1/epmmodel/' + path

        session = self._authorizationService.getEpmSession()
        response = session.get(url, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object ' + path + ' not found')
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("_epmModelInstancesToJson call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + " Path: '" + path + "'. Text: " + response.text)

        json_response = json.loads(response.text)
        itemsList = []

        for dic in json_response['items']:
            if dic['type'] != 'Property' and dic['type'] != 'AliasProperty':
                if path == '':
                    items = self._epmModelInstancesToJson(dic['name'])
                else:
                    items = self._epmModelInstancesToJson(path + '/' + dic['name'])
                dic['items'] = items
            elif dic['type'] == 'Property':
                propPath = path + '/' + dic['name']
                prop = self.getEpmModelObjects(propPath)[propPath]
                dic['value'] = prop.read().value
            itemsList.append(dic)

        return itemsList

    def _jsonToEpmModelInstances(self, items, path, importMode):
        url = self._webApi + '/epm/v1/epmmodel/' + path

        session = self._authorizationService.getEpmSession()
        response = session.get(url, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object ' + path + ' not found')
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("JsonToEpmModelInstances call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + " Path: '" + path + "'. Text: " + response.text)

        objInstances = json.loads(response.text)
        createdInstances = []
        for instance in objInstances['items']:
            createdInstances.append(instance['name'])

        obj = self.getEpmModelObjects(path)[path]

        if importMode == ImportMode.OnlyAdd:
            for item in items:
                try:
                    if item['type'] == 'Property':
                        propPath = path + '/' + item['name']
                        prop = self.getEpmModelObjects(propPath)[propPath]
                        prop.write(item['value'])
                    elif item['type'] == 'AliasProperty':
                        if item['source']:
                            obj.setBindedVariables(item['name'], item['source'])
                    else:
                        if path != '':
                            objType = self.getCustomType(obj.type)
                            if item['type'] in objType.placeHolderTypes:
                                objPropertiesNames = []
                                for objProp in objType.objectProperties:
                                    objPropertiesNames.append(objProp.name)
                                if item['name'] not in createdInstances:
                                    obj.addInstances(item['name'], item['type'])
                                elif item['name'] not in objPropertiesNames:
                                    raise InvalidObjectNameException(item['name'] + ' already exists')
                            objPath = path + '/' + item['name']
                            self._jsonToEpmModelInstances(item['items'], objPath, importMode)
                        else:
                            if item['name'] not in createdInstances:
                                obj.addInstances(item['name'], item['type'])
                            else:
                                raise InvalidObjectNameException(item['name'] + ' already exists')
                            self._jsonToEpmModelInstances(item['items'], item['name'], importMode)
                except InvalidObjectNameException as err:
                    raise err
                except:
                    raise BadArgumentException("Argument error on " + item['name'])
        elif importMode == ImportMode.OnlyEdit:
            for item in items:
                try:
                    if item['type'] == 'Property':
                        propPath = path + '/' + item['name']
                        prop = self.getEpmModelObjects(propPath)[propPath]
                        prop.write(item['value'])
                    elif item['type'] == 'AliasProperty':
                        if 'source' in item and item['source'] is not None:
                            obj.setBindedVariables(item['name'], item['source'])
                    else:
                        if item['name'] not in createdInstances:
                            raise InvalidObjectNameException(item['name'] + ' does not exist')
                        if path == '':
                            self._jsonToEpmModelInstances(item['items'], item['name'], importMode)
                        else:
                            objPath = path + '/' + item['name']
                            self._jsonToEpmModelInstances(item['items'], objPath, importMode)
                except InvalidObjectNameException as err:
                    raise err
                except:
                    raise BadArgumentException("Argument error on " + item['name'])
        elif importMode == ImportMode.AddAndEdit:
            for item in items:
                try:
                    if item['type'] == 'Property':
                        propPath = path + '/' + item['name']
                        prop = self.getEpmModelObjects(propPath)[propPath]
                        prop.write(item['value'])
                    elif item['type'] == 'AliasProperty':
                        if 'source' in item and item['source'] is not None:
                            obj.setBindedVariables(item['name'], item['source'])
                    else:
                        if item['name'] not in createdInstances:
                            obj.addInstances(item['name'], item['type'])
                        if path == '':
                            self._jsonToEpmModelInstances(item['items'], item['name'], importMode)
                        else:
                            objPath = path + '/' + item['name']
                            self._jsonToEpmModelInstances(item['items'], objPath, importMode)
                except Exception as ex:
                    raise BadArgumentException("Argument error on " + item['name'])
        else:
            raise BadArgumentException("Invalid ImportMode argument")

    def getAdvancedEvent(self, eventName:str):
        """
        Gets an object representing an **Advanced** event.

        :param eventName: The name of an event.
        :type eventName: str

        Examples
        --------
        The following examples show how to use the **getAdvancedEvent** function.

        + Retrieves all events from a period of time:

        .. code-block:: python

            ini_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
            end_date = dt.datetime.now(dt.timezone.utc)
            queryPeriod = epm.QueryPeriod(ini_date, end_date)
            typeEvent = connection.getAdvancedEvent('EventName')
            result = typeEvent.historyRead(queryPeriod)

        + Retrieves all events in which `Tag0023` is greater than 30 (`Tag0023` must be inserted on Payload):

        .. code-block:: python

            ini_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
            end_date = dt.datetime.now(dt.timezone.utc)
            queryPeriod = epm.QueryPeriod(ini_date, end_date)
            typeEvent = connection.getTypeEvent('PumpEventName')
            where = ElementOperand(Operator.Greater, [SimpleAttributeOperand('Tag0023'), LiteralOperand(30)])
            result = typeEvent.historyRead(queryPeriod, where)
        """
        return AdvancedEvent(self, eventName)

    def getTypeEvent(self, eventName:str):
        """
        Gets an object representing a `TypeEvent` event.

        :param eventName: The name of an event.
        :type eventName: str

        Examples
        --------
        The following examples show how to use the **getTypeEvent** function.

        + Retrieves all events from a period of time:

        .. code-block:: python

            ini_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
            end_date = dt.datetime.now(dt.timezone.utc)
            queryPeriod = epm.QueryPeriod(ini_date, end_date)
            typeEvent = connection.getTypeEvent('EventName')
            result = typeEvent.historyRead(queryPeriod)

        + Retrieves all events from `Pump14` in the last hour:

        .. code-block:: python

            ini_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
            end_date = dt.datetime.now(dt.timezone.utc)
            queryPeriod = epm.QueryPeriod(ini_date, end_date)
            typeEvent = connection.getTypeEvent('PumpEventName')
            where = ElementOperand(Operator.Like, [SimpleAttributeOperand('SourceInstance'), LiteralOperand('Pump14')])
            result = typeEvent.historyRead(queryPeriod, where)

        + Retrieves all Pumps in which temperature is greater than 30 degrees (Pump's **Temperature** property must be inserted on Payload):

        .. code-block:: python

            ini_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
            end_date = dt.datetime.now(dt.timezone.utc)
            queryPeriod = epm.QueryPeriod(ini_date, end_date)
            typeEvent = connection.getTypeEvent('PumpEventName')
            where = ElementOperand(Operator.Greater, [SimpleAttributeOperand('Temperature'), LiteralOperand(30)])
            result = typeEvent.historyRead(queryPeriod, where, ['SourceInstance'])
        """
        return TypeEvent(self, eventName)

    def newDataset(self, name:str, description:str=None) -> DatasetConfig:
        """
        Creates a new Dataset.

        :param name: Name of this new Dataset.
        :type name: str
        :param description: Optional parameter indicating a description for this Dataset. Default is **None**.
        :return: An `epmwebapi.datasetconfig.DatasetConfig` object.
        :rtype: epmwebapi.datasetconfig.DatasetConfig
        """
        return DatasetConfig(self, name, description=description)

    def newDatasetLocal(self, name:str, description:str = None) -> DatasetConfig:
        """
        Creates a new local Dataset.

        :param name: Name of this new local Dataset.
        :type name: str
        :param description: Optional parameter indicating a description for this local Dataset. Default is **None**.
        :return: An `epmwebapi.datasetconfig.DatasetConfig` object.
        :rtype: epmwebapi.datasetconfig.DatasetConfig
        :raises BadArgumentException: Dataset already exists.
        """
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        documentsFolder = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, documentsFolder)
        documentsFolder = documentsFolder.value.replace('\\', '/')
        filesPath = documentsFolder + '/Elipse Software/EPM Studio/Datasets/'
        files = os.listdir(filesPath)
        for file in files:
            if str.lower(name) == str.lower(file.title()[:-11]):
                raise BadArgumentException("Dataset name already exists")
        filePath = filesPath + name + '.epmdataset'
        dataset = DatasetConfigLocal(self, name, description=description, filePath=filePath)
        dataset.save()

        return dataset

    def newDatasetServer(self, name:str, description:str = None) -> DatasetConfig:
        """
        Creates a new Dataset on the server.

        :param name: Name of this new Dataset.
        :type name: str
        :param description: An optional parameter indicating a description for this new Dataset. Default is **None**.
        :return: An `epmwebapi.datasetconfig.DatasetConfig` object.
        :rtype: epmwebapi.datasetconfig.DatasetConfig
        :raises BadArgumentException: Dataset already exists on the server.
        """
        for datasetName in self.listDatasetServer():
            if str.lower(name) == str.lower(datasetName):
                raise BadArgumentException("Dataset name already exists")
        dataset = DatasetConfigServer(self, name, description=description)
        dataset.save()

        return dataset

    def loadDatasetFile(self, filePath:str) -> DatasetConfig:
        """
        Loads a Dataset file from the local computer.

        :param filePath: Path of a Dataset file.
        :type filePath: str
        :return: An `epmwebapi.datasetconfig.DatasetConfig` object.
        :rtype: epmwebapi.datasetconfig.DatasetConfig
        :raises BadArgumentException: Invalid file extension.
        """
        if str.lower(filePath).endswith('.epmdataset'):
            if '\\' in filePath:
                filePath = filePath.value.replace('\\', '/')
            name = filePath.split('/')[-1]
            name = name[:-11]
            with open(filePath, "r") as file:
                content = file.read()

            return DatasetConfigLocal(self, name, content, filePath=filePath)
        else:
            raise BadArgumentException("Invalid file extension")

    def loadDatasetLocal(self, fileName:str) -> DatasetConfig:
        """
        Loads a local Dataset from the local computer.

        :param fileName: Name of a Dataset.
        :type fileName: str
        :return: An `epmwebapi.datasetconfig.DatasetConfig` object.
        :rtype: epmwebapi.datasetconfig.DatasetConfig
        """
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        documentsFolder = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, documentsFolder)
        documentsFolder = documentsFolder.value.replace('\\', '/')
        filePath = documentsFolder + '/Elipse Software/EPM Studio/Datasets/' + fileName + '.epmdataset'
        name = fileName

        with open(filePath, "r") as file:
            content = file.read()

        return DatasetConfigLocal(self, name, content, filePath=filePath)

    def loadDatasetServer(self, name:str) -> DatasetConfig:
        """
        Loads a Dataset from an **EPM Server**.

        :param name: Name of a Dataset.
        :type name: str
        :return: An `epmwebapi.datasetconfig.DatasetConfig` object.
        :rtype: epmwebapi.datasetconfig.DatasetConfig
        """
        url = self._webApi + '/epm/v1/resource'
        datasetAddress = "1:Datasets/1:" + name
        itemPath = ItemPathJSON("OPCUA.BrowsePath", None, datasetAddress)
        continuationPoint = None
        jsonRequest = {"continuationPoint": continuationPoint, "paths": [itemPath.toDict()]}
        session = self._authorizationService.getEpmSession()
        response = session.post(url, json=jsonRequest, verify=False)
        jsonResponse = json.loads(response.text)
        if response.status_code != 200:
            return None
        content = jsonResponse['items'][0]['content']
        description = jsonResponse['items'][0]['description']

        return DatasetConfigServer(self, name, description, content)

    def _saveDatasetFile(self, content, filePath, overwrite = False):
        if overwrite is False:
            if os.path.exists(filePath):
                raise Exception("Dataset file already exists")

        content = content.replace('\r\n', '\n')
        with open(filePath, "w") as file:
            file.write(content)

    def _saveDatasetServer(self, name, description, content, overwrite = False, oldName = None):
        exists = False
        for datasetName in self.listDatasetServer():
            if str.lower(name) == str.lower(datasetName):
                exists = True

        session = self._authorizationService.getEpmSession()

        if exists is False:
            if oldName is None:
                identity = None
            else:
                url = self._webApi + '/epm/v1/resource'
                datasetAddress = "1:Datasets/1:" + oldName
                itemPath = ItemPathJSON("OPCUA.BrowsePath", None, datasetAddress)
                continuationPoint = None
                jsonRequest = {"continuationPoint": continuationPoint, "paths": [itemPath.toDict()]}
                response = session.post(url, json=jsonRequest, verify=False)
                jsonResponse = json.loads(response.text)
                identity = jsonResponse['items'][0]['identity']
        else:
            if overwrite is False:
                raise Exception("Dataset already exists")
            else:
                url = self._webApi + '/epm/v1/resource'
                datasetAddress = "1:Datasets/1:" + name
                itemPath = ItemPathJSON("OPCUA.BrowsePath", None, datasetAddress)
                continuationPoint = None
                jsonRequest = {"continuationPoint": continuationPoint, "paths": [itemPath.toDict()]}
                response = session.post(url, json=jsonRequest, verify=False)
                jsonResponse = json.loads(response.text)
                identity = jsonResponse['items'][0]['identity']

        url = self._webApi + '/epm/v1/resource/update'
        resourceModelJson = {"identity": identity, "name": name, "description": description,
                             "typeId": "{041582AB-CD7B-4313-8477-1D3AC4A43256}", "content": content}
        jsonRequest = {"items": [resourceModelJson]}
        response = session.post(url, json=jsonRequest, verify=False)
        jsonResponse = json.loads(response.text)
        errorCode = jsonResponse['diagnostics'][0]['code']
        if errorCode != 0:
            raise Exception("Dataset save did not succeed")

    def _deleteDatasetFile(self, filePath):
        if filePath is not None and os.path.exists(filePath) and filePath.endswith('.epmdataset'):
            os.remove(filePath)
        else:
            raise BadArgumentException("Dataset file does not exist")

    def _deleteDatasetServer(self, name):
        exists = False
        for datasetName in self.listDatasetServer():
            if str.lower(name) == str.lower(datasetName):
                exists = True
        if exists is True:
            url = self._webApi + '/epm/v1/resource/remove'
            datasetAddress = "1:Datasets/1:" + name
            itemPath = ItemPathJSON("OPCUA.BrowsePath", None, datasetAddress)
            jsonRequest = {"paths": [itemPath.toDict()]}
            session = self._authorizationService.getEpmSession()
            response = session.post(url, json=jsonRequest, verify=False)
            jsonResponse = json.loads(response.text)
            errorCode = jsonResponse['diagnostics'][0]['code']
            if errorCode != 0:
                raise Exception("Dataset delete did not succeed")
        else:
            raise BadArgumentException("Dataset does not exist")

    def listDatasetLocal(self) -> List[str]:
        """
        Returns all Datasets on the local computer.

        :return: A `List[str]` with all Datasets found.
        :rtype: List[str]
        """
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        documentsFolder = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, documentsFolder)
        documentsFolder = documentsFolder.value.replace('\\', '/')
        filesPath = documentsFolder + '/Elipse Software/EPM Studio/Datasets/'
        files = os.listdir(filesPath)
        datasetNames = []
        for file in files:
            if str.lower(file.title()).endswith('.epmdataset'):
                datasetNames.append(str.lower(file.title()[:-11]))

        return datasetNames

    def listDatasetServer(self) -> List[str]:
        """
        Returns all Datasets from an **EPM Server**.

        :return: A `List[str]` with all Datasets found.
        :rtype: List[str]
        """
        url = self._webApi + '/epm/v1/resource/list'
        continuationPoint = None
        datasetTypeId = "{041582AB-CD7B-4313-8477-1D3AC4A43256}"
        jsonRequest = {"continuationPoint": continuationPoint, "types": [datasetTypeId]}
        session = self._authorizationService.getEpmSession()
        response = session.post(url, json=jsonRequest, verify=False)
        jsonResponse = json.loads(response.text)
        datasetNames = []
        for item in jsonResponse['items']:
            datasetNames.append(item['name'])

        return datasetNames

    def close(self):
        """
        Closes the current **EPM** Connection.
        """
        self._authorizationService.close()

    def historyUpdate(self, variables:List[Union[EpmDataObject,EpmVariable]], numpyArrays:List[np.ndarray]):
        """
        Writes an array of values, with **Value**, **Timestamp**, and **Quality**, for each specified variable.

        :param variables: List of variables to write the specified values.
        :type variables: List[Union[EpmDataObject,EpmVariable]]
        :param numpyArrays: List of `numpy` arrays with values to write.
        :type numpyArrays: np.ndarray
        """
        self._historyUpdate(HistoryUpdateType.Update.value, [variable._itemPath for variable in variables], numpyArrays)
        return

    def getProperties(self, objects:List[EpmModelObject], propertyName:str) -> collections.OrderedDict[str, EpmProperty]:
        """
        Retrieves the specified property for each object in the provided list.

        :param objects: A list of `EpmModelObject` instances to query.
        :type objects: List[EpmModelObject]
        :param propertyName: The name of a property to retrieve.
        :type propertyName: str
        :return: An Ordered Dictionary mapping each object's ID (`string`) to its corresponding `EpmProperty` instance for the specified property.
        :rtype: collections.OrderedDict[str, EpmProperty]
        """
        from .epmnodeids import EpmNodeIds
        from .itempathjson import ItemPathJSON
        properties = collections.OrderedDict()

        batchSize = 1000

        i = 0

        from itertools import islice
        iterador = iter(objects)

        while True:
            batch = list(islice(iterador, batchSize))
            if not batch:
                break
            hasPropertyResult = self._browse([item._itemPath for item in batch], EpmNodeIds.HasProperty.value, NodeClassMask.Variable, BrowseDirection.Forward).references()
            result = hasPropertyResult
            if len(result) < 1:
                return None

            for index in range(0, len(hasPropertyResult)):
                for j in range(0, len(result[index])):
                    if result[index][j]._nodeClass == 4:  # Method is ignored
                        continue
                    if result[index][j]._displayName == propertyName:
                        path = objects[i]._path + '.' + result[index][j]._displayName
                        properties[path] = EpmProperty(self, result[index][j]._displayName, path, 
                                                         ItemPathJSON('OPCUA.NodeId', '', result[index][j]._identity))
                i = i + 1

        return properties

    def getObjectsPropertyValue(self, objects:List[EpmModelObject], propertyName:str) -> collections.OrderedDict[str, DataValueJSON]:
        """
        Retrieves the value of a specified property for each object in the provided list.

        :param objects: A list of `EpmModelObject` instances to query.
        :type objects: List[EpmModelObject]
        :param propertyName: The name of a property to retrieve.
        :type propertyName: str
        :return: An Ordered Dictionary mapping object property paths (`string`) to the corresponding property values as `DataValueJSON`.
        :rtype: collections.OrderedDict[str, DataValueJSON]
        """
        from .epmnodeids import EpmNodeIds
        from .itempathjson import ItemPathJSON
        properties = collections.OrderedDict()

        batchSize = 1000

        i = 0

        from itertools import islice
        iterador = iter(objects)

        while True:
            batch = list(islice(iterador, batchSize))
            if not batch:
                break
            hasPropertyResult = self._browse([item._itemPath for item in batch], EpmNodeIds.HasProperty.value, NodeClassMask.Variable, BrowseDirection.Forward).references()
            result = hasPropertyResult
            if len(result) < 1:
                return None

            identitiesToRead = []
            paths = []

            for index in range(0, len(hasPropertyResult)):
                for j in range(0, len(result[index])):
                    if result[index][j]._nodeClass == 4:  # Method is ignored
                        continue
                    if result[index][j]._displayName == propertyName:
                        path = objects[i]._path + '.' + result[index][j]._displayName
                        identitiesToRead.append(ItemPathJSON('OPCUA.NodeId', '', result[index][j]._identity))
                        paths.append(path)
                i = i + 1

            resultValues = self._read(identitiesToRead, [NodeAttributes.Value.value] * len(identitiesToRead)).items()
            for index in range(0, len(resultValues)):
                properties[paths[index]] = resultValues[index][0]._value            

        return properties

    def getParents(self, objects:List[EpmModelObject]) -> collections.OrderedDict[str, EpmModelObject]:
        """
        Gets the parent object from all provided objects.

        :param objects: List of `EpmModelObject` instances.
        :type objects: List[EpmModelObject]
        :return: An Ordered Dictionary mapping object paths (`string`) to their corresponding parent `EpmModelObject` instances.
        :rtype: collections.OrderedDict[str, EpmModelObject]
        """

        from .epmnodeids import EpmNodeIds
        from .itempathjson import ItemPathJSON
        parentObjects = collections.OrderedDict()

        batchSize = 1000

        i = 0

        from itertools import islice
        iterador = iter(objects)

        while True:
            batch = list(islice(iterador, batchSize))
            if not batch:
                break
            hasComponentResult = self._browse([item._itemPath for item in batch], EpmNodeIds.HasComponent.value, NodeClassMask.Object, BrowseDirection.Inverse).references()
            result = hasComponentResult
            if len(result) < 1:
                return None

            identities = [ItemPathJSON('OPCUA.NodeId', '', item[0]._identity) for item in result]

            typesResults = self._browse(identities, EpmNodeIds.HasTypeDefinition.value).references()

            for index in range(0, len(hasComponentResult)):
                if result[index][0]._nodeClass == 4:  # Method is ignored
                    continue
                path = objects[i]._path + '/' + result[index][0]._displayName
                parentObjects[path] = EpmModelObject(self, identities[index],
                                                            path, result[index][0]._displayName,
                                                            typesResults[index][0]._displayName)
                i = i + 1

        return parentObjects

    def _historyUpdate(self, updateType, itemPaths, numpyArrays, dataTypeId=None):
        if len(itemPaths) != len(numpyArrays):
            raise Exception('Invalid number of item in numpyArrays')

        # updateType = 3 # Update
        blockSize = 80000
        totalValues = 0

        historyUpdateRequests = []

        import numpy as np
        for index in range(len(itemPaths)):
            valuesCount = len(numpyArrays[index])
            if (valuesCount == 0):
                continue

            if (not numpyArrays[index].dtype.names == ('Value', 'Timestamp', 'Quality')):
                raise Exception('Invalid array definition')

            if valuesCount > blockSize:
                if len(historyUpdateRequests) > 0:
                    self._historyUpdateCall(HistoryUpdateDataModelJSON(historyUpdateRequests))
                    historyUpdateRequests.clear()
                # Prepare big call
                chunks = [numpyArrays[index][x:x + blockSize] for x in range(0, len(numpyArrays[index]), blockSize)]
                for chunk in chunks:
                    dataValueArray = []
                    for i in iter(range(0, len(chunk))):
                        dataType = dataTypeId if i < 1 else None
                        if 'numpy' in str(type(chunk['Value'][i])):
                            dataValueArray.append(DataValueJSON(None if np.isnan(chunk['Value'][i]) else chunk['Value'][i].item(), 
                                                                chunk['Quality'][i],
                                                                chunk['Timestamp'][i], dataTypeId=dataType))
                        else:
                            dataValueArray.append(DataValueJSON(None if np.isnan(chunk['Value'][i]) else chunk['Value'][i], 
                                                                chunk['Quality'][i],
                                                                chunk['Timestamp'][i], dataTypeId=dataType))
                    historyUpdateRequest = HistoryUpdateDataModelJSON(
                        [HistoryUpdateDataItemModelJSON(itemPaths[index], updateType, dataValueArray)])
                    self._historyUpdateCall(historyUpdateRequest)
                totalValues = 0
            else:
                dataValueArray = []
                for i in range(len(numpyArrays[index])):
                    dataType = dataTypeId if i < 1 else None
                    if 'numpy' in str(type(numpyArrays[index]['Value'][i])):
                        dataValueArray.append(DataValueJSON(None if np.isnan(numpyArrays[index]['Value'][i]) else numpyArrays[index]['Value'][i].item(),
                                                            numpyArrays[index]['Quality'][i],
                                                            numpyArrays[index]['Timestamp'][i],
                                                            dataTypeId=dataType))
                    else:
                        dataValueArray.append(DataValueJSON(None if np.isnan(numpyArrays[index]['Value'][i]) else numpyArrays[index]['Value'][i],
                                                            numpyArrays[index]['Quality'][i],
                                                            numpyArrays[index]['Timestamp'][i],
                                                            dataTypeId=dataType))
                historyUpdateRequests.append(
                    HistoryUpdateDataItemModelJSON(itemPaths[index], updateType, dataValueArray))
                if totalValues + valuesCount > blockSize:
                    self._historyUpdateCall(HistoryUpdateDataModelJSON(historyUpdateRequests))
                    historyUpdateRequests.clear()
                    totalValues = 0
                else:
                    totalValues = totalValues + valuesCount
        if len(historyUpdateRequests) > 0:
            self._historyUpdateCall(HistoryUpdateDataModelJSON(historyUpdateRequests))
        return

    def _historyUpdateCall(self, historyUpdateRequest):
        url = self._webApi + '/opcua/v1/history/update/data'

        jsonRequest = historyUpdateRequest.toDict()

        session = self._authorizationService.getEpmSession()

        response = session.post(url, json=jsonRequest, verify=False)
        if response.status_code != 200:
            raise Exception(
                "HistoryUpdate call error + '" + str(response.status_code) + "'. Reason: " + response.reason)

        json_result = json.loads(response.text)
        if json_result['diagnostics'][0]['code'] != 0:
            raise Exception("HistoryUpdate call error. Reason: " + str(json_result['diagnostics'][0]['code']))

        return json_result

    def _historyUpdateAnnotation(self, annotationPath:str, updateType:int, annotations):

        blockSize = 1000
        totalValues = 0

        historyUpdateRequests = []

        valuesCount = len(annotations)
        if (valuesCount == 0):
            return

        import datetime

        dataValueArray = []

        for i in range(len(annotations)):
            dataValueArray.append(AnnotationValueJSON(annotations[i][2], annotations[i][1], annotations[i][0]))

        annotationType = ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.AnnotationType.value)
        historyUpdateRequest = HistoryUpdateDataModelJSON(
            [HistoryUpdateDataItemModelJSON(annotationPath, updateType, dataValueArray, annotationType)])
        self._historyUpdateCall(historyUpdateRequest)

        return

    def _write(self, paths, attributeIds, values):

        url = self._webApi + '/opcua/v1/write'

        writeItems = []
        for x in range(0, len(paths)):
            writeItems.append(WriteItemModelJSON(paths[x], attributeIds[x], values[x]))

        request = WriteModelJSON(writeItems)
        jsonRequest = request.toDict()
        session = self._authorizationService.getEpmSession()
        response = session.post(url, json=jsonRequest, verify=False)
        if response.status_code != 200:
            print(response.reason)
            raise Exception(
                "Write service call http error '" + str(response.status_code) + "'. Reason: " + response.reason + ". Message: " + response.text)
        json_result = json.loads(response.text)
        if json_result is None:
            raise Exception("Write Failed no result")
        elif len(json_result['diagnostics']) != len(writeItems):
            raise Exception("Write Failed with error '" + str(json_result['diagnostics'][0]) + "'")
        elif json_result['diagnostics'][0]['code'] != 0:
            raise Exception(
                "Write Failed with error code: " + str(json_result['diagnostics'][0]['code']) + " and message: '" + str(
                    json_result['diagnostics'][0]['message']) + "'")
        return

    def _read(self, paths, attributeIds):

        url = self._webApi + '/opcua/v1/read'

        readItems = []
        for x in range(0, len(paths)):
            readItems.append(ReadItemModelJSON(paths[x], attributeIds[x]))

        continuationPoint = None

        resultItems = []
        diagnostics = []

        while True:
            request = ReadModelJSON(readItems, continuationPoint)
            jsonRequest = request.toDict()
            session = self._authorizationService.getEpmSession()
            response = session.post(url, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Read service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result is None:
                raise Exception("Read Failed no result")
            elif len(json_result['diagnostics']) != len(readItems):
                raise Exception("Read Failed with error '" + str(json_result['diagnostics'][0]) + "'")

            for diagnostic, item in zip(json_result['diagnostics'], json_result['items']):
                diagnostics.append(DiagnosticModelJSON(diagnostic['code']))
                if diagnostic['code'] == 0:
                    readItem = ReadResultItemModelJSON(item['identity'],
                                                       DataValueJSON(item['value']['value'], item['value']['quality'],
                                                                     item['value']['timestamp'], 
                                                                     item['value']['serverTimestamp'] if 'serverTimestamp' in item['value'] else None, 
                                                                     item['value']['dataTypeId'] if 'dataTypeId' in item['value'] else None))
                else:
                    readItem = None
                resultItems.append(readItem)

            continuationPoint = json_result['continuationPoint']
            if continuationPoint is None:
                break

        return ReadResultModelJSON(resultItems, diagnostics)

    def _browse(self, paths, referenceType, nodeClassMask = NodeClassMask.Unspecified, browseDirection = BrowseDirection.Forward):

        url = self._webApi + '/opcua/v1/browse'

        itemsModels = []
        if not isinstance(paths, list):
            paths = [paths]

        if not isinstance(referenceType, list):
            referenceType = [referenceType]

        for item in paths:
            itemsModels.append(BrowseItemModelJSON(item, nodeClassMask.value, referenceType, browseDirection.value))

        continuationPoint = None

        requestResults = []
        diagnostics = []

        while True:
            request = BrowseModelJSON(itemsModels, continuationPoint)
            jsonRequest = request.toDict()
            session = self._authorizationService.getEpmSession()
            response = session.post(url, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Browse service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result is None:
                raise Exception("Browse Failed no result")
            elif len(json_result['diagnostics']) != len(paths):
                raise Exception("Invalid browse result items!")

            for json_item, json_diags in zip(json_result['items'], json_result['diagnostics']):
                diagnostics.append(DiagnosticModelJSON(json_diags['code']))
                if json_diags['code'] == 0:
                    resultItems = []
                    for item in json_item:
                        browseItem = BrowseResultItemModelJSON(item['identity'], item['displayName'],
                                                               item['relativePath'], item['type'], item['nodeClass'])
                        resultItems.append(browseItem)
                    requestResults.append(resultItems)
                else:
                    requestResults.append(None)
            continuationPoint = json_result['continuationPoint']
            if continuationPoint is None:
                break

        return BrowseResultModelJSON(requestResults, diagnostics)

    def _historyReadAggregate(self, aggregateType, queryPeriod, itemPath):

        url = self._webApi + '/opcua/v1/history/processed'

        if aggregateType.type == AggregateType.Trend.name:
            aggregatePath = ItemPathJSON('OPCUA.NodeId', None, "ns=1;i=245")
        elif aggregateType.type == AggregateType.PercentInStateZero.name:
            aggregatePath = ItemPathJSON('OPCUA.NodeId', None, "ns=1;i=270")
        elif aggregateType.type == AggregateType.PercentInStateNonZero.name:
            aggregatePath = ItemPathJSON('OPCUA.NodeId', None, "ns=1;i=271")
        else:
            basePath = "/Server/ServerCapabilities/AggregateFunctions/"
            aggregatePath = ItemPathJSON('OPCUA.BrowsePath', '', basePath + aggregateType.type)
        continuationPoint = None
        dataValues = []

        processingInterval = aggregateType.interval.total_seconds() * 1000

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(itemPath, continuationPoint, False)
            historyReadRequest = HistoryProcessedModelJSON(aggregatePath, processingInterval, queryPeriod.start,
                                                           queryPeriod.end, [itemPathAndCP])
            jsonRequest = historyReadRequest.toDict()
            session = self._authorizationService.getEpmSession()
            response = session.post(url, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result is None:
                raise Exception("historyReadAggregate Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadAggregate Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadAggregate Failed with error code: " + str(
                    json_result['diagnostics'][0]['code']) + " and message: '" + str(
                    json_result['diagnostics'][0]['message']) + "'")
            dataValues.extend(json_result['dataValues'][0]['dataValues'])
            continuationPoint = json_result['dataValues'][0]['continuationPoint']
            if continuationPoint is None:
                break
        util = NumpyExtras()
        numpyArray = util.numpyArrayFromDataValues(dataValues)
        return numpyArray

    def _historyReadAnnotation(self, queryPeriod:QueryPeriod, annotationPath:ItemPathJSON) -> List[Tuple[dt.datetime,str,str]]:

        url = self._webApi + '/opcua/v1/history/raw'

        continuationPoint = None
        annotations = []

        import dateutil.parser

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(annotationPath, continuationPoint, False)
            historyReadRequest = HistoryRawModelJSON(queryPeriod.start, queryPeriod.end, False, [itemPathAndCP])
            jsonRequest = historyReadRequest.toDict()
            session = self._authorizationService.getEpmSession()
            response = session.post(url, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result is None:
                raise Exception("historyReadAnnotation Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadAnnotation Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadAnnotation Failed with error code: " + str(
                    json_result['diagnostics'][0]['code']) + " and message: '" + str(
                    json_result['diagnostics'][0]['message']) + "'")

            for value in json_result['dataValues'][0]['dataValues']:
                if ('userName' in value['value'] and
                        'annotationTime' in value['value'] and
                        'message' in value['value']):
                    annotationTime = dateutil.parser.parse(value['value']['annotationTime'])
                    annotations.append((annotationTime, value['value']['userName'],
                                        value['value']['message']))
            # dataValues.extend(json_result['dataValues'][0]['dataValues'])
            continuationPoint = json_result['dataValues'][0]['continuationPoint']
            if continuationPoint is None:
                break

        return annotations

    from numpy.typing import NDArray
    def _historyReadEvent(self, queryPeriod, itemPath:ItemPathJSON, selectFields:List[str], whereClause = None) -> NDArray[Any]:
        url = self._webApi + '/opcua/v1/history/event'

        continuationPoint = None
        values = []
        types = []
        valueRanks = []

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(itemPath, continuationPoint, False)
            select = []
            for item in selectFields:
                select.append(SimpleAttributeOperand(item))
            filter = EventFilterModel(select, whereClause)

            historyEventRequest = HistoryEventModelJSON(queryPeriod.start, queryPeriod.end, filter, [itemPathAndCP])
            jsonRequest = historyEventRequest.toDict()
            session = self._authorizationService.getEpmSession()
            response = session.post(url, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result is None:
                raise Exception("historyReadEvent Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadEvent Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadEvent Failed with error code: " + str(
                    json_result['diagnostics'][0]['code']) + " and message: '" + str(
                    json_result['diagnostics'][0]['message']) + "'")

            if len(types) < 1:
                types = json_result['values'][0]['dataTypeIds']
                valueRanks = json_result['values'][0]['valueRanks']

            values.extend(json_result['values'][0]['events'])
            continuationPoint = json_result['values'][0]['continuationPoint']
            if continuationPoint is None:
                break

        util = NumpyExtras()
        numpyArray = util.numpyArrayFromEvents(selectFields, values, types, valueRanks)
        return numpyArray

    def _historyReadRaw(self, queryPeriod, itemPath, bounds=False, dataType=None):
        url = self._webApi + '/opcua/v1/history/raw'

        continuationPoint = None
        dataValues = []

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(itemPath, continuationPoint, False)
            historyReadRequest = HistoryRawModelJSON(queryPeriod.start, queryPeriod.end, bounds, [itemPathAndCP])
            jsonRequest = historyReadRequest.toDict()
            session = self._authorizationService.getEpmSession()
            response = session.post(url, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result is None:
                raise Exception("historyReadRaw Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadRaw Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadRaw Failed with error code: " + str(
                    json_result['diagnostics'][0]['code']) + " and message: '" + str(
                    json_result['diagnostics'][0]['message']) + "'")

            dataValues.extend(json_result['dataValues'][0]['dataValues'])
            continuationPoint = json_result['dataValues'][0]['continuationPoint']
            if continuationPoint is None:
                break
        util = NumpyExtras()
        numpyArray = util.numpyArrayFromDataValues(dataValues, dataType)
        return numpyArray

    def _queryModel(self, startNode:List[ItemPathJSON], browseNameFilter:str, typeFilter:ItemPathJSON, filter:QueryFilterContent):

        url = self._webApi + '/epm/v1/query/model'

        continuationPoint = None

        items = collections.OrderedDict()

        while True:
            model = QueryModelFilterJSON(continuationPoint, False,
                                   QueryResultMask.Name.value | QueryResultMask.Identity.value | QueryResultMask.Type.value | QueryResultMask.Path.value, 
                                   startNode, browseNameFilter,
                                   typeFilter,
                                   filter)
            jsonRequest = model.toDict()
            session = self._authorizationService.getEpmSession()
            response = session.post(url, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result is None:
                raise Exception("Query Failed no result")
            elif json_result['diagnostic']['code'] != 0:
                raise Exception(
                    "query Failed with error code: " + str(json_result['diagnostic']['code']) + " and message: '" + str(
                        json_result['diagnostic']['message']) + "'")
            continuationPoint = json_result['continuationPoint']

            typeIds = list(set(d['typeId']['path'] for d in json_result['items']))

            typesResults = self._read(list(ItemPathJSON('OPCUA.NodeId', None, d) for d in typeIds), [NodeAttributes.DisplayName.value] * len(typeIds)).items()
            types = {}
            index = 0
            for item in typesResults:
                types[typeIds[index]] = typesResults[index][0].value.value['text']

            index = 0
            from .itempathjson import fromDict
            for item in json_result['items']:
                if item['typeId'] == EpmNodeIds.BasicVariableType.value:
                    object = BasicVariable(self, fromDict(item['identity']), item['name'])
                elif item['typeId'] == EpmNodeIds.ExpressionVariableType.value:
                    object = EpmDataObject(self, item['name'], fromDict(item['identity']))
                else:
                    object = EpmModelObject(self, fromDict(item['identity']), item['path'], item['name'], types[item['typeId']['path']])
                items[item['path']] = object
                index = index + 1
            if continuationPoint is None:
                break
        return items

    def _query(self, browseNameFilter, descriptionFilter, euNameFilter, domainFilter, typeFilter):

        url = self._webApi + '/epm/v1/query'

        continuationPoint = None

        items = collections.OrderedDict()

        while True:
            model = QueryModelJSON(continuationPoint, False,
                                   QueryResultMask.Name.value | QueryResultMask.Identity.value, browseNameFilter,
                                   descriptionFilter, euNameFilter, typeFilter, domainFilter.value)
            jsonRequest = model.toDict()
            session = self._authorizationService.getEpmSession()
            response = session.post(url, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result is None:
                raise Exception("Query Failed no result")
            elif json_result['diagnostic']['code'] != 0:
                raise Exception(
                    "query Failed with error code: " + str(json_result['diagnostic']['code']) + " and message: '" + str(
                        json_result['diagnostic']['message']) + "'")
            continuationPoint = json_result['continuationPoint']

            resultTypes = self._browse(
                [ItemPathJSON('OPCUA.NodeId', '', item['identity']) for item in json_result['items']],
                EpmNodeIds.HasTypeDefinition.value).references()

            index = 0
            for item in json_result['items']:
                if resultTypes[index][0]._identity == EpmNodeIds.BasicVariableType.value:
                    dataObject = BasicVariable(self, ItemPathJSON('OPCUA.NodeId', None, item['identity']), item['name'])
                else:
                    dataObject = EpmDataObject(self, item['name'], ItemPathJSON('OPCUA.NodeId', None, item['identity']))
                items[item['name']] = dataObject
                index = index + 1
            if continuationPoint is None:
                break
        return items

    def _getAllDataObjects(self, attributes, reference, rootNode='/1:DataObjects') -> OrderedDict[str, EpmDataObject]:

        itemPath = ItemPathJSON('OPCUA.BrowsePath', '', rootNode)
        browseResult = self._browse([itemPath], reference.value, NodeClassMask.Variable).references()
        if len(browseResult) < 1:
            return []

        epmVariables = collections.OrderedDict()

        for item in browseResult[0]:
            if item._type == EpmNodeIds.BasicVariableType.value:
                epmVariables[item._displayName] = BasicVariable(self, ItemPathJSON('OPCUA.NodeId', None, item._identity), item._displayName)
            else:
                epmVariables[item._displayName] = EpmDataObject(self, item._displayName, ItemPathJSON('OPCUA.NodeId', None, item._identity))

        self._fillDataObjectsAttributes(list(epmVariables.values()), attributes)

        return epmVariables

    def _getDataObjectsFromIdentities(self, names, identities) -> OrderedDict[str, EpmDataObject]:
        epmVariables = collections.OrderedDict()
        doNames = []
        paths = []
        if type(names) is str:
            doNames.append(names)
        else:
            doNames = names

        # Verifica se todos os itens existem
        browseRequest = self._browse(identities, EpmNodeIds.HasTypeDefinition.value)
        resultReferences = browseRequest.references()

        epmVariables = collections.OrderedDict()
        for index in range(0, len(doNames)):
            if browseRequest.diagnostics()[index].code == 0:
                if resultReferences[index][0]._identity == EpmNodeIds.BasicVariableType.value:
                        epmVariables[doNames[index]] = BasicVariable(self, identities[index], doNames[index])
                else:
                        epmVariables[doNames[index]] = EpmDataObject(self, doNames[index], identities[index])
            else:
                epmVariables[doNames[index]] = None

        return epmVariables

    def _getDataObjects(self, names, attributes, rootNode='/1:DataObjects') -> OrderedDict[str, EpmDataObject]:
        epmVariables = collections.OrderedDict()
        doNames = []
        paths = []
        if type(names) is str:
            doNames.append(names)
            paths.append(ItemPathJSON('OPCUA.BrowsePath', '', rootNode + '/1:' + names))
        else:
            doNames = names
            for item in names:
                paths.append(ItemPathJSON('OPCUA.BrowsePath', '', rootNode + '/1:' + item))

        # Verifica se todos os itens existem
        epmVariables = collections.OrderedDict()
        existentNames = []
        identities = []
        readRequest = self._read(paths, [NodeAttributes.NodeId.value] * len(paths)).items()
        index = 0
        for item in readRequest:
            if item[1].code != 0:
                epmVariables[doNames[index]] = None
            else:
                existentNames.append(doNames[index])
                identities.append(ItemPathJSON('OPCUA.NodeId', None, item[0]._identity))
            index = index + 1

        if len(identities) < 1:
            return epmVariables

        resultTypes = self._browse(identities, EpmNodeIds.HasTypeDefinition.value).references()

        for index in range(0, len(existentNames)):
            if resultTypes[index][0]._identity == EpmNodeIds.BasicVariableType.value:
                epmVariables[existentNames[index]] = BasicVariable(self, identities[index], existentNames[index])
            else:
                epmVariables[existentNames[index]] = EpmDataObject(self, existentNames[index], identities[index])

        self._fillDataObjectsAttributes(list(epmVariables.values()), attributes)

        return epmVariables

    def _fillDataObjectsAttributes(self, dataObjects, attributes):

        propertyPaths = []
        if attributes == DataObjectAttributes.Unspecified.value:
            return dataObjects

        for index in range(0, len(dataObjects)):
            # for item in dataObjects:
            variable = dataObjects[index]
            if variable is None:
                continue
            if DataObjectAttributes.Name in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Name, ItemPathJSON('OPCUA.NodeId', None,
                                                                                        variable._encodePropertyIdentity(
                                                                                            EpmDataObjectAttributeIds.Name.value))))
            if DataObjectAttributes.Description in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Description, ItemPathJSON('OPCUA.NodeId', None,
                                                                                               variable._encodePropertyIdentity(
                                                                                                   EpmDataObjectAttributeIds.Description.value))))
            if DataObjectAttributes.EU in attributes:
                propertyPaths.append((variable, DataObjectAttributes.EU, ItemPathJSON('OPCUA.NodeId', None,
                                                                                      variable._encodePropertyIdentity(
                                                                                          EpmDataObjectAttributeIds.EU.value))))
            if DataObjectAttributes.LowLimit in attributes:
                propertyPaths.append((variable, DataObjectAttributes.LowLimit, ItemPathJSON('OPCUA.NodeId', None,
                                                                                            variable._encodePropertyIdentity(
                                                                                                EpmDataObjectAttributeIds.LowLimit.value))))
            if DataObjectAttributes.HighLimit in attributes:
                propertyPaths.append((variable, DataObjectAttributes.HighLimit, ItemPathJSON('OPCUA.NodeId', None,
                                                                                             variable._encodePropertyIdentity(
                                                                                                 EpmDataObjectAttributeIds.HighLimit.value))))
            if DataObjectAttributes.Clamping in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Clamping, ItemPathJSON('OPCUA.NodeId', None,
                                                                                            variable._encodePropertyIdentity(
                                                                                                EpmDataObjectAttributeIds.Clamping.value))))
            if DataObjectAttributes.Domain in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Domain, ItemPathJSON('OPCUA.NodeId', None,
                                                                                          variable._encodePropertyIdentity(
                                                                                              EpmDataObjectAttributeIds.Domain.value))))
            if DataObjectAttributes.Active in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Active, ItemPathJSON('OPCUA.NodeId', None,
                                                                                          variable._encodePropertyIdentity(
                                                                                              EpmDataObjectAttributeIds.Active.value))))
            if DataObjectAttributes.TagType in attributes:
                propertyPaths.append((variable, DataObjectAttributes.TagType, ItemPathJSON('OPCUA.NodeId', None,
                                                                                          variable._encodePropertyIdentity(
                                                                                              EpmDataObjectAttributeIds.TagType.value))))

        chunks = [propertyPaths[x:x + 1000] for x in range(0, len(propertyPaths), 1000)]

        for chunk in chunks:
            if len(chunk) > 0:
                readResults = self._read(list(zip(*chunk))[2], [13] * len(chunk)).items()
                for index in range(0, len(readResults)):
                    dataObject = chunk[index][0]
                    attributeId = chunk[index][1]
                    if readResults[index][1].code == 0:
                        dataObject._setAttribute(attributeId, readResults[index][0].value.value)

            # Private Methods

    def _translatePathToBrowsePath(self, path):
        if len(path) == 0:
            return ''
        if path[0] == '/':
            path = path[1:]

        browsePath = ''
        splittedPath = path.split('/')
        for relativePath in splittedPath:

            splittedRelativePath = relativePath.split(':')
            currentPath = relativePath
            if len(splittedRelativePath) == 1:
                currentPath = '1:' + relativePath
            browsePath = browsePath + '/' + currentPath

        return browsePath

class BadArgumentException(Exception):
    pass
