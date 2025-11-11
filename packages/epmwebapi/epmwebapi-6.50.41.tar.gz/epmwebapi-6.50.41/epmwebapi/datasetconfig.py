import datetime
from enum import Enum
from dateutil.relativedelta import relativedelta
import re
import os
import ctypes

from .datasetpen import DatasetPen
from .queryperiod import QueryPeriod

import datetime

import numpy as np

from typing import Union, List

class PeriodUnit(Enum):
    """
    Enumeration with all available period units.
    """
    Second = 1

    Minute = 2

    Hour = 3

    Day = 4

    Month = 5


class DatasetConfig(object):
    """
    Class representing an **EPM** Dataset.
    """

    REGEX_PATTERN = r'^[^a-z_]+|[^a-z0-9\.\:\%\&\@\!\-\#_]+|[^a-z0-9]+$|.{{{0},}}'
    NAME_MAX_SIZE = 50
    DESCRIPTION_MAX_SIZE = 500

    def __init__(self, connection, name, description = None):
        import os
        import clr
        clr.AddReference(os.path.dirname(os.path.abspath(__file__)) + '/dll_references/EpmData')

        from Elipse.Epm.Common import DatasetAndChartData, DatasetData

        self._connection = connection
        self._startTime = None
        self._endTime = None
        self._datasetPens = []
        self.setName(name)
        self.recentPeriodConfig(1, PeriodUnit.Hour)
        self._description = description
        self._datasetAndChartData = DatasetAndChartData(DatasetData(), '')

    @property
    def name(self) -> str:
        """
        Returns the name of a Dataset.

        :return: A `str` with the name of a Dataset.
        :rtype: str
        """
        return self._name

    @property
    def description(self) -> str:
        """
        Returns the description of a Dataset.

        :return: A `str` with the description of a Dataset.
        :rtype: str
        """
        return self._description

    @property
    def startTime(self) -> datetime.datetime:
        """
        Returns the starting time of a Dataset.

        :return: A `datetime` representing the starting time of a Dataset.
        :rtype: datetime
        """
        return self._startTime

    @property
    def endTime(self) -> datetime.datetime:
        """
        Returns the ending time of a Dataset.

        :return: A `datetime` representing the ending time of a Dataset.
        :rtype: datetime.datetime
        """
        return self._endTime

    @property
    def period(self) -> Union[datetime.timedelta,relativedelta]:
        """
        Returns the period interval of a Dataset.

        :return: A `timedelta` or a `relativedelta` value with the interval of a Dataset.
        :rtype: Union[timedelta | relativedelta]
        """
        return self._period

    @property
    def isTimeInterval(self) -> bool:
        """
        Returns whether the type of a Dataset is a TimeInterval.

        :return: True if the type of a Dataset is a TimeInterval or False otherwise.
        :rtype: bool
        """
        return self._isTimeInterval

    @property
    def datasetPens(self) -> List[DatasetPen]:
      return self._datasetPens

    def setName(self, name:str):
        """
        Sets a name for a Dataset.

        :param name: A new name for a Dataset.
        :type name: str
        :raises Exception: Invalid name length.
        :raises Exception: Invalid character on the name.
        :raises Exception: Name must be a `str`.
        """
        if type(name) is str:
            if len(name) > self.NAME_MAX_SIZE:
                raise Exception("Name cannot exceed " + str(self.NAME_MAX_SIZE) + " characters")
            elif re.search(self.REGEX_PATTERN, name):
                raise Exception("Invalid character on string argument")
            else:
                self._name = name
        else:
            raise Exception("Argument must be a string")

    def setDescription(self, description:str):
        """
        Sets a new description for a Dataset.

        :param description: A new description for a Dataset.
        :type description: str
        :raises Exception: Invalid description length.
        :raises Exception: Description must be a `str`.
        """
        if type(description) is str:
            if len(description) > self.DESCRIPTION_MAX_SIZE:
                raise Exception("Description cannot exceed " + str(self.DESCRIPTION_MAX_SIZE) + " characters")
            else:
                self._description = description
        else:
            raise Exception("Argument must be a string")

    def timeIntervalConfig(self, startTime:datetime.datetime, endTime:datetime.datetime):
        """
        Sets a time interval for a Dataset.

        :param startTime: Starting time interval.
        :type startTime: `datetime`
        :param endTime: Ending time interval.
        :type endTime: `datetime`
        :raises Exception: The `startTime` parameter must be before the `endTime` parameter.
        :raises Exception: Both parameters must have a `datetime` data type.
        """
        if isinstance(startTime, datetime.datetime) and isinstance(endTime, datetime.datetime):
            import pytz
            startTimeUtc = startTime.astimezone(pytz.UTC)
            endTimeUtc = endTime.astimezone(pytz.UTC)
            if startTimeUtc < endTimeUtc:
                self._startTime = startTimeUtc
                self._endTime = endTimeUtc
                self._isTimeInterval = True
            else:
                raise Exception("startTime must be before endTime")
        else:
            raise Exception("Arguments must be of datetime type")

    def recentPeriodConfig(self, count:int, periodUnit:PeriodUnit):
        """
        Sets a recent period interval of a Dataset.

        :param count: Number of Period Units.
        :type count: int
        :param periodUnit: Type of Period Unit. Possible values are **Second**, **Minute**, **Hour**, **Day**, or **Month**.
        :type periodUnit: `epmwebapi.datasetconfig.PeriodUnit`
        :raises Exception: The `count` parameter must be an Integer.
        :raises Exception: The `periodUnit` parameter must have a `PeriodUnit` data type.
        """
        if not isinstance(count, int):
            raise Exception("count argument must be an integer")
        if not isinstance(periodUnit, PeriodUnit):
            raise Exception("periodUnit argument must be of type PeriodUnit")
        self._periodXmlToTimePeriod(count, periodUnit.value)
        self._isTimeInterval = False

    def addPen(self, title:str, dataSourceName:str=None) -> DatasetPen:
        """
        Adds a new Pen to a Dataset.

        :param title: Title of this new Pen.
        :type title: str
        :param dataSourceName: Optional parameter with a data source for this Pen. Default is None.
        :type dataSourceName: str
        :return: A new `epmwebapi.datasetpen.DatasetPen` object.
        :rtype: DatasetPen
        :raises Exception: Pen title already exists.
        """
        for pen in self._datasetPens:
            if pen.title == title:
                raise Exception("Pen title already exists")
        datasetPen = DatasetPen(self, title, dataSourceName)
        self._datasetPens.append(datasetPen)
        return self.getPen(title)

    def getPen(self, title:str) -> DatasetPen:
        """
        Returns a Pen from this Dataset.

        :param title: Title of a Pen.
        :type title: str
        :return: An `epmwebapi.datasetpen.DatasetPen` object.
        :rtype: epmwebapi.datasetpen.DatasetPen
        :raises Exception: Pen not found.
        """
        for pen in self._datasetPens:
            if pen.title == title:
                return pen
        raise Exception("Pen not found")

    def removePen(self, title:str):
        """
        Removes a Pen from this Dataset.

        :param title: Title of a Pen to remove.
        :type title: str
        :raises Exception: Pen not found.
        """
        for pen in self._datasetPens:
            if pen.title == title:
                self._datasetPens.remove(pen)
                return
        raise Exception("Pen not found")

    def execute(self) -> np.ndarray:
        """
        Executes this Dataset.

        :return: The result of the execution of this Dataset as an `np.ndarray` object.
        :rtype: np.ndarray
        """
        results = {}

        if self.isTimeInterval:
            queryPeriod = QueryPeriod(self.startTime, self.endTime)
        else:
            import pytz
            endTime = datetime.datetime.utcnow()
            endTime = pytz.UTC.localize(endTime)
            startTime = endTime - self.period
            queryPeriod = QueryPeriod(startTime, endTime)

        for pen in self.datasetPens:
            pen.setDataSource(pen.dataSource.name)
            if pen.isRaw:
                result = self._connection._historyReadRaw(queryPeriod, pen.dataSource._itemPath)
            else:
                result = self._connection._historyReadAggregate(pen.aggregateType, queryPeriod, pen.dataSource._itemPath)
            results[pen.title] = result

        return results

    def saveToFile(self, path:str, overwrite:bool=False):
        """
        Saves the configuration of this Dataset to a file.

        :param path: Path to a file.
        :type path: str
        :param overwrite: Optional parameter indicating whether the configuration file must be overwritten. Default is False.
        :type overwrite: bool
        """
        if path.endswith('/'):
            filePath = path + self.name + ".epmdataset"
        else:
            filePath = path + '/' + self.name + ".epmdataset"
        epmExtensionXml = self._getEpmExtensionXmlLocal()
        self._connection._saveDatasetFile(epmExtensionXml, filePath, overwrite=overwrite)
        self.__class__ = DatasetConfigLocal
        self._filePath = filePath

    def saveToLocal(self, overwrite:bool=False):
        """
        Saves the configuration of this Dataset to the local user's **Documents** folder.

        :param overwrite: Optional parameter indicating whether the configuration file must be overwritten. Default is False.
        :type overwrite: bool
        """
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        documentsFolder = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, documentsFolder)
        documentsFolder = documentsFolder.value.replace('\\', '/')
        filePath = documentsFolder + '/Elipse Software/EPM Studio/Datasets/' + self.name + ".epmdataset"
        epmExtensionXml = self._getEpmExtensionXmlLocal()
        self._connection._saveDatasetFile(epmExtensionXml, filePath, overwrite=overwrite)
        self.__class__ = DatasetConfigLocal
        self._filePath = filePath

    def saveToServer(self, overwrite:bool=False):
        """
        Saves the configuration of this Dataset to an **EPM Server**.

        :param overwrite: Optional parameter indicating whether the configuration must be overwritten. Default is False.
        :type overwrite: bool
        """
        epmExtensionXml = self._getEpmExtensionXmlServer()
        self._connection._saveDatasetServer(self.name, self.description, epmExtensionXml, overwrite=overwrite)
        self.__class__ = DatasetConfigServer

    def _getEpmExtensionXmlLocal(self):
        import os
        import clr
        clr.AddReference(os.path.dirname(os.path.abspath(__file__)) + '/dll_references/EpmData')
        from Elipse.Epm.Common import TimeInterval, RecentPeriod, DatasetField, RawByPeriod, TrendMode, CalculateMode, \
            EpmExtensionObject, DatasetAndChartData, FileContentData, DatasetData
        from Elipse.Epm.AddressSpaceModel import NodeIdentifier
        from System import DateTime, TimeSpan
        from System.Collections.Generic import List

        if self.isTimeInterval:
            period = TimeInterval()
            period.StartTime = DateTime.Parse(str(self.startTime))
            period.EndTime = DateTime.Parse(str(self.endTime))
        else:
            period = RecentPeriod()
            period.Count = self._count
            period.PeriodType = self._periodUnit

        fields = []
        for datasetPen in self._datasetPens:
            pen = DatasetField()
            pen.Alias = datasetPen.title
            if datasetPen.isRaw:
                pen.Mode = RawByPeriod()
            else:
                sampleInterval = TimeSpan.Parse(str(datasetPen.aggregateType.interval))
                aggregateType = datasetPen._getAggregateId()
                if aggregateType == 1:
                    pen.Mode = TrendMode(sampleInterval)
                else:
                    pen.Mode = CalculateMode(aggregateType, sampleInterval)
            nodeId = datasetPen.dataSource._identity
            identifier = int(nodeId.split(';')[1].split('=')[1])
            namespaceIndex = int(nodeId.split(';')[0].split('=')[1])
            pen.Identity = NodeIdentifier()
            pen.Identity.IdentifierType = 1
            pen.Identity.Numeric32Identifier = identifier
            pen.Identity.NamespaceIndex = namespaceIndex
            fields.append(pen)

        self._datasetAndChartData.Dataset.Period = period
        fieldsList = List[DatasetField]()
        for field in fields:
            fieldsList.Add(field)
        self._datasetAndChartData.Dataset.Fields = fieldsList

        epmExtensionObject = EpmExtensionObject(self._datasetAndChartData.ToXml())
        epmExtensionObject.Tag = DatasetAndChartData.Tag
        epmExtensionXml = epmExtensionObject.ToXml()

        fileContent = FileContentData(self.description, epmExtensionXml)
        fileContentXml = fileContent.ToXml()

        epmExtensionObject = EpmExtensionObject()
        epmExtensionObject.Tag = FileContentData.Tag
        epmExtensionObject.Content = fileContentXml
        epmExtensionXml = epmExtensionObject.ToXml()

        return epmExtensionXml

    def _getEpmExtensionXmlServer(self):
        import os
        import clr
        clr.AddReference(os.path.dirname(os.path.abspath(__file__)) + '/dll_references/EpmData')
        from Elipse.Epm.Common import TimeInterval, RecentPeriod, DatasetField, RawByPeriod, TrendMode, CalculateMode, \
            EpmExtensionObject, DatasetAndChartData, FileContentData, DatasetData, PeriodType
        from Elipse.Epm.AddressSpaceModel import NodeIdentifier, IdentifierType
        from System import DateTime, TimeSpan
        from System.Collections.Generic import List

        if self.isTimeInterval:
            period = TimeInterval()
            period.StartTime = DateTime.Parse(str(self.startTime))
            period.EndTime = DateTime.Parse(str(self.endTime))
        else:
            period = RecentPeriod()
            period.Count = self._count
            period.PeriodType = self._periodUnit if isinstance(self._periodUnit, PeriodType) else PeriodType(self._periodUnit)

        fields = []
        for datasetPen in self._datasetPens:
            pen = DatasetField()
            pen.Alias = datasetPen.title
            if datasetPen.isRaw:
                pen.Mode = RawByPeriod()
            else:
                sampleInterval = TimeSpan.Parse(str(datasetPen.aggregateType.interval))
                aggregateType = datasetPen._getAggregateId()
                if aggregateType == 1:
                    pen.Mode = TrendMode(sampleInterval)
                else:
                    pen.Mode = CalculateMode(aggregateType, sampleInterval)
            nodeId = datasetPen.dataSource._itemPath._relativePath
            identifier = int(nodeId.split(';')[1].split('=')[1])
            namespaceIndex = int(nodeId.split(';')[0].split('=')[1])
            pen.Identity = NodeIdentifier()
            pen.Identity.IdentifierType = IdentifierType(1)
            pen.Identity.Numeric32Identifier = identifier
            pen.Identity.NamespaceIndex = namespaceIndex
            fields.append(pen)

        self._datasetAndChartData.Dataset.Period = period
        fieldsList = List[DatasetField]()
        for field in fields:
            fieldsList.Add(field)
        self._datasetAndChartData.Dataset.Fields = fieldsList

        epmExtensionObject = EpmExtensionObject(self._datasetAndChartData.ToXml())
        epmExtensionObject.Tag = DatasetAndChartData.Tag
        epmExtensionXml = epmExtensionObject.ToXml()

        return epmExtensionXml

    def _periodXmlToTimePeriod(self, count, period):
        from Elipse.Epm.Common import PeriodType
        if isinstance(period, int):
            period = PeriodType(period)
        if period == PeriodType.Second:
            self._period = datetime.timedelta(seconds=count)
        elif period == PeriodType.Minute:
            self._period = datetime.timedelta(minutes=count)
        elif period == PeriodType.Hour:
            self._period = datetime.timedelta(hours=count)
        elif period == PeriodType.Day:
            self._period = datetime.timedelta(days=count)
        elif period == PeriodType.Month:
            self._period = relativedelta(months=count)
        else:
            raise Exception("Error with the period time unit")
        self._count = count
        self._periodUnit = period

    def _convertToPyDateTime(self, dateTime):
        import dateutil.parser
        import pytz
        strDateTime = dateTime.ToString()
        try:
            pyDateTime = datetime.datetime.strptime(strDateTime, '%m/%d/%Y %H:%M:%S %p')
        except:
            try:
                pyDateTime = datetime.datetime.strptime(strDateTime, '%d/%m/%Y %H:%M:%S')
            except:
                pyDateTime = dateutil.parser.parse(strDateTime)
        finally:
            pyDateTime = pytz.UTC.localize(pyDateTime)
            return pyDateTime

