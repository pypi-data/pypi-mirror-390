from enum import Enum

class NodeAttributes(Enum):
    """
    Enumeration with values for node attributes.
    """

    # <summary>
    # The canonical identifier for the node.
    # </summary>
    NodeId = 1
    """
    Node's canonical identifier.
    """
    # <summary>
    # The class of the node.
    # </summary>
    NodeClass = 2
    """
    Node's class.
    """
    # <summary>
    # A non-localized, human readable name for the node.
    # </summary>
    BrowseName = 3
    """
    Non-localized, human readable name for a node.
    """
    # <summary>
    # A localized, human readable name for the node.
    # </summary>
    DisplayName = 4
    """
    Localized, human readable name for a node.
    """
    # <summary>
    # A localized description for the node.
    # </summary>
    Description = 5
    """
    Node's localized description.
    """
    # <summary>
    # Indicates which attributes are writeable.
    # </summary>
    WriteMask = 6
    """
    Indicates writable attributes.
    """
    # <summary>
    # Indicates which attributes are writeable by the current user.
    # </summary>
    UserWriteMask = 7
    """
    Indicates writable attributes for the current user.
    """
    # <summary>
    # Indicates that a type node may not be instantiated.
    # </summary>
    IsAbstract = 8
    """
    Indicates that a type node may not be instantiated.
    """
    # <summary>
    # Indicates that forward and inverse references have the same meaning.
    # </summary>
    Symmetric = 9
    """
    Indicates that forward and inverse references have the same meaning.
    """
    # <summary>
    # The browse name for an inverse reference.
    # </summary>
    InverseName = 10
    """
    Browsing name for an inverse reference.
    """
    # <summary>
    # Indicates that following forward references within a view will not cause a loop.
    # </summary>
    ContainsNoLoops = 11
    """
    Indicates that the following forward references in a view do not cause a loop.
    """
    # <summary>
    # Indicates that the node can be used to subscribe to events.
    # </summary>
    EventNotifier = 12
    """
    Indicates that a node can be used to subscribe to events.
    """
    # <summary>
    # The value of a variable.
    # </summary>
    Value = 13
    """
    Variable's value.
    """
    # <summary>
    # The node id of the data type for the variable value.
    # </summary>
    DataType = 14
    """
    Data type's node ID for the variable's value.
    """
    # <summary>
    # The number of dimensions in the value.
    # </summary>
    ValueRank = 15
    """
    Number of dimensions in the value.
    """
    # <summary>
    # The length for each dimension of an array value.
    # </summary>
    ArrayDimensions = 16
    """
    Length for each dimension of an array value.
    """
    # <summary>
    # How a variable may be accessed.
    # </summary>
    AccessLevel = 17
    """
    The way a variable can be accessed.
    """
    # <summary>
    # How a variable may be accessed after taking the user's access rights into account.
    # </summary>
    UserAccessLevel = 18
    """
    The way a variable can be accessed after considering a user's access rights.
    """
    # <summary>
    # Specifies (in milliseconds) how fast the server can reasonably sample the value for changes.
    # </summary>
    MinimumSamplingInterval = 19
    """
    Specifies how fast a server can reasonably sample a value for changes, in milliseconds.
    """
    # <summary>
    # Specifies whether the server is actively collecting historical data for the variable.
    # </summary>
    Historizing = 20
    """
    Specifies whether a server is actively collecting historical data for a variable.
    """
    # <summary>
    # Whether the method can be called.
    # </summary>
    Executable = 21
    """
    Whether a method can be called.
    """
    # <summary>
    # Whether the method can be called by the current user.
    # </summary>
    UserExecutable = 22
    """
    Whether a method can be called by the current user.
    """
