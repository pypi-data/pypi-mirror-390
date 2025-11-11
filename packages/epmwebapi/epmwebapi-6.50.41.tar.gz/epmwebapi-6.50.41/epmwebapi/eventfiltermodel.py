from typing import List
from .elementoperand import ElementOperand
from .simpleattributeoperand import SimpleAttributeOperand


class EventFilterModel(object):
    def __init__(self, select:List[SimpleAttributeOperand], where:ElementOperand) -> None:
        self._select = select
        self._where = where

    def toDict(self):

        select = []
        for item in self._select:
            select.append(item.toDict())

        where = None
        if self._where is not None:
            where = self._where.toDict()

        map = {'select' : select, 'where' : where}

        return map
        