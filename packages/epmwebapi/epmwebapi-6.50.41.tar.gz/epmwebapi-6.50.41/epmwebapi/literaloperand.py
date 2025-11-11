from .datavaluejson import DataValueJSON
import datetime as dt

class LiteralOperand(object):
    """
    LiteralOperand class
    """
    def __init__(self, value:object):
        """
        Creates a new instance of an LiteralOperand object.

        :param value: The value of the literal operand filter.
        :type value: object.
        """
        self._value = DataValueJSON(value, 0, dt.datetime.now(dt.timezone.utc))

    def toDict(self):
        return {'type':'literal', 'value': self._value.toDict()}