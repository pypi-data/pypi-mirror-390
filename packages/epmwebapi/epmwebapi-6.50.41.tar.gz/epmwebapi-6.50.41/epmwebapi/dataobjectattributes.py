from enum import IntFlag

class DataObjectAttributes(IntFlag):
    """
    Enumeration with all types of attributes for Data Objects.
    """

    Unspecified = 0

    Name = 1

    Description = 2

    EU = 4

    LowLimit = 8

    HighLimit = 16

    Clamping = 32

    Domain = 64

    Active = 128

    TagType = 256

    All = 65535

