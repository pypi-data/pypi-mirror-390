import json

def fromDict(itemPathDict):
    return ItemPathJSON(itemPathDict['language'], itemPathDict['context'], itemPathDict['path'])

class ItemPathJSON(object):
    """description of class"""
    def __init__(self, language, context, path):
        self._language = language
        self._context = context
        self._relativePath = path

    @property
    def relativePath(self):
      return self._relativePath;

    def toDict(self):
        return {'language' : self._language, 'context' : self._context, 'path' : self._relativePath}

    def toJSON(self):
        return json.dumps({'language' : self._language, 'context' : self._context, 'path' : self._relativePath})

