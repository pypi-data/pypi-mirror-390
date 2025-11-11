from .epmvariable import EpmVariable
from .filteroperand import FilterOperand

class AttributeOperand(FilterOperand):
    """
    AttributeOperand class
    """
    def __init__(self, variable:EpmVariable): 
        """
        Creates a new instance of an AttributeOperand object.

        :param variable: The variable used by this operand filter.
        :type variable: :class:`EpmVariable`.
        """
        self._variable = variable

    def toDict(self):
        return {'type':'attribute', 'path':self._variable._itemPath.toDict(), 'alias': None, 'browsePath': None, 'attributeId': 13}
