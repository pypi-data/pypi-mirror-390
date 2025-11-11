from threading import Timer, Thread, Event

class AutoStartTimer(object):
  def __init__(self, spam, callback):
    self._spam = spam
    self._callback = callback
    self._stopEvent = Event()
    self._thread = Thread(target=self._periodicalExecution)
    self._thread.daemon = True
    self._thread.start()

  def _periodicalExecution(self):
    while not self._stopEvent.is_set():
      if not self._stopEvent.wait(self._spam):
          self._callback()
      

  def start(self):
    self.cancel()
    self._thread = Thread(target=self._periodicalExecution)
    self._thread.daemon = True
    self._thread.start()

  def cancel(self):
    self._stopEvent.set()
    self._thread.join()
