from typing import List

from .elementoperand import ElementOperand
from .simpleattributeoperand import SimpleAttributeOperand


class FilterModel(object):
    """
    FilterModel class
    """
    def __init__(self, select:List[SimpleAttributeOperand], where:ElementOperand):
        """
        Creates a new instance of an AnnotationValueJSON object.

        :param message: A string with a message for this Annotation.
        :param userName: A string with the name of a user.
        :param annotationTime: A date and time for this Annotation.
        """
        self._select = select
        self._where = where
