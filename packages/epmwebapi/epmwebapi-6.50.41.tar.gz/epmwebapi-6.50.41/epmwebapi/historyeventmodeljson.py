from datetime import datetime
from typing import List

from .itempathandcontinuationpointjson import ItemPathAndContinuationPointJSON
from .eventfiltermodel import EventFilterModel

class HistoryEventModelJSON(object):
    """description of class"""
    def __init__(self, startTime:datetime, endTime:datetime, filter:EventFilterModel, paths:List[ItemPathAndContinuationPointJSON]):
        self._startTime = startTime
        self._endTime = endTime
        self._filter = filter
        self._paths = paths

    def toDict(self):

        childMap = []
        for item in self._paths:
            childMap.append(item.toDict());

        map = {'startTime' : self._startTime.isoformat(), 'endTime' : self._endTime.isoformat(), 
               'filter' : self._filter.toDict(), 'paths' : childMap}

        return map