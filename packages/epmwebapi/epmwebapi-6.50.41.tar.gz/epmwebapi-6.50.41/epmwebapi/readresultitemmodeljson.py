class ReadResultItemModelJSON(object):

  def __init__(self, identity, value):
    self._identity = identity
    self._value = value

  @property
  def identity(self):
      return self._identity

  @property
  def value(self):
      return self._value

