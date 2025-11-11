
"""
### Easily Access Data from an Elipse Plant Manager Server in Python

Welcome to the **EPM Web API**, your bridge to unlock the power of an [**Elipse Plant Manager**](https://www.elipse.com.br/produto/elipse-plant-manager/ "Elipse Plant Manager website") server directly through Python. This API was designed to simplify and streamline the access to **EPM** data, offering a wide range of functionality that enable reading, writing, and querying data, in addition to allow creating datasets and exploring **EPM** data modeling.

The main resources are:

* **Directly accessing data**
  * **Reading and writing data**: Get **EPM** data easily and update information as needed.
  * **Streamlined queries**: Execute powerful queries to retrieve specific data with reliability.
* **Manipulating Data**
  * **Creating Datasets**: Simplify the process of creating custom data sets.
  * **Transforming Data**: Adapt and manipulate data according to specific needs.
* **Exploring EPM Data Modeling**
  * **Querying Models**: View and explore **EPM** data structure for a deep understanding.
  * **Creating and Instantiating Types**: Develop and use custom types effectively.
"""

from ._version import __version__

from .epmconnection import EpmConnection, ImportMode, BadArgumentException
from .epmdataobject import EpmDataObject, ClampingMode
from .epmvariable import RetrievalMode
from .epmmodelobject import EpmModelObject, InstanceNameDuplicatedException, InvalidObjectNameException, \
    InvalidObjectPropertyException, InvalidObjectTypeException, InvalidSourceVariableException, \
    ObjectDependenciesException
from .basicvariable import BasicVariable, TagType
from .epmobject import EpmObject
from .queryperiod import QueryPeriod
from .aggregatedetails import AggregateDetails
from .aggregatedetails import AggregateType
from .browseitemmodeljson import BrowseItemModelJSON
from .browsemodeljson import BrowseModelJSON
from .readitemmodeljson import ReadItemModelJSON
from .readmodeljson import ReadModelJSON
from .writeitemmodeljson import WriteItemModelJSON
from .writemodeljson import WriteModelJSON
from .querymodeljson import QueryModelJSON
from .domainfilter import DomainFilter
from .downloadtype import DownloadType
from .customtypedefinition import CustomTypeDefinition, CustomTypeAlreadyExistsException, \
    CustomTypeDependenciesException, DuplicatedPropertiesNamesException, DuplicatedPropertiesTypeException, \
    InvalidCustomTypeNameException, InvalidIconException, InvalidPropertyNameException, InvalidPropertyTypeException, \
    MissingPropertyNameException
from .datasetconfig import DatasetConfig, PeriodUnit
from .datasetpen import DatasetPen
from .epmutils import EpmUtils
from .dataobjectattributes import DataObjectAttributes
