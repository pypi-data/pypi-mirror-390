class WriteItemModelJSON(object):
  
  def __init__(self, path, attributeId, value):
    self._path = path
    self._attributeId = attributeId
    self._value = value

  def toDict(self):

    return { 'path': self._path.toDict(), 
             'attributeId': self._attributeId,
             'value': self._value.toDict() }

