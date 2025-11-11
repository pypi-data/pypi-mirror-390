from enum import Enum

class ExportType(Enum):
    """
    An enumeration with all types of Export Type.
    """
    Excel2003 = "Excel2003"
    Excel = "Excel"
    Word = "Word"
    Pdf = "Pdf"
    Csv = "Csv"
    Json = "Json"
    Xml = "Xml"
    Tiff = "Tiff"
    Mht = "Mht"