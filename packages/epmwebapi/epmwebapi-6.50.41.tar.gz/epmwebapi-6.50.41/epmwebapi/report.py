import requests
import json


from typing import Dict, Any
from .resource import Resource
from .mimetype import Application
from .exporttype import ExportType

class Report(Resource):
  """
  Class representing a Report (rdlx file) from **EPM Portal**'s or **EPM Processor**'s Resource Manager.
  """

  def __init__(self, resourcesManager, id, name, description):
    super().__init__(resourcesManager, id, name, description, Application.OctetStream.value)

  def export(self, type:ExportType, params:Dict[str, Any]) -> any:
    """
    Exports a Report from Resources Manager to the specified type.

    :param type: Type of Exportation. Possible values are `epmwebapi.downloadtype.ExportType.Excel2003`, `epmwebapi.downloadtype.ExportType.Excel`, 
        `epmwebapi.downloadtype.ExportType.Word`, `epmwebapi.downloadtype.ExportType.Pdf`, `epmwebapi.downloadtype.ExportType.Csv`, `epmwebapi.downloadtype.ExportType.Json`,
        `epmwebapi.downloadtype.ExportType.Xml`, `epmwebapi.downloadtype.ExportType.Tiff`, `epmwebapi.downloadtype.ExportType.Mht`.
    :type type: epmwebapi.exporttype
    :return: Exported Report. 
    :rtype: any
    """
    return self._resourcesManager._export(self._id, type, params)
