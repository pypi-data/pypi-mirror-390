from .itempathjson import ItemPathJSON


class SimpleAttributeOperand(object):
    """
    SimpleAttributeOperand class
    """
    def __init__(self, propertyName:str):
        """Creates a new instance of an SimpleAttributeOperand object.

       :param propertyName: The property name used by this operand filter.
       :type propertyName: str.
        """
        self._propertyName = propertyName

    def toDict(self):
        return {'type':'simple', 'typePath': None, 'browsePath': self._propertyName, 'attributeId': 13} 