from .domainfilter import DomainFilter

from enum import IntFlag


class DataObjectsFilterType(IntFlag):
  """
  Enumeration with all types of filter for Data Objects.
  """

  BasicVariable = 1

  ExpressionVariable = 2


class DataObjectsFilter(object):
  """
  Class representing a Data Object Filter.
  """

  def __init__(self, type:DataObjectsFilterType = None, name:str = None, eu:str = None, description:str = None, domain:DomainFilter = None):
    """
    Creates a new instance of a Data Object Filter.

    :param type: An optional parameter indicating a type of Data Object Filter. Default is None.
    :type type: `DataObjectsFilterType`
    :param name: An optional parameter indicating a name to a Data Object Filter. Use `*` for **All**. Default is None.
    :type name: str
    :param eu: An optional parameter indicating an engineering unit of a Data Object Filter. Use `*` for **All**. Default is None.
    :type eu: str
    :param description: An optional parameter indicating a description of a Data Object Filter.  Use `*` for **All**. Default is None.
    :type description: str
    :param domain: Optional parameter indicating a Domain for a Data Object Filter. Possible values are 0 (zero, **All**), 1 (one, **Continuous**), or 2 (two, **Discrete**). Default is None.
    :type domain: `epmwebapi.domainfilter.DomainFilter`
    """
    self._type = DataObjectsFilterType.BasicVariable | DataObjectsFilterType.ExpressionVariable if type == None else type
    self._name = '*' if name == None else name
    self._eu = '*' if eu == None else eu
    self._description = description
    self._domain = DomainFilter.All if domain == None else domain

  @property
  def type(self) -> DataObjectsFilterType:
    """
    Returns a type of Filter of a Data Object. Possible values are `BasicVariable`, `ExpressionVariable` or both. Default is None.
    :return: A `DataObjectsFilterType` object.
    :rtype: DataObjectsFilterType
    """
    return self._type

  @property
  def name(self) -> str:
    """
    Returns the name of a Data Object Filter. Default is None.

    :return: A `str` with the name of a Data Object Filter. A value of `*` means "All".
    :rtype: str
    """
    return self._name
  
  @property
  def eu(self) -> str:
    """
    Returns the engineering unit of a Data Object Filter. Default is None.

    :return: A `str` with the engineering unit of a Data Object Filter. A value of `*` means "All".
    :rtype: str
    """
    return self._eu

  @property
  def description(self) -> str:
    """
    Returns the description of a Data Object Filter. Default is None.

    :return: A `str` with the description of a Data Object Filter. A value of `*` means "All".
    :rtype: str
    """
    return self._description

  @property
  def domain(self) -> DomainFilter:
    """
    Returns the domain of a Data Object Filter. Default is None.

    :return: An `epmwebapi.domainfilter.DomainFilter` enumeration. Possible values are 0 (zero, **All**), 1 (one, **Continuous**), or 2 (two, **Discrete**).
    :rtype: epmwebapi.domainfilter.DomainFilter
    """
    return self._domain
