from .resourcesmanager import ResourcesManager

class ProcessorResources(ResourcesManager):
  """
  Class representing an `epmwebapi.resourcesmanager.ResourcesManager` object from **EPM Processor**.
  """

  def __init__(self, authorizationService, webApi):
    super().__init__(authorizationService, webApi, 'processor')



    

