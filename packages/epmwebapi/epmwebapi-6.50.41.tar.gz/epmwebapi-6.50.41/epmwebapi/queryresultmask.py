from enum import Enum

class QueryResultMask(Enum):
    """
    Enumeration with values for query result masks.
    """

    Unknown = 0

    Identity = 1

    Name = 2

    Description = 4

    Type = 8

    Path = 16

    All = 31

