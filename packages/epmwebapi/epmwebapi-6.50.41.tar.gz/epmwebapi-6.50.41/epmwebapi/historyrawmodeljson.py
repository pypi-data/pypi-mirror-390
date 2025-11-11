import json
class HistoryRawModelJSON(object):
    """description of class"""
    def __init__(self, startTime, endTime, bounds, paths):
        self._startTime = startTime
        self._endTime = endTime
        self._bounds = bounds
        self._paths = paths

    def toDict(self):
        jsonPaths = []

        childMap = []
        for item in self._paths:
            childMap.append(item.toDict());

        map = {'startTime' : self._startTime.isoformat(), 'endTime' : self._endTime.isoformat(), 
                                'bounds' : self._bounds, 'paths' : childMap}

        return map

