class ReadItemModelJSON(object):
  
  def __init__(self, path, attributeId):
    self._path = path
    self._attributeId = attributeId

  def toDict(self):

    return { 'path': self._path.toDict(), 
             'attributeId': self._attributeId }

