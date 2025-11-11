import numpy as np
from .itempathjson import ItemPathJSON
import datetime as dt
from .datavaluejson import DataValueJSON
from .historyupdatetype import HistoryUpdateType
from .queryperiod import QueryPeriod
from .aggregatedetails import AggregateDetails

from enum import Enum

import pytz

InfinityName = 'Infinity'
MinusInfinityName = '-Infinity'
NanName = 'NaN'

class RetrievalMode(Enum):
    """
    Enumeration with all types of retrieval modes.
    """
    Previous = "Previous"

    Exact = "Exact"

    Next = "Next"


class EpmVariable(object):
    """
    Class representing a Variable.
    """

    def __init__(self, epmConnection, name, path, itemPath):
      self._epmConnection = epmConnection
      self._name = name
      self._path = path
      self._itemPath = itemPath

    ### Properties
    @property
    def name(self) -> str:
        """
        :return: The name of this Variable.
        :rtype: str
        """
        return self._name

    @property
    def path(self) -> str:
        """
        :return: The path of this Variable.
        :rtype: str
        """
        return self._path

    ### Methods

        ## Public Methods
    def recordedValue(self, timestamp:dt.datetime, retrieval:RetrievalMode=RetrievalMode.Previous):
      """
      Returns data effectively recorded as informed in the `retrieval` parameter.

      :param timestamp: Timestamp considered for data searching.
      :type timestamp: dt.datetime
      :param retrieval: Mode for data searching. Default is `RetrievalMode.Previous`.
      :type retrieval: RetrievalMode
      :return: A `numpy` array element with Value, Timestamp, and Quality.
      """
      timestamp = timestamp.astimezone(pytz.UTC)
      start = timestamp - dt.timedelta(milliseconds=1)
      end = timestamp + dt.timedelta(milliseconds=1)
      queryPeriod = QueryPeriod(start, end)
      result = self.historyReadRaw(queryPeriod, True)

      previousVal = None
      exactVal = None
      nextVal = None

      if result.size == 1:
          if result[0][1] > timestamp:
              nextVal = result[0]
          elif result[0][1] == timestamp:
              exactVal = result[0]
          else:
              previousVal = result[0]
      elif result.size == 2:
          if result[1][1] > timestamp:
              nextVal = result[1]
          elif result[1][1] == timestamp:
              exactVal = result[1]
          if result[0][1] < timestamp:
              previousVal = result[0]
          elif result[0][1] == timestamp:
              exactVal = result[0]
      elif result.size == 3:
          previousVal = result[0]
          exactVal = result[1]
          nextVal = result[2]
      elif result.size == 4:
          previousVal = result[1]
          exactVal = result[2]
          nextVal = result[3]
      else:
          return None

      if retrieval == RetrievalMode.Previous:
          if previousVal and previousVal[2] == 2156527616:
              return self.recordedValue(previousVal[1], retrieval)
          else:
              return previousVal
      elif retrieval == RetrievalMode.Exact:
          if exactVal and exactVal[2] == 2156527616:
              return None
          else:
              return exactVal
      elif retrieval == RetrievalMode.Next:
          if nextVal and nextVal[2] == 2156527616:
              return self.recordedValue(nextVal[1], retrieval)
          else:
              return nextVal


    def historyReadRaw(self, queryPeriod:QueryPeriod, bounds:bool=False) -> np.ndarray:
      """
      Returns raw values from this Variable within the configured period.

      :param queryPeriod: An `epmwebapi.queryperiod.QueryPeriod` object with the period of time to query.
      :type queryPeriod: epmwebapi.queryperiod.QueryPeriod
      :param bounds: An optional parameter indicating whether the bound value must be returned or not. Default is False.
      :type bounds: bool
      :return: A numpy NDArray with Value, Timestamp, and Quality.
      :rtype: np.NDArray
      """
      return self._epmConnection._historyReadRaw(queryPeriod, self._itemPath, bounds = bounds)

    def read(self) -> DataValueJSON:
        """
        :return: The current value of this Variable.
        :rtype: DataValueJSON
        :raises Exception: Reading error.
        """
        readResult = self._epmConnection._read([self._itemPath], [13]).items()[0]
        if readResult[1].code != 0:
          raise Exception("Read from '" + self._path + "' failed with error: " + str(readResult[1].code))
        from .basicvariable import DataTypeId
        # Verifica Inf, -Inf, Nan
        if (type(readResult[0].value._value) == str):
            if ((readResult[0].value._dataTypeId == 'i=' + str(DataTypeId.Float.value) or 
                readResult[0].value._dataTypeId == 'i=' + str(DataTypeId.Double.value))):
                import numpy as np
                if readResult[0].value._value == InfinityName:
                    readResult[0].value._value = np.inf
                elif readResult[0].value._value == MinusInfinityName:
                    readResult[0].value._value = -np.inf
                elif readResult[0].value._value == NanName:
                    readResult[0].value._value = np.nan
            elif (readResult[0].value._dataTypeId == 'i=' + str(DataTypeId.Int.value) or 
                  readResult[0].value._dataTypeId == 'i=' + str(DataTypeId.UInt.value)):
                readResult[0].value._value = int(readResult[0].value._value) 
            elif (readResult[0].value._dataTypeId == 'i=' + str(DataTypeId.DateTime.value)):
                import dateutil
                from datetime import timezone
                try:
                    readResult[0].value._value = dateutil.parser.parse(readResult[0].value._value).replace(tzinfo=timezone.utc)
                except:
                    pass
        return readResult[0].value

    def write(self, value:any, timestamp:dt.datetime=dt.datetime.now(dt.timezone.utc), quality:int=0):
        """
        Writes a value to this Variable.

        :param value: Value to write.
        :type value: any
        :param timestamp: Optional parameter indicating the value's date and time. Default is `dt.datetime.now(dt.timezone.utc)`.
        :type timestamp: dt.datetime
        :param quality: OPC UA quality of the value. Default is 0 (zero, Good).
        :type quality: int

        """
        return self._epmConnection._write([self._itemPath], [13], [DataValueJSON(value, quality, timestamp)])

    def historyReadAggregate(self, aggregateDetails:AggregateDetails, queryPeriod:QueryPeriod) -> np.ndarray:
        """
        Returns the aggregated values of this Variable within the configured period.

        :param aggregateDetails: An `epmwebapi.aggregatedetails.AggregateDetails` object with the aggregate function.
        :type aggregateDetails: epmwebapi.aggregatedetails.AggregateDetails
        :param queryPeriod: An `epmwebapi.queryperiod.QueryPeriod` object with the period to search.
        :type queryPeriod: epmwebapi.queryperiod.QueryPeriod
        :return: A numpy NDArray with Value, Timestamp, and Quality.
        """
        return self._epmConnection._historyReadAggregate(aggregateDetails, queryPeriod, self._itemPath)

    def historyUpdate(self, values:np.ndarray):
      """
      Writes an array of values, with Value, Timestamp, and Quality, to this Variable.

      #### Example
      `array = np.empty([valuesCount], dtype=np.dtype([('Value', '>f4'), ('Timestamp', 'object'), ('Quality', 'object')]))`

      :param value: A numpy NDArray with values to write.
      :type value: np.ndarray
      """
      return self._epmConnection._historyUpdate(HistoryUpdateType.Update.value, [ self._itemPath ], [ values ])

    def historyDelete(self, queryPeriod:QueryPeriod):
        """
        Removes data from a specified period of time.

        :param queryPeriod: An `epmwebapi.queryperiod.QueryPeriod` object with the period to remove data.
        :type queryPeriod: epmwebapi.queryperiod.QueryPeriod
        """
        values = self._epmConnection._historyReadRaw(queryPeriod, self._itemPath, False)
        return self._epmConnection._historyUpdate(HistoryUpdateType.Remove.value, [ self._itemPath ], [ values ])


