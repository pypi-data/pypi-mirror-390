class WriteModelJSON(object):

  def __init__(self, items):
    self._items = items

  def toDict(self):

    childMap = []
    for item in self._items:
        childMap.append(item.toDict())

    return {'items': childMap }
