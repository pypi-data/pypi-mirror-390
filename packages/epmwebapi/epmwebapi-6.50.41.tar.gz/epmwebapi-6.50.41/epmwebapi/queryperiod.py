import datetime

class QueryPeriod(object):
    """
    Class representing a period of time for queries.
    """

    def __init__(self, start:datetime.datetime, end:datetime.datetime):
        """
        Initializes a new `QueryPeriod` object.

        :param start: Starting time of this query period.
        :type start: datetitme.datetime
        :param end: Ending time of this query period.
        :type end: datetime.datetime
        """
        self._start = start
        self._end = end

    @property
    def start(self) -> datetime.datetime:
        """
        Returns or sets the starting time of a period.
        :param value: Starting time of a period.
        :type value: datetime.datetime
        :return: Starting time of this query period.
        :rtype: datetime.datetime
        """
        return self._start

    @start.setter
    def start(self, value:datetime.datetime):
        self._start = value

    @property
    def end(self) -> datetime.datetime:
        """
        Returns or sets the ending time of a period.
        :param value: Ending time of a period.
        :type value: datetime.datetime
        :return: Ending time of this query period.
        :rtype: datetime.datetime
        """
        return self._end

    @end.setter
    def end(self, value:datetime.datetime):
        self._end = value
