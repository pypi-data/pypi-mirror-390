class BrowseModelJSON(object):

  def __init__(self, items, continuationPoint):
    self._items = items
    self._continuationPoint = continuationPoint

  def toDict(self):
    jsonPaths = []

    childMap = []
    for item in self._items:
        childMap.append(item.toDict());

    return {'items': childMap, 'continuationPoint': self._continuationPoint }
