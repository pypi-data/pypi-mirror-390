import requests
import json
import collections
from .resource import Resource

from typing import OrderedDict

class Folder(object):
  """
  Class representing a Resources folder.
  """
  def __init__(self, resourcesManager, id, name, description):
    """
    Constructor for this class.

    :param resourcesManager: An `epmwebapi.resourcesmanager.ResourcesManager` object
    :type resourcesManager: epmwebapi.resourcesmanager.ResourcesManager
    :param id: Identification of this Folder
    :type id: str
    :param name: Name of this Folder
    :type name: str
    :param description: Description for this Folder
    :type description: str
    """
    self._resourcesManager = resourcesManager
    self._id = id
    self._name = name
    self._description = description


  def browse(self) -> OrderedDict[str, Resource]:
    """
    Lists all child elements from this Folder.

    :return: An Ordered Dictionary with all child elements from this Folder.
    :rtype: collections.OrderedDict[Resource|Folder]
    """
    return self._resourcesManager._browse(self._id)

  def upload(self, name:str, file:str, description:str=None, mimeType:str=None, thumbnail:str=None, thumbnailMimeType:str=None, starred:bool=None, overrideFile:bool=False) -> Resource:
    """
    Uploads a file to a Resouces Manager.

    :param name: Resource name.
    :type name: str
    :param file: File path.
    :type file: str
    :param description: Optional parameter with a Resource description. Default is None.
    :type description: str
    :param mimeType: An optional MIME type for this Resource. It can be one of the options of enumerations `epmwebapi.mimetype.Application`, `epmwebapi.mimetype.Text`, `epmwebapi.mimetype.Image`, `epmwebapi.mimetype.Audio`, or `epmwebapi.mimetype.Video`. Default is None.
    :type mimeType: epmwebapi.mimetype.Application|epmwebapi.mimetype.Text|epmwebapi.mimetype.Image|epmwebapi.mimetype.Audio|epmwebapi.mimetype.Video
    :param thumbnail: An optional thumbnail for this Resource. Default is None.
    :type thumbnail: str
    :param thumbnailMimeType: An optional MIME type for this thumbnail. It can be one of the options of enumerations `epmwebapi.mimetype.Application`, `epmwebapi.mimetype.Text`, `epmwebapi.mimetype.Image`, `epmwebapi.mimetype.Audio`, or `epmwebapi.mimetype.Video`. Default is None.
    :type thumbnailMimeType: epmwebapi.mimetype.Application|epmwebapi.mimetype.Text|epmwebapi.mimetype.Image|epmwebapi.mimetype.Audio|epmwebapi.mimetype.Video
    :param starred: Optional parameter indicating whether this Resource is starred. Default is None.
    :type starred: bool
    :param overrideFile: Optional parameter indicating whether the file can be overridden. Default is None.
    :type overrideFile: bool
    :return: An `epmwebapi.resource.Resource` object.
    :rtype: epmwebapi.resource.Resource
    """
    
    return self._resourcesManager._upload(self._id, name, file, description, mimeType, thumbnail, thumbnailMimeType, starred, overrideFile)

  def createFolder(self, name:str, description:str) -> any:
    """
    Creates a new Folder.

    :param name: Folder name.
    :type name: str
    :param description: Folder description
    :type description: str
    :return: The Folder just created.
    :rtype: epmwebapi.resourcesmanager.ResourcesManager
    """
    
    return self._resourcesManager._createFolder(self._id, name, description)

  def delete(self):
    """
    Deletes the current Folder.
    """
    return self._resourcesManager._delete(self._id)
