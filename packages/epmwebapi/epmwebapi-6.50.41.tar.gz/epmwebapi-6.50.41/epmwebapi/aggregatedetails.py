from enum import Enum
import datetime as dt

class AggregateType(Enum):
    """
    Enumeration with all types of Aggregate functions.
    """
    Trend = 'Trend'
    Interpolative = 'Interpolative'
    Average = 'Average'
    TimeAverage = 'TimeAverage'
    Total = 'Total'
    Minimum = 'Minimum'
    Maximum = 'Maximum'
    MinimumActualTime = 'MinimumActualTime'
    MaximumActualTime = 'MaximumActualTime'
    Range = 'Range'
    AnnotationCount = 'AnnotationCount'
    Count = 'Count'
    DurationInStateZero = 'DurationInStateZero'
    DurationInStateNonZero = 'DurationInStateNonZero'
    PercentInStateZero = 'PercentInStateZero'
    PercentInStateNonZero = 'PercentInStateNonZero'
    NumberOfTransitions = 'NumberOfTransitions'
    Start = 'Start'
    End = 'End'
    Delta = 'Delta'
    DurationGood = 'DurationGood'
    DurationBad = 'DurationBad'
    PercentGood = 'PercentGood'
    PercentBad = 'PercentBad'
    WorstQuality = 'WorstQuality'
    TimeAverage2 = 'TimeAverage2'
    Total2 = 'Total2'
    Minimum2 = 'Minimum2'
    Maximum2 = 'Maximum2'
    MinimumActualTime2 = 'MinimumActualTime2'
    MaximumActualTime2 = 'MaximumActualTime2'
    Range2 = 'Range2'
    StartBound = 'StartBound'
    EndBound = 'EndBound'
    DeltaBounds = 'DeltaBounds'
    WorstQuality2 = 'WorstQuality2'
    StandardDeviationPopulation = 'StandardDeviationPopulation'
    VariancePopulation = 'VariancePopulation'
    StandardDeviationSample = 'StandardDeviationSample'
    VarianceSample = 'VarianceSample'

class AggregateDetails(object):
    """
    AggregateDetails class.
    """

    def __init__(self, interval:dt.timedelta, type:AggregateType):
        """
        Creates a new instance of an AggregateDetails object.
        """
        self._interval = interval
        self._type = type.value

    @property
    def interval(self) -> dt.timedelta:
        """
        Returns or sets a time interval for this AggregateDetails object.
        :return: A `timedelta` value indicating a time interval.
        """
        return self._interval

    @interval.setter
    def interval(self, value:dt.timedelta):
        self._interval = value

    @property
    def type(self) -> AggregateType:
        """
        Returns or sets the type of an Aggregate function.
        :return: An `epmwebapi.aggregatedetails.AggregateType` value.
        """
        return self._type

    @type.setter
    def type(self, value:AggregateType):
        self._type = value
