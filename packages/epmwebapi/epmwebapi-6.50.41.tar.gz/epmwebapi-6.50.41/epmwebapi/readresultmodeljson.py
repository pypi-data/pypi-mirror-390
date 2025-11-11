class ReadResultModelJSON(object):
  
  def __init__(self, items, diagnostics):
    self._items = items
    self._diagnostics = diagnostics

  def items(self):
    return list(zip(self._items, self._diagnostics))

  def values(self):
    return self._items

  def diagnostics(self):
    return self._diagnostics

