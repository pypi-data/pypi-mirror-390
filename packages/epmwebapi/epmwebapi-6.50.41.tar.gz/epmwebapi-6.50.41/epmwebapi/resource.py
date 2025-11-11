import requests
import json

from .downloadtype import DownloadType

class Resource(object):
  """
  Class representing a Resource from **EPM Portal**'s or **EPM Processor**'s Resource Manager.
  """

  def __init__(self, resourcesManager, id, name, description, mimeType):
    self._resourcesManager = resourcesManager
    self._id = id
    self._name = name
    self._description = description
    self._mimeType = mimeType

  def download(self, type:DownloadType) -> any:
    """
    Downloads a Resource from Resources Manager.

    :param type: Type of Resource. Possible values are `epmwebapi.downloadtype.DownloadType.Text`, `epmwebapi.downloadtype.DownloadType.Json`, or `epmwebapi.downloadtype.DownloadType.Binary`.
    :type type: epmwebapi.downloadtype
    :return: Downloaded Resource. For **Text** return a `str`, for **Json** returns a `dict`, and for **Binary** returns a `BytesIO`.
    :rtype: any
    """
    return self._resourcesManager._download(self._id, type)

  def upload(self, file:str) -> any:
    """
    Uploads the current Resource to an **EPM Server**.

    :param file: File to upload.
    :type file: str
    :return: Uploaded Resource.
    :rtype: any
    """
    return self._resourcesManager._updateFile(self._id, self._name, self._mimeType, file)

  def delete(self):
    """
    Deletes the current Resouce.
    """

    return self._resourcesManager._delete(self._id)


