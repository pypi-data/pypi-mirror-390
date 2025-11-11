from .itempathjson import ItemPathJSON
import datetime as dt
from .datavaluejson import DataValueJSON
from .epmvariable import EpmVariable

class EpmProperty(EpmVariable):
    """
    Class representing an EPM Object property.
    """

    def __init__(self, epmConnection, name, path, itemPath):
        super().__init__(epmConnection, name, path, itemPath)






