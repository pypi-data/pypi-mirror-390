from .resourcesmanager import ResourcesManager

class PortalResources(ResourcesManager):
  """
  Class representing an `epmwebapi.resourcesmanager.ResourcesManager` object from **EPM Portal**.
  """
  def __init__(self, authorizationService, webApi):
    super().__init__(authorizationService, webApi, 'resources')



    