class DatasetConfigLocal(DatasetConfig):
    """
    Class representing a local Dataset.
    """
    def __init__(self, connection, name, content = None, description = None, filePath = None):
        import os
        import clr
        clr.AddReference(os.path.dirname(os.path.abspath(__file__)) + '/dll_references/EpmData')
        from Elipse.Epm.Common import EpmExtensionObject, SerializationExtensions, TimeInterval, DatasetAndChartData, \
                                      DatasetData
        self._connection = connection
        self._name = None
        self._count = None
        self._periodUnit = None
        self._startTime = None
        self._endTime = None
        self._period = None
        self._datasetPens = []
        self._filePath = filePath
        self._nameChanged = False
        if content is None:
            self.setName(name)
            self.recentPeriodConfig(1, PeriodUnit.Hour)
            self._description = description
            self._datasetAndChartData = DatasetAndChartData(DatasetData(), '')
        else:
            self._name = name
            contentObject = EpmExtensionObject.FromXml(content)
            resource = SerializationExtensions.ReadFileResourceContent(contentObject)
            self._description = resource.Description
            resourceObject = EpmExtensionObject.FromXml(resource.Content)
            dataset = SerializationExtensions.ReadDatasetAndChartData(resourceObject)
            self._datasetAndChartData = dataset

            periodType = dataset.Dataset.Period
            if isinstance(periodType, TimeInterval):
                self._isTimeInterval = True
                start = dataset.Dataset.Period.StartTime
                startUtc = start.ToUniversalTime()
                startTime = self._convertToPyDateTime(startUtc)
                self._startTime = startTime
                end = dataset.Dataset.Period.EndTime
                endUtc = end.ToUniversalTime()
                endTime = self._convertToPyDateTime(endUtc)
                self._endTime = endTime
            else:
                self._isTimeInterval = False
                count = dataset.Dataset.Period.Count
                period = dataset.Dataset.Period.PeriodType
                self._periodXmlToTimePeriod(count, period)


            for penConfig in dataset.Dataset.Fields:
                title = penConfig.Alias
                self._datasetPens.append(DatasetPen(self, title, penConfig=penConfig))

    @property
    def filePath(self) -> str:
        """
        File path of a local Dataset.

        :return: A `str` representing the path of a local Dataset.
        :rtype: str
        """
        return self._filePath

    def setName(self, name:str):
        """
        Sets a name for a local Dataset.

        :param name: Name for a local Dataset.
        :type name: str
        :raises Exception: Invalid name length.
        :raises Exception: Invalid character on name.
        :raises Exception: The `name` parameter must be a `str`.
        """
        if type(name) is str:
            if len(name) > self.NAME_MAX_SIZE:
                raise Exception("Name cannot exceed " + str(self.NAME_MAX_SIZE) + " characters")
            elif re.search(self.REGEX_PATTERN, name):
                raise Exception("Invalid character on string argument")
            else:
                if name != self.name:
                    self._name = name
                    self._nameChanged = True
        else:
            raise Exception("Argument must be a string")

    def save(self):
        """
        Saves a local Dataset to a file.

        :raises Exception: Local Dataset changed but there is another Dataset with this name on the same folder.
        :raises Exception: There is no Dataset file to save. Please use the `saveToFile` or `saveToLocal` methods.
        """
        epmExtensionXml = self._getEpmExtensionXmlLocal()
        if self._filePath is not None:
            if self._nameChanged:
                pathSplit = self._filePath.split("/")
                pathSplit.pop(-1)
                path = '/'.join(pathSplit)
                newFilePath = path + '/' + self.name + ".epmdataset"
                if os.path.exists(newFilePath):
                    raise Exception("Dataset name changed but there is another dataset with this name on the same folder")
                self._connection._saveDatasetFile(epmExtensionXml, self._filePath, overwrite=True)
                os.rename(self._filePath, newFilePath)
                self._filePath = newFilePath
                self._nameChanged = False
            else:
                self._connection._saveDatasetFile(epmExtensionXml, self._filePath, overwrite=True)
        else:
            raise Exception("There is no dataset file to save, use the method saveToFile() or saveToLocal() instead")

    def delete(self):
        """
        Deletes a local Dataset.
        """
        self._connection._deleteDatasetFile(self._filePath)
        self.__class__ = DatasetConfig

    def duplicate(self, newName:str, samePath:bool=True) -> DatasetConfig:
        """
        Creates a copy of a local Dataset.

        :param newName: A name for the copy of this local Dataset.
        :type newName: str
        :param samePath: An optional parameter indicating whether the new local Dataset has the same path of this local Dataset. Default is True.
        :type samePath: bool
        :return: A `DatasetConfigLocal` object as a copy of this local Dataset.
        :rtype: DatasetConfigLocal
        :raises Exception: Dataset has no file on folder.
        :raises Exception: Dataset already exists.
        """
        duplicate = DatasetConfigLocal(self._connection, self.name, self._getEpmExtensionXmlLocal())
        duplicate.setName(newName)
        if samePath:
            if self._filePath is None:
                raise Exception("Dataset has no file on folder")
            pathSplit = self._filePath.split("/")
            pathSplit.pop(-1)
            path = '/'.join(pathSplit)
            newFilePath = path + '/' + newName + ".epmdataset"
            if os.path.exists(newFilePath):
                raise Exception("Dataset name already exists on that folder")
            duplicate._filePath = newFilePath
        else:
            duplicate._filePath = None

        return duplicate


