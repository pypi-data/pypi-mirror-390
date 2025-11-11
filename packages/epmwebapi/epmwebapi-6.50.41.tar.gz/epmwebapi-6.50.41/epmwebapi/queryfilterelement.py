from __future__ import annotations

from typing import List, Union

from .attributeoperand import AttributeOperand
from .elementoperand import ElementOperand
from .literaloperand import LiteralOperand
from .simpleattributeoperand import SimpleAttributeOperand


class QueryFilterElement(object):
    def __init__(self, operator:str, operands:List[Union[AttributeOperand,ElementOperand,LiteralOperand,SimpleAttributeOperand,QueryFilterElement]]) -> None:
        self._operator = operator
        self._operands = operands    

    def toDict(self):
        return {'operator': self._operator, 'operands': [item.toDict() for item in self._operands]}