class AnnotationValueJSON(object):
    """
    AnnotatioValueJSON class
    """
    def __init__(self, message, userName, annotationTime):
        """
        Creates a new instance of an AnnotationValueJSON object.

        :param message: A string with a message for this Annotation.
        :param userName: A string with the name of a user.
        :param annotationTime: A date and time for this Annotation.
        """
        self._message = message
        self._userName = userName
        self._annotationTime = annotationTime

    @property
    def message(self):
        """
        Property defining a message for this Annotation.
        :return: A string with this Annotation's message.
        :rtype: str
        """
        return self._message

    @property
    def userName(self):
        """
        Property defining the user that created this Annotation.
        :return: A string with the name of the user that created this Annotation.
        :rtype: str
        """
        return self._userName

    @property
    def annotationTime(self):
        """
        Property defining the creation date and time of this Annotation.
        :return: A date and time for this Annotation.
        :rtype: datetime
        """
        return self._annotationTime

    def toDict(self):
        """
        Returns this Annotation as a `dict` object.
        :return: A Dictionary with data from this Annotation.
        :rtype: dict
        """
        from .epmnodeids import EpmNodeIds
        return {'value': { 
                            'annotationTime' : self._annotationTime.isoformat(), 
                            'message' : self._message,
                            'userName' : self._userName 
                         }, 
                'quality': 0, 
                'timestamp' : self._annotationTime.isoformat(),
                'dataTypeId': EpmNodeIds.AnnotationType.value }
