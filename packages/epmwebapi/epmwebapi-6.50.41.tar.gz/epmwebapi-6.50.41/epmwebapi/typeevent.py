from __future__ import annotations
from typing import Any, List
from numpy.typing import NDArray

from .elementoperand import ElementOperand
from .queryperiod import QueryPeriod
from .itempathjson import ItemPathJSON


class TypeEvent(object):
    """
    Class representing an **EPM** Event TypeEvents.
    """
    
    def __init__(self, connection:EpmConnection, eventName:str):
        self._connection = connection
        self._eventPath = ItemPathJSON('OPCUA.BrowsePath', '', '1:Events/1:TypeEvents/1:' + eventName)


    def historyRead(self, queryPeriod:QueryPeriod, where:ElementOperand=None, select:List[str]=['Time', 'Severity', 'EventId', 'SourceInstanceId','SourceInstance', 'SourceNode', 'PayloadVariables', 'PayloadValues']) -> NDArray[Any]:
      """
      Returns raw values from this Event within the configured period.

      :param queryPeriod: An `epmwebapi.queryperiod.QueryPeriod` object with the period of time to query.
      :type queryPeriod: epmwebapi.queryperiod.QueryPeriod
      :param where: An optional parameter indicating the where condition to be applied. Default is None.
      :type where: epmwebapi.elementoperand.ElementOperand
      :param select: An optional parameter indicating the selected fields to be returned. Default is ['Time', 'Severity', 'EventId', 'SourceInstanceId','SourceInstance', 'SourceNode', 'PayloadVariables', 'PayloadValues'].
      :type select: List[str]
      :return: A numpy NDArray.
      :rtype: np.NDArray

      Examples
      --------
        The following examples show how to use historyRead function.

        Retrives all events from a period of time:

        .. code-block:: python

            ini_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
            end_date = dt.datetime.now(dt.timezone.utc)
            queryPeriod = epm.QueryPeriod(ini_date, end_date)
            typeEvent = connection.getTypeEvent('EventName')
            result = typeEvent.historyRead(queryPeriod)

        Retrieves all events from Pump14 in the last hour:

        .. code-block:: python

            ini_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
            end_date = dt.datetime.now(dt.timezone.utc)
            queryPeriod = epm.QueryPeriod(ini_date, end_date)
            typeEvent = connection.getTypeEvent('PumpEventName')
            where = ElementOperand(Operator.Like, [SimpleAttributeOperand('SourceInstance'), LiteralOperand('Pump14')])
            result = typeEvent.historyRead(queryPeriod, where)

        Retrieves all Pumps where the Temperature is greater thar 30 degres (Temperature Pump property must be inserted on Payload):

        .. code-block:: python

            ini_date = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)
            end_date = dt.datetime.now(dt.timezone.utc)
            queryPeriod = epm.QueryPeriod(ini_date, end_date)
            typeEvent = connection.getTypeEvent('PumpEventName')
            where = ElementOperand(Operator.Greater, [SimpleAttributeOperand('Temperature'), LiteralOperand(30)])
            result = typeEvent.historyRead(queryPeriod, where, ['SourceInstance'])
      """
      return self._connection._historyReadEvent(queryPeriod, self._eventPath, select, where)