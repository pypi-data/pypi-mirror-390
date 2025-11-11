import json
class HistoryProcessedModelJSON(object):
    """description of class"""
    def __init__(self, aggregateType, processingInterval, startTime, endTime, paths):
        self._aggregateType = aggregateType
        self._processingInterval = processingInterval
        self._startTime = startTime
        self._endTime = endTime
        self._paths = paths

    def toDict(self):
        jsonPaths = []

        childMap = []
        for item in self._paths:
            childMap.append(item.toDict());

        return {'aggregateType': self._aggregateType.toDict(), 'processingInterval': self._processingInterval, 
               'startTime' : self._startTime.isoformat(), 'endTime' : self._endTime.isoformat(), 
               'paths' : childMap}

