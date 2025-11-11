from enum import Enum

class HistoryUpdateType(Enum):
    """
    Enumeration with all types of historical updates.
    """

    Insert = 0

    Remove = 1

    Replace = 2

    Update = 3


