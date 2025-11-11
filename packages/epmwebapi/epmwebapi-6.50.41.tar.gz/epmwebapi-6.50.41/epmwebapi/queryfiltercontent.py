from typing import List

from .queryfilterelement import QueryFilterElement


class QueryFilterContent(object):
    def __init__(self, elements:List[QueryFilterElement]) -> None:
        if not isinstance(elements, list):
            raise TypeError("Parameter elements must be a list")
        if not all(isinstance(item, QueryFilterElement) for item in elements):
            raise TypeError("Todos os elementos da lista devem ser inteiros")
        self._elements = elements 

    def toDict(self):
        return {'elements': [item.toDict() for item in self._elements]}