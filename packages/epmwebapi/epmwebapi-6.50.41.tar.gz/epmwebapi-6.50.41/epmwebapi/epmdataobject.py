import pytz

from .itempathjson import ItemPathJSON
import datetime as dt
from .queryperiod import QueryPeriod
from .datavaluejson import DataValueJSON
from .epmvariable import EpmVariable
from .epmproperty import EpmProperty
from .dataobjectattributes import DataObjectAttributes
from .epmnodeids import EpmNodeIds
from .basicvariablepropertymask import BasicVariablePropertyMask

from enum import Enum
import collections

from typing import Union, List, Tuple, OrderedDict


class EpmDataObjectPropertyNames(Enum):
    """
    Enumeration with all types of properties of EPM Data Objects.
    """
    Name = "4:Name"

    Description = "4:Description"

    EU = "0:EngineeringUnits"

    LowLimit = "4:RangeLow"

    HighLimit = "4:RangeHigh"

    Clamping = "4:RangeClamping"

    Domain = "4:Discrete"

    Annotations = "4:Annotations"


class EpmDataObjectAttributeIds(Enum):
    """
    Enumeration with all types of attribute IDs of EPM Data Objects.
    """
    Name = 1

    Description = 2

    TagType = 3

    LowLimit = 15

    HighLimit = 16

    Clamping = 17

    Domain = 21

    EU = 22

    Active = 23

    Annotations = 900


class ClampingMode(Enum):
    """
    Enumeration with all types of clamping modes.
    """
    NoneClamping = 0

    Discard = 1

    ClampToRange = 2


def getDiscreteValue(domain):
  if domain == 'Discrete':
    return True
  elif domain == 'Continuous':
    return False
  else:
    return None

def getDomainValue(discrete):
  if discrete == None:
    return None
  elif discrete:
    return 'Discrete'
  else:
    return 'Continuous'