class DatasetConfigServer(DatasetConfig):
    """
    Class representing a Dataset from an **EPM Server**.
    """
    
    def __init__(self, connection, name, description, content = None):
        import os
        import clr
        clr.AddReference(os.path.dirname(os.path.abspath(__file__)) + '/dll_references/EpmData')
        from Elipse.Epm.Common import EpmExtensionObject, SerializationExtensions, TimeInterval, DatasetAndChartData, \
                                      DatasetData
        self._connection = connection
        self._name = None
        self._description = description
        self._count = None
        self._periodUnit = None
        self._startTime = None
        self._endTime = None
        self._period = None
        self._datasetPens = []
        self._nameChanged = False
        self._oldName = None
        if content is None:
            self.setName(name)
            self.recentPeriodConfig(1, PeriodUnit.Hour)
            self._datasetAndChartData = DatasetAndChartData(DatasetData(), '')
        else:
            self._name = name
            resourceObject = EpmExtensionObject.FromXml(content)
            dataset = SerializationExtensions.ReadDatasetAndChartData(resourceObject)
            self._datasetAndChartData = dataset

            periodType = dataset.Dataset.Period
            if isinstance(periodType, TimeInterval):
                self._isTimeInterval = True
                start = dataset.Dataset.Period.StartTime
                startUtc = start.ToUniversalTime()
                startTime = self._convertToPyDateTime(startUtc)
                self._startTime = startTime
                end = dataset.Dataset.Period.EndTime
                endUtc = end.ToUniversalTime()
                endTime = self._convertToPyDateTime(endUtc)
                self._endTime = endTime
            else:
                self._isTimeInterval = False
                count = dataset.Dataset.Period.Count
                period = dataset.Dataset.Period.PeriodType
                self._periodXmlToTimePeriod(count, period)


            for penConfig in dataset.Dataset.Fields:
                title = penConfig.Alias
                self._datasetPens.append(DatasetPen(self, title, penConfig=penConfig))

    def setName(self, name:str):
        """
        Sets the name of this Dataset.

        :param name: Name of this **EPM Server** Dataset.
        :type name: str
        :raises Exception: Invalid name length.
        :raises Exception: Invalid character on `name` parameter.
        :raises Exception: The `name` argument must be a `str`.
        """
        if type(name) is str:
            if len(name) > self.NAME_MAX_SIZE:
                raise Exception("Name cannot exceed " + str(self.NAME_MAX_SIZE) + " characters")
            if re.search(self.REGEX_PATTERN, name):
                raise Exception("Invalid character on string argument")
            else:
                if name != self.name:
                    self._oldName = self._name
                    self._name = name
                    self._nameChanged = True
        else:
            raise Exception("Argument must be a string")

    def save(self):
        """
        Saves this Dataset to an **EPM Server**.

        :raises Exception: Dataset name changed but there is another Dataset with the same name on the **EPM Server**.
        """
        epmExtensionXml = self._getEpmExtensionXmlServer()
        if self._nameChanged:
            for datasetName in self._connection.listDatasetServer():
                if str.lower(self.name) == str.lower(datasetName):
                    raise Exception("Dataset name changed but there is another dataset with this name on server")
            if self._oldName is None:
                self._connection._saveDatasetServer(self.name, self.description, epmExtensionXml)
            else:
                self._connection._saveDatasetServer(self.name, self.description, epmExtensionXml, oldName=self._oldName)
            self._nameChanged = False
        else:
            self._connection._saveDatasetServer(self.name, self.description, epmExtensionXml, overwrite=True)

    def delete(self):
        """
        Deletes this Dataset from the **EPM Server**.
        """
        self._connection._deleteDatasetServer(self.name)
        self.__class__ = DatasetConfig

    def duplicate(self, newName:str) -> DatasetConfig:
        """
        Creates a copy of this Dataset from the current **EPM Server**.

        :param newName: A name for the copy of this Dataset.
        :type newName: str
        :return: A copy of this Dataset.
        :rtype: DatasetConfig
        :raises Exception: A duplicated Dataset must have a different name.
        :raises Exception: There is another Dataset with the same name on the **EPM Server**.
        """
        duplicate = DatasetConfigServer(self._connection, self.name, self.description, content=self._getEpmExtensionXmlServer())
        if newName == self.name:
            raise Exception("Duplicated dataset must have a different name")
        for datasetName in self._connection.listDatasetServer():
            if str.lower(newName) == str.lower(datasetName):
                raise Exception("There is another dataset with this name on server")
        duplicate.setName(newName)
        duplicate._oldName = None

        return duplicate

