from enum import IntFlag

class NodeClassMask(IntFlag):
    """
    Enumeration with values for node class masks.
    """

    # <summary>
    # No classes are selected.
    # </summary>
    Unspecified = 0,
    """
    There are no classes selected.
    """
    #/ <summary>
    #/ The node is an object.
    #/ </summary>
    Object = 1,
    """
    Node is an object.
    """
    #/ <summary>
    #/ The node is a variable.
    #/ </summary>
    Variable = 2,
    """
    Node is a variable.
    """
    #/ <summary>
    #/ The node is a method.
    #/ </summary>
    Method = 4,
    """
    Node is a method.
    """
    #/ <summary>
    #/ The node is an object type.
    #/ </summary>
    ObjectType = 8,
    """
    Node is an object type.
    """
    #/ <summary>
    #/ The node is an variable type.
    #/ </summary>
    VariableType = 16,
    """
    Node is a variable type.
    """
    #/ <summary>
    #/ The node is a reference type.
    #/ </summary>
    ReferenceType = 32,
    """
    Node is a reference type.
    """
    #/ <summary>
    #/ The node is a data type.
    #/ </summary>
    DataType = 64,
    """
    Node is a data type.
    """
    #/ <summary>
    #/ The node is a view.
    #/ </summary>
    View = 128,
    """
    Node is a view.
    """
