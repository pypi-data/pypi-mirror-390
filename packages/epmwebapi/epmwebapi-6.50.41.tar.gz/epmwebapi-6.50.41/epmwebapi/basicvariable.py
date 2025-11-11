from .itempathjson import ItemPathJSON
import datetime as dt
from .datavaluejson import DataValueJSON
from .epmvariable import EpmVariable
from .epmproperty import EpmProperty
from .dataobjectattributes import DataObjectAttributes
from .epmnodeids import EpmNodeIds
from .epmdataobject import EpmDataObject, ClampingMode
from .basicvariablepropertymask import BasicVariablePropertyMask
from .historyupdatetype import HistoryUpdateType
from .queryperiod import QueryPeriod
import numpy as np

from enum import Enum

from typing import Union

class TagType(Enum):
    """
    Enumeration with all types of Tags.
    """
    SourceType = 0

    Bit = 1

    Int = 2

    UInt = 3

    Float = 4

    Double = 5

    String = 6

    DateTime = 8

class DataTypeId(Enum):
    """
    Enumeration with all types of IDS for data types.
    """
    SourceType = None

    Unknown = 0

    Bit = 1

    Int = 8 # Int64 Code

    UInt = 9 # UInt64 code

    Float = 10

    Double = 11

    String = 12

    DateTime = 13

    ByteString = 15

    NodeId = 17

    DataValue = 23

