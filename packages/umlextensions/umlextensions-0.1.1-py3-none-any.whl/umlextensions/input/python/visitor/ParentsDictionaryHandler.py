
from typing import List
from typing import Union

from logging import Logger
from logging import getLogger

from umlextensions.input.python.pythonpegparser.PythonParser import PythonParser

from umlextensions.input.python.visitor.ParserTypes import ChildName
from umlextensions.input.python.visitor.ParserTypes import Children
from umlextensions.input.python.visitor.ParserTypes import ParentName
from umlextensions.input.python.visitor.ParserTypes import Parents
from umlextensions.input.python.visitor.ParserTypes import PyutClassName


class ParentsDictionaryHandler:

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._parents:      Parents     = Parents({})

    @property
    def parents(self) -> Parents:
        return self._parents

    @parents.setter
    def parents(self, newValue: Parents):
        self._parents = newValue

    def createParentChildEntry(self, argumentsCtx: PythonParser.ArgumentsContext, childName: Union[PyutClassName, ChildName]):

        args:       PythonParser.ArgsContext = argumentsCtx.args()
        parentName: ParentName               = ParentName(args.getText())
        self.logger.debug(f'Class: {childName} is subclass of {parentName}')

        multiParents = parentName.split(',')
        if len(multiParents) > 1:
            self._handleMultiParentChild(multiParents=multiParents, childName=childName)
        else:
            self._updateParentsDictionary(parentName=parentName, childName=childName)

    def _handleMultiParentChild(self, multiParents: List[str], childName: Union[PyutClassName, ChildName]):
        """

        Args:
            multiParents:
            childName:

        """
        self.logger.debug(f'handleMultiParentChild: {childName} -- {multiParents}')
        for parent in multiParents:
            # handle the special case
            if parent.startswith('metaclass'):
                splitParent: List[str] = parent.split('=')
                parentName: ParentName = ParentName(splitParent[1])
                self._updateParentsDictionary(parentName=parentName, childName=childName)
            else:
                parentName = ParentName(parent)
                self._updateParentsDictionary(parentName=parentName, childName=childName)

    def _updateParentsDictionary(self, parentName: ParentName, childName: Union[PyutClassName, ChildName]):
        """
        Update our dictionary of parents. If the parent dictionary
        does not have an entry, create one with the single child.

        Args:
            parentName:     The prospective parent
            childName:      Child class name

        """
        if parentName in self._parents:
            children: Children = self._parents[parentName]
            children.append(childName)
        else:
            children = [childName]

        self._parents[parentName] = children
