
from typing import List
from typing import Dict
from typing import Union
from typing import NewType

from enum import Enum

from dataclasses import dataclass

from pyutmodelv2.PyutClass import PyutClass

VERSION: str = '3.0'

PyutClassName = NewType('PyutClassName', str)
ParentName    = NewType('ParentName',    str)
PropertyName  = NewType('PropertyName',  str)
ChildName     = NewType('ChildName',     str)

PropertyNames = NewType('PropertyNames', List[PropertyName])
PyutClasses   = NewType('PyutClasses',   Dict[PyutClassName, PyutClass])

PropertyMap   = NewType('PropertyMap',    Dict[PyutClassName, PropertyNames])
Children      = List[Union[PyutClassName, ChildName]]
Parents       = NewType('Parents',        Dict[ParentName,    Children])

AssociateName = PyutClassName

class AssociationType(Enum):

    ASSOCIATION = 'ASSOCIATION'
    AGGREGATION = 'AGGREGATION'
    COMPOSITION = 'COMPOSITION'
    INHERITANCE = 'INHERITANCE'
    INTERFACE   = 'INTERFACE'

@dataclass
class Associate:
    associateName:   AssociateName   = AssociateName('')
    associationType: AssociationType = AssociationType.ASSOCIATION


Associates = NewType('Associates', List[Associate])

#
# e.g.
#     @property
#     def pages(self) -> Pages:
#         return self._pages
# In the above "Pages" is the AssociateName and goes in the List for the method containing PyutClassName
#
# e.g.
#  self.pages: Pages = Pages({})
#
#  Pages is the AssociateName and the enclosing class for the __init__ method is the PyutClassName
#
#
Associations = NewType('Associations', Dict[PyutClassName, Associates])
