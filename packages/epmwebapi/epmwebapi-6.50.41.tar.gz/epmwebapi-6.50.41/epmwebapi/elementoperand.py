from __future__ import annotations

from typing import List, Union

from .literaloperand import LiteralOperand
from .simpleattributeoperand import SimpleAttributeOperand
from .attributeoperand import AttributeOperand

from enum import Enum

class Operator(Enum):
    """
    Enumeration with all types of operators
    """
    Equals = "Equals"
    IsNull = "IsNull"
    GreaterThan = "GreaterThan"
    LessThan = "LessThan"
    GreaterThanOrEqual = "GreaterThanOrEqual"
    LessThanOrEqual = "LessThanOrEqual"
    Like = "Like"
    Not = "Not"
    Between = "Between"
    InList = "InList"
    And = "And"
    Or = "Or"
    Cast = "Cast"
    InView = "InView"
    OfType = "OfType"
    RelatedTo = "RelatedTo"
    BitwiseAnd = "BitwiseAnd"
    BitwiseOr = "BitwiseOr"


class ElementOperand(object):
    """
    ElementOperand class
    """
    def __init__(self, operator:Operator, operands:List[Union[SimpleAttributeOperand,AttributeOperand,LiteralOperand,ElementOperand]]):
        """
        Creates a new instance of an ElementOperand object.

        :param operator: The selected Operator enum.
        :type operator: :class:`Operator`
        :param operands: A list of filter operands that must be:
             -  :class:`SimpleAttributeOperand`: Operando for simple attributes.
             -  :class:`AttributeOperand`: Operand for generic attributes.
             -  :class:`LiteralOperand`: Operand for literal values.
             -  :class:`ElementOperand`: Operand to reference other filter elements.
        :type operands: :class:`typing.List`
        """
        self._operator = operator
        self._operands = operands

    def toDict(self):
        return {'type':'element', 'operator': self._operator.value, 'operands': [item.toDict() for item in self._operands]}
