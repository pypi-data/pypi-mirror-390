import json
from typing import List

from .itempathjson import ItemPathJSON
from .queryfiltercontent import QueryFilterContent

class QueryModelFilterJSON(object):
    """description of class"""
    def __init__(self, continuationPoint, release, resultMask, startNodeIds:List[ItemPathJSON], browseNameFilter:str, 
                 typeFilter:ItemPathJSON, filter:QueryFilterContent):
      self._continuationPoint = continuationPoint
      self._release = release
      self._resultMask = resultMask
      self._startNodeIds = startNodeIds
      self._browseNameFilter = browseNameFilter
      self._typeFilter = typeFilter
      self._filter = filter

    def toDict(self):
        startNodeIds = [item.toDict() for item in self._startNodeIds]
        filter = None
        if self._filter != None:
           filter = self._filter.toDict()
        return {'continuationPoint': self._continuationPoint, 'release': self._release, 
               'resultMask' : self._resultMask, 'startNodeIds' : startNodeIds,'browseNameFilter' : self._browseNameFilter, 
               'typeFilter' : self._typeFilter.toDict() if self._typeFilter is not None else None,
               'filter': filter}