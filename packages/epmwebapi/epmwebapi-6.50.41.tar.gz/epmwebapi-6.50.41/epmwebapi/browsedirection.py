from enum import IntFlag

class BrowseDirection(IntFlag):
    """
    Enumeration with all types of browsing directions.
    """
    # <summary>
    # No classes are selected.
    # </summary>
    Forward = 0,
    """
    There are no classes selected.
    """

    #/ <summary>
    #/ The node is an object.
    #/ </summary>
    Inverse = 1,
    """
    This node is an object.
    """
