from enum import Enum

class PerformUpdateType(Enum):
    """
    Enumeration with values for types of updates.
    """

    Insert = 0

    Remove = 1

    Replace = 2

    Update = 3