class BasicVariable(EpmDataObject):
    """
    Class representing an **EPM** Basic Variable.
    """

    def __init__(self, epmConnection, itemPath, name, description = None, tagType = None, realTimeEnabled = None, deadBandFilter = None, 
                 deadBandUnit = None, eu = None, lowLimit = None, highLimit = None, scaleEnable = None, inputLowLimit = None, 
                 inputHighLimit = None, clamping = None, domain = None, interface = None, ioTagAddress = None, processingEnabled = None, 
                 isRecording = None, isCompressing = None, storeMillisecondsEnabled = None, storageSet = None, active = None):
        super().__init__(epmConnection, name, itemPath)
        self._name = name
        self._newName = None
        self._description = description
        self._tagType = TagType.SourceType.value if tagType == None else TagType[tagType].value if isinstance(tagType, str) else tagType if isinstance(tagType, int) or tagType is None else tagType.value
        self._realTimeEnabled = realTimeEnabled
        self._deadBandFilter = deadBandFilter
        self._deadBandUnit = deadBandUnit
        self._eu = eu
        self._lowLimit = lowLimit
        self._highLimit = highLimit
        self._scaleEnable = scaleEnable
        self._inputLowLimit = inputLowLimit
        self._inputHighLimit = inputHighLimit
        self._clamping = clamping if isinstance(clamping, int) or clamping is None else clamping.value
        self._domain = domain
        self._interface = interface
        self._ioTagAddress = ioTagAddress
        self._processingEnabled = processingEnabled
        self._isRecording = isRecording
        self._isCompressing = isCompressing
        self._storeMillisecondsEnabled = storeMillisecondsEnabled
        self._storageSet = storageSet
        self._active = active

    @property
    def name(self) -> str:
      """
      Gets or sets the name of this Basic Variable.

      :param value: A new name for this Basic Variable.
      :type value: str
      :return: A `str` representing the name of this Basic Variable.
      :rtype: str
      """
      return self._name

    @name.setter
    def name(self, value:str):
      if self._name == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Name.value
      self._newName = value

    @property
    def tagType(self) -> TagType:
      """
      Gets or sets the type of Tag of this Basic Variable.

      :param value: A new type of Tag for this Basic Variable (An `int` or a `TagType` value).
      :type value: TagType
      :return: A `TagType` value representing the type of Tag.
      :rtype: TagType
      """
      return TagType(self._tagType) if self._tagType is not None else None

    @tagType.setter
    def tagType(self, value:Union[int,TagType]):
      if isinstance(value, int) or value is None:
        if self._tagType == value:
          return
        self._tagType = value
      else:
        if self._tagType == value.value:
          return
        self._tagType = value.value
      self._changeMask = self._changeMask | BasicVariablePropertyMask.TagType.value

    @property
    def realTimeEnabled(self) -> bool:
      """
      Gets or sets whether real-time is enabled in this Basic Variable.

      :param value: True if real-time must be enabled or False if real-time must be disabled.
      :type value: bool
      :return: True if real-time is enabled or False if real-time is not enabled.
      :rtype: bool
      """
      return self._realTimeEnabled

    @realTimeEnabled.setter
    def realTimeEnabled(self, value:bool):
      if self._realTimeEnabled == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.RealTimeEnabled.value
      self._realTimeEnabled = value

    @property
    def deadBandFilter(self) -> float:
      """
      Gets or sets a dead band filter for this Basic Variable.

      :param value: If `value` is equal to 0 (zero), then dead band filter is disabled.
      :type value: float
      :return: Dead band filter from this Basic Variable as a `float` number.
      :rtype: float
      """
      return self._deadBandFilter

    @deadBandFilter.setter
    def deadBandFilter(self, value:float):
      if self._deadBandFilter == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.DeadBandFilter.value
      self._deadBandFilter = value
        
    @property
    def deadBandUnit(self) -> str:
      """
      Gets or sets the dead band unit for this Basic Variable.

      :param value: A dead band unit for this Basic Variable. Possible values are **Absolute**, **PercentOfEURange**, **PercentOfValue**, or **None**.
      :type value: str
      :return: Dead band unit from this Basic Variable. Possible values are **Absolute**, **PercentOfEURange**, **PercentOfValue**, or **None**.
      :rtype: str
      """
      return self._deadBandUnit

    @deadBandUnit.setter
    def deadBandUnit(self, value:str):
      if self._deadBandUnit == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.DeadBandUnit.value
      self._deadBandUnit = value

    @property
    def scaleEnable(self) -> bool:
      """
      Enables or disables a scale for this Basic Variable. Deprecated, please use `processingEnabled` instead.

      :param value: True to enable a scale or False to disable a scale.
      :type value: bool
      :return: True if a scale is enabled or False if a scale is disabled.
      :rtype: bool
      """
      return self._scaleEnable

    @scaleEnable.setter
    def scaleEnable(self, value:bool):
      if self._scaleEnable == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.ScaleEnable.value
      self._scaleEnable = value

    @property
    def inputLowLimit(self) -> float:
      """
      Gets or sets a low limit to a scale.

      :param value: A `float` number to set a low limit to a scale.
      :type value: float
      :return: A `float` number representing a scale's low limit.
      :rtype: float
      """
      return self._inputLowLimit

    @inputLowLimit.setter
    def inputLowLimit(self, value:float):
      if self._inputLowLimit == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.InputLowLimit.value
      self._inputLowLimit = value
        
    @property
    def inputHighLimit(self) -> float:
      """
      Gets or sets a high limit to a scale.

      :param value: A `float` number to set a high limit to a scale.
      :type value: float
      :return: A `float` number representing a scale's high limit.
      :rtype: float
      """
      return self._inputHighLimit

    @inputHighLimit.setter
    def inputHighLimit(self, value:float):
      if self._inputHighLimit == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.InputHighLimit.value
      self._inputHighLimit = value
        
    @property
    def interface(self) -> str:
      """
      Gets or sets the name of this Basic Variable's interface, in the format **interfaceServerName/interfaceName**.

      :param value: A `str` with the name of an interface.
      :type value: str
      :return: The name of this Basic Variable's interface.
      :rtype: str
      """
      return self._interface

    @interface.setter
    def interface(self, value:str):
      if self._interface == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.Interface.value
      self._interface = value
        
    @property
    def ioTagAddress(self) -> str:
      """
      Gets or sets the interface's source address for this Basic Variable.

      :param value: A `str` with the name of an interface's source address.
      :type value: str
      :return: A `str` representing the interface's source address for this Basic Variable.
      :rtype: str
      """
      return self._ioTagAddress

    @ioTagAddress.setter
    def ioTagAddress(self, value:str):
      if self._ioTagAddress == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.IoTagAddress.value
      self._ioTagAddress = value
        
    @property
    def processingEnabled(self) -> bool:
      """
      Enables or disables a scale for this Basic Variable.

      :param value: True to enable a scale or False to disable a scale.
      :type value: bool
      :return: True if a scale is enabled or False if a scale is disabled.
      :rtype: bool
      """
      return self._processingEnabled

    @processingEnabled.setter
    def processingEnabled(self, value:bool):
      if self._processingEnabled == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.ProcessingEnabled.value
      self._processingEnabled = value
        
    @property
    def isRecording(self) -> bool:
      """
      Enables or disables recording in this Basic Variable.

      :param value: True to enable recording or False to disable recording.
      :type value: bool
      :return: True if recording is enabled or False if recording is disabled.
      :rtype: bool
      """
      return self._isRecording

    @isRecording.setter
    def isRecording(self, value:bool):
      if self._isRecording == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.IsRecording.value
      self._isRecording = value
        
    @property
    def isCompressing(self) -> bool:
      """
      Enables or disables compressing in this Basic Variable.

      :param value: True to enable compressing or False to disable compressing.
      :type value: bool
      :return: True if compressing is enabled or False if compressing is disabled.
      :rtype: bool
      """
      return self._isCompressing

    @isCompressing.setter
    def isCompressing(self, value:bool):
      if self._isCompressing == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.IsCompressing.value
      self._isCompressing = value
        
    @property
    def storeMillisecondsEnabled(self) -> bool:
      """
      Enables or disables storing milliseconds in this Basic Variable.

      :param value: True to enable storing milliseconds or False to disable storing milliseconds.
      :type value: bool
      :return: True if storing milliseconds is enabled or False if storing milliseconds is disabled.
      :rtype: bool
      """
      return self._storeMillisecondsEnabled 

    @storeMillisecondsEnabled.setter
    def storeMillisecondsEnabled(self, value:bool):
      if self._storeMillisecondsEnabled == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.StoreMillisecondsEnabled.value
      self._storeMillisecondsEnabled = value
        
    @property
    def storageSet(self) -> str:
      """
      Gets or sets the name of a Storage Set for this Basic Variable.

      :param value: A `str` with the name of a Storage Set for this Basic Variable.
      :type value: str
      :return: A `str` representing the Storage Set for this Basic Variable.
      :rtype: str
      """
      return self._storageSet

    @storageSet.setter
    def storageSet(self, value:str):
      if self._storageSet == value:
        return
      self._changeMask = self._changeMask | BasicVariablePropertyMask.StorageSet.value
      self._storageSet = value


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
      elif attributeId == DataObjectAttributes.TagType:
        self._tagType = value

    #Public Methods

    def historyReadRaw(self, queryPeriod:QueryPeriod, bounds:bool=False) -> np.ndarray:
      """
      Returns raw values of this Basic Variable from the configured `epmwebapi.queryperiod.QueryPeriod`.

      :param queryPeriod: A period of time for querying raw values.
      :type queryPeriod: QueryPeriod
      :param bounds: True if the bound value must be returned or False if the bound value must not be returned. Default value is False.
      :type bounds: bool
      :return: A numpy `ndarray` with raw values from the configured period, including **Value**, **Timestamp**, and **Quality**.
      :rtype: ndarray
      """
      if self.tagType != None and self.tagType != TagType.SourceType:
            if self._hasFlag(BasicVariablePropertyMask.TagType):
                raise Exception("Save the basic variable new tagType before writing a value")
            dataType = DataTypeId[self.tagType.name].value
            return self._epmConnection._historyReadRaw(queryPeriod, self._itemPath, bounds, "i=" + str(dataType))
      else:
            return self._epmConnection._historyReadRaw(queryPeriod, self._itemPath, bounds)

    def write(self, value, timestamp:dt.datetime=dt.datetime.now(dt.timezone.utc), quality:int=0):
      """
      Writes a **Value**, a **Timestamp**, and a **Quality** to this Basic Variable's real-time.

      :param value: A value as a `float`, an `int`, a `str`, or a `datetime`.
      :type value: [float | int | str | datetime]
      :param timestamp: An optional timestamp for the value. Default is `dt.datetime.now`.
      :type timestamp: datetime
      :param quality: An optional quality for the value. Default is 0 (zero).
      :type: int
      """
      if self.tagType != None and self.tagType != TagType.SourceType:
          if self._hasFlag(BasicVariablePropertyMask.TagType):
              raise Exception("Save the basic variable new tagType before writing a value")
          dataType = DataTypeId[self.tagType.name].value
          return self._epmConnection._write([self._itemPath], [13], [DataValueJSON(value, quality, timestamp,
                                                                                    dataTypeId="i="+str(dataType))])
      else:
        return self._epmConnection._write([self._itemPath], [13], [DataValueJSON(value, quality, timestamp)])

    def historyUpdate(self, values:np.ndarray):
      """
      Writes an array of values to this Basic Variable, including **Value**, **Timestamp**, and **Quality**.

      ### Example

      `array = np.empty([valuesCount], dtype=np.dtype([('Value', '>f4'), ('Timestamp', 'object'), ('Quality', 'object')]))`

      :param values: A numpy `ndarray` with values to write.
      :type values: np.ndarray
      """
      if self.tagType != None and self.tagType != TagType.SourceType:
          if self._hasFlag(BasicVariablePropertyMask.TagType):
              raise Exception("Save the basic variable new tagType before using historyUpdate")
          dataType = DataTypeId[self.tagType.name].value
          return self._epmConnection._historyUpdate(HistoryUpdateType.Update.value, [ self._itemPath ], [ values ],
                                                    dataTypeId="i="+str(dataType))
      else:
          return self._epmConnection._historyUpdate(HistoryUpdateType.Update.value, [ self._itemPath ], [ values ])


    def save(self):
      """
      Saves the configuration of this Basic Variable to an **EPM** Server.
      """
      self._epmConnection.updateBasicVariable(self._name, 
                                              self._newName if self._hasFlag(BasicVariablePropertyMask.Name) else None,
                                              self._description if self._hasFlag(BasicVariablePropertyMask.Description) else None,
                                              self._tagType if self._hasFlag(BasicVariablePropertyMask.TagType) else None,
                                              self._realTimeEnabled if self._hasFlag(BasicVariablePropertyMask.RealTimeEnabled) else None,
                                              self._deadBandFilter if self._hasFlag(BasicVariablePropertyMask.DeadBandFilter) else None,
                                              self._deadBandUnit if self._hasFlag(BasicVariablePropertyMask.DeadBandUnit) else None,
                                              self._eu if self._hasFlag(BasicVariablePropertyMask.Eu) else None,
                                              self._lowLimit if self._hasFlag(BasicVariablePropertyMask.LowLimit) else None,
                                              self._highLimit if self._hasFlag(BasicVariablePropertyMask.HighLimit) else None,
                                              self._scaleEnable if self._hasFlag(BasicVariablePropertyMask.ScaleEnable) else None,
                                              self._inputLowLimit if self._hasFlag(BasicVariablePropertyMask.InputLowLimit) else None,
                                              self._inputHighLimit if self._hasFlag(BasicVariablePropertyMask.InputHighLimit) else None,
                                              self._clamping if self._hasFlag(BasicVariablePropertyMask.Clamping) else None,
                                              self._domain if self._hasFlag(BasicVariablePropertyMask.Domain) else None,
                                              self._interface if self._hasFlag(BasicVariablePropertyMask.Interface) else None,
                                              self._ioTagAddress if self._hasFlag(BasicVariablePropertyMask.IoTagAddress) else None,
                                              self._processingEnabled if self._hasFlag(BasicVariablePropertyMask.ProcessingEnabled) else None,
                                              self._isRecording if self._hasFlag(BasicVariablePropertyMask.IsRecording) else None,
                                              self._isCompressing if self._hasFlag(BasicVariablePropertyMask.IsCompressing) else None,
                                              self._storeMillisecondsEnabled if self._hasFlag(BasicVariablePropertyMask.StoreMillisecondsEnabled) else None,
                                              self._storageSet if self._hasFlag(BasicVariablePropertyMask.StorageSet) else None)

      if (self._newName != None and self._hasFlag(BasicVariablePropertyMask.Name)):
        self._name = self._newName

      self._changeMask = BasicVariablePropertyMask.Unspecified.value

      


    def copy(self, newName:str, description:str=None, tagType:Union[str,TagType]=None, realTimeEnabled:bool=None, deadBandFilter:float=None,
                            deadBandUnit:str=None,
                            eu:str=None, lowLimit:float=None, highLimit:float=None, scaleEnable:bool=None, inputLowLimit:float=None,
                            inputHighLimit:float=None, clamping:str=None,
                            domain:str=None, interface:str=None, ioTagAddress:str=None, processingEnabled:bool=None, isRecording:bool=None,
                            isCompressing:bool=None,
                            storeMillisecondsEnabled:bool=None, storageSet:bool=None):
      """
      Creates a new Basic Variable on an **EPM** Server by merging the current values of properties and parameters specified.

      :param newName: A name for the new Basic Variable.
      :type newName: str
      :param description: An optional description for the new Basic Variable.
      :type: str
      :param tagType: An optional `TagType` for the new Basic Variable. Possible values are **SourceType**, **Bit**, **Int**, **UInt**, **Float**, **Double**, **String**, **DateTime**. Default value is **None**.
      :type tagType: `TagType`
      :param realTimeEnabled: An optional `bool` value indicating whether real-time is enabled or not. Default value is **None**.
      :type realTimeEnabled: bool
      :param deadbandFilter: An optional `float` value indicating a dead band filter. Default value is **None**.
      :type deadbandFilter: float
      :param deadbandUnit: An optional `str` indicating a dead band unit. Possible values are **Absolute**, **PercentOfEURange**, or **PercentOfValue**. Default value is **None**.
      :type deadbandUnit: str
      :param eu: An optional `str` indicating an engineering unit. Default value is **None**.
      :param lowLimit: An optional `float` value indicating a low limit. Default value is **None**.
      :type lowLimit: float
      :param highLimit: An optional `float` value indicating a high limit. Default value is **None**.
      :type highLimit: float
      :param scaleEnable: An optional `bool` value indicating whether the scale is enabled. Default value is **None**.
      :type scaleEnable: bool
      :param inputLowLimit: An optional `float` value indicating an input low limit. Default value is **None**.
      :type inputLowLimit: float
      :param inputHighLimit: An optional `float` value indicating an input high limit. Default value is **None**.
      :type inputHighLimit: float
      :param clamping: An optional `str` value indicating a type of clamping. Possible values are **ClampToRange** or **Discard**. Default value is **None**.
      :type clamping: str
      :param domain: An optional `str` indicating a type of domain for this Basic Variable. Possible values are **Continuous** or **Discrete**. Default value is **None**.
      :type domain: str
      :param interface: An optional `str` indicating a name of an interface, in the format **interfaceServerName/interfaceName**. Default value is **None**.
      :type interface: str
      :param ioTagAddress: An optional `str` indicating the interface's source path. Default value is **None**.
      :type ioTagAddress: str
      :param processingEnabled: An optional `bool` value indicating whether the scale is enabled. Default value is **None**.
      :type processingEnabled: bool
      :param isRecording: An optional `bool` value indicating whether this Basic Variable is recording. Default value is **None**.
      :type isRecording: bool
      :param isCompressing: An optional `bool` value indicating whether this Basic Variable is compressing values. Default value is **None**.
      :type isCompressing: bool
      :param storeMillisecondsEnabled: An optional `bool` value indicating whether this Basic Variable is storing milliseconds. Default value is **None**.
      :type storeMillisecondsEnabled: bool
      :param storageSet: An optional `bool` value indicating whether this Basic Variable contains a name of a Storage Set. Default value is **None**.
      :type storageSet: bool
      :return: A new `BasicVariable` object.
      :rtype: BasicVariable
      """
      return self._epmConnection.createBasicVariable(newName,
                                              description = description if description != None else self._description,
                                              tagType = tagType if tagType != None else self._tagType,
                                              realTimeEnabled = realTimeEnabled if realTimeEnabled != None else self._realTimeEnabled,
                                              deadBandFilter = deadBandFilter if deadBandFilter != None else self._deadBandFilter,
                                              deadBandUnit = deadBandUnit if deadBandUnit != None else self._deadBandUnit,
                                              eu = eu if eu != None else self._eu,
                                              lowLimit = lowLimit if lowLimit != None else self._lowLimit,
                                              highLimit = highLimit if highLimit != None else self._highLimit,
                                              scaleEnable = scaleEnable if scaleEnable != None else self._scaleEnable,
                                              inputLowLimit = inputLowLimit if inputLowLimit != None else self._inputLowLimit,
                                              inputHighLimit = inputHighLimit if inputHighLimit != None else self._inputHighLimit,
                                              clamping = clamping if clamping != None else self._clamping,
                                              domain = domain if domain != None else self._domain,
                                              interface = interface if interface != None else self._interface,
                                              ioTagAddress = ioTagAddress if ioTagAddress != None else self._ioTagAddress,
                                              processingEnabled = processingEnabled if processingEnabled != None else self._processingEnabled,
                                              isRecording = isRecording if isRecording != None else self._isRecording,
                                              isCompressing = isCompressing if isCompressing != None else self._isCompressing,
                                              storeMillisecondsEnabled = storeMillisecondsEnabled if storeMillisecondsEnabled != None else self._storeMillisecondsEnabled,
                                              storageSet = storageSet if storageSet != None else self._storageSet)

    def delete(self) -> bool:
      """
      Deletes a Basic Variable.

      :return: True if the Basic Variable was deleted or False otherwise.
      :rtype: bool
      """
      result = self._epmConnection.deleteBasicVariable([ self._name ])
      return result[0]

    def _hasFlag(self, flag):
      return self._changeMask & flag.value == flag.value




class BasicVariableAlreadyExistsException(Exception):
    pass

class BasicVariableInvalidNameException(Exception):
    pass

class StorageSetDoesNotExistException(Exception):
    pass

class InterfaceDoesNotExistException(Exception):
    pass