class EpmDataObject(EpmVariable):
    """
    Class representing a DataObject
    """

    def __init__(self, epmConnection, name, itemPath):
        super().__init__(epmConnection, name, '/DataObjects/' + name, itemPath)
        self._changeMask = BasicVariablePropertyMask.Unspecified.value
        self._itemPath = itemPath
        self._description = None
        self._eu = None
        self._highLimit = None
        self._lowLimit = None
        self._clamping = None
        self._domain = None
        self._active = None

    ### Properties
    @property
    def description(self) -> str:
      """
      Returns or sets the description of a Data Object.
      :param value: A description for this Data Object.
      :type: str
      :return: The description of a Data Object.
      :rtype: str
      """
      return self._description

    @description.setter
    def description(self, value:str):
      if self._description == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Description.value
      self._description = value

    @property
    def eu(self) -> str:
      """
      Returns or sets the engineering unit of a Data Object.

      :param value: An engineering unit for this Data Object.
      :type value: str
      :return: The engineering unit of a Data Object.
      :rtype: str
      """
      return self._eu

    @eu.setter
    def eu(self, value:str):
      if self._eu == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Eu.value
      self._eu = value

    @property
    def lowLimit(self) -> float:
      """
      Returns or sets the clamping low limit of a Data Object.

      :param value: A new clamping low limit for this Data Object.
      :type value: float
      :return: The clamping low limit of a Data Object.
      :rtype: float
      """
      return self._lowLimit

    @lowLimit.setter
    def lowLimit(self, value:float):
      if self._lowLimit == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.LowLimit.value
      self._lowLimit = value

    @property
    def highLimit(self) -> float:
      """
      Returns or sets the clamping high limit of a Data Object.

      :param value: A new clamping high limit for this Data Object.
      :type value: float
      :return: The clamping high limit of a Data Object.
      :rtype: float
      """
      return self._highLimit

    @highLimit.setter
    def highLimit(self, value:float):
      if self._highLimit == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.HighLimit.value
      self._highLimit = value

    @property
    def clamping(self) -> str:
      """
      Returns or sets the clamping type of a Data Object.

      :param value: Clamping type for this Data Object. Possible values are **ClampToRange**, **Discard**, or **None**.
      :type value: str
      :return: The current clamping type of this Data Object.
      :rtype: str
      """
      return ClampingMode(self._clamping) if self._clamping is not None else None

    @clamping.setter
    def clamping(self, value:str):
      if isinstance(value, int) or value is None:
          if self._clamping == value:
              return
          self._clamping = value
      else:
          if self._clamping == value.value:
              return
          self._clamping = value.value
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Clamping.value

    @property
    def domain(self) -> str:
      """
      Returns or sets the domain of a Data Object.

      :param value: Domain for this Data Object. Possible values are **Continuous**, **Discrete** or **None**.
      :type value: str
      :return: The domain of this Data Object.
      :rtype: str
      """
      return self._domain

    @domain.setter
    def domain(self, value:str):
      if self._domain == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Domain.value
      self._domain = value

    @property
    def active(self) -> bool:
      """
      :return: True if a Data Object is active or False if it is not.
      :rtype: bool
      """
      return self._active


    def readAnnotations(self, start:dt.datetime, end:dt.datetime) -> List[Tuple[dt.datetime,str,str]]:
      """
      Returns a list of Annotations registered for the informed period.

      :param start: Starting period.
      :type start: dt.datetime
      :param end: Ending period.
      :type end: dt.datetime
      :return: A list with all Annotations found.
      :rtype: List[dt.datetime,str,str]
      """
      queryPeriod = QueryPeriod(start, end)
      annotationPath = ItemPathJSON('OPCUA.NodeId', None, self._encodePropertyIdentity(EpmDataObjectAttributeIds.Annotations.value))
      return self._epmConnection._historyReadAnnotation(queryPeriod, annotationPath)

    def deleteAnnotations(self, start:dt.datetime, end:dt.datetime, allUsers:bool=False):
      """
      Removes Annotations from the informed period.

      :param start: Starting period.
      :type start: dt.datetime
      :param end: Ending period.
      :type end: dt.datetime
      :param allUsers: A `bool` indicating whether to delete Annotations from all users or not. Default is False.
      """
      userName = self._epmConnection._authorizationService._userName
      result = self.readAnnotations(start, end)
      deletedItems = []
      for index in range(len(result)):
        if allUsers or result[index][1] == userName:
          deletedItems.append(result[index])

      if len(deletedItems) == 0:
        return

      annotationPath = ItemPathJSON('OPCUA.NodeId', None, self._encodePropertyIdentity(EpmDataObjectAttributeIds.Annotations.value))
      from .performupdatetype import PerformUpdateType
      self._epmConnection._historyUpdateAnnotation(annotationPath, PerformUpdateType.Remove.value, deletedItems)

    def writeAnnotation(self, timestamp:dt.datetime, message:str, override:bool=True):
      """
      Writes an Annotation.

      :param timestamp: Timestamp of the Annotation to write.
      :type timestamp: dt.datetime
      :param message: Message of the Annotation to write.
      :type message: str
      :param override: A `bool` indicating whether this message must override an existing Annotation or not. Default is True.
      """
      timestamp = timestamp.astimezone(pytz.UTC)
      annotationPath = ItemPathJSON('OPCUA.NodeId', None, self._encodePropertyIdentity(EpmDataObjectAttributeIds.Annotations.value))
      userName = self._epmConnection._authorizationService._context._userName
      annotations = [ (timestamp, userName, message) ]
      from .performupdatetype import PerformUpdateType
      if override:
        results = self.readAnnotations(timestamp, timestamp + dt.timedelta(seconds=1))
        for index in range(len(results)):
          if results[index][1] == userName and self._compareDatetime(results[index][0].astimezone(pytz.UTC), timestamp):
            return self._epmConnection._historyUpdateAnnotation(annotationPath, PerformUpdateType.Update.value, annotations)
      return self._epmConnection._historyUpdateAnnotation(annotationPath, PerformUpdateType.Insert.value, annotations)

    def readAttributes(self):
      """
      Reads all attributes of a Data Object.
      """
      self._epmConnection._fillDataObjectsAttributes([ self ], DataObjectAttributes.All)

    def enumProperties(self) -> OrderedDict[str,EpmProperty]:
      """
      :return: An Ordered Dictionary with all properties of a Data Object.
      :rtype: OrderedDict[str,EpmProperty]
      """
      result = self._epmConnection._browse([ self._itemPath ], EpmNodeIds.HasProperty.value).references()
      childProperties = collections.OrderedDict()
      for item in result[0]:
        childProperties[item._displayName] = EpmProperty(self._epmConnection, item._displayName, self._path + '/' + item._displayName, item._identity)
      return childProperties

    #Private Methods
    
    def _compareDatetime(self, datetime1, datetime2):
      return (datetime1.year == datetime2.year and
              datetime1.month == datetime2.month and
              datetime1.day == datetime2.day and
              datetime1.hour == datetime2.hour and
              datetime1.minute == datetime2.minute and
              datetime1.second == datetime2.second and
              datetime1.microsecond == datetime2.microsecond)

    def _setAttribute(self, attributeId, value):
      if attributeId == DataObjectAttributes.Description:
        self._description = value if value is not None else ""
      elif attributeId == DataObjectAttributes.EU:
        self._eu = value['displayName'] if value is not None else value
      elif attributeId == DataObjectAttributes.HighLimit:
        self._highLimit = value
      elif attributeId == DataObjectAttributes.LowLimit:
        self._lowLimit = value
      elif attributeId == DataObjectAttributes.Clamping:
        self._clamping = value
      elif attributeId == DataObjectAttributes.Domain:
        self._domain = 'Discrete' if value else 'Continuous'
      elif attributeId == DataObjectAttributes.Active:
        self._active = value


    def _encodePropertyIdentity(self, propertyIdentity):

      nodeIdSplitted = self._itemPath.relativePath.split(';')
      if len(nodeIdSplitted) != 2:
        raise Exception('Invalid nodeId format')
      matches = [x for x in nodeIdSplitted if x.startswith('i=')]
      if len(matches) != 1:
        raise Exception('Invalid nodeId type')

      objectIdentity = int(matches[0][2:])
      SignatureLSB = 0xFE;
      SignatureMSB = 0xCA;

      ret = [ 0 ] * 8

      ret[0] = ((propertyIdentity & 0x000000FF) >> (0 * 8));
      ret[1] = ((propertyIdentity & 0x0000FF00) >> (1 * 8));
      ret[2] = ((objectIdentity   & 0x000000FF) >> (0 * 8));
      ret[3] = ((objectIdentity   & 0x0000FF00) >> (1 * 8));
      ret[4] = ((objectIdentity   & 0x00FF0000) >> (2 * 8));
      ret[5] = ((objectIdentity   & 0xFF000000) >> (3 * 8));
      ret[6] = SignatureLSB;
      ret[7] = SignatureMSB;

      import base64

      return 'ns=1;b=' + base64.b64encode(bytes(ret)).decode("utf-8") 




