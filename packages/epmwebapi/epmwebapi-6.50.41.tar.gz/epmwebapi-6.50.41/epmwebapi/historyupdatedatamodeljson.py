class HistoryUpdateDataModelJSON(object):
    """description of class"""
    def __init__(self, items):
        self._items = items

    def toDict(self):
        jsonItems = []

        for item in self._items:
            jsonItems.append(item.toDict());

        return {'items': jsonItems }


