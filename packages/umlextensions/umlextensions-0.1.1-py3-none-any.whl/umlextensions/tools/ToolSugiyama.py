
from logging import Logger
from logging import getLogger

from umlshapes.ShapeTypes import UmlShapes

from umlextensions.IExtensionsFacade import IExtensionsFacade
from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import Version
from umlextensions.tools.BaseToolExtension import BaseToolExtension
from umlextensions.tools.sugiyama.Sugiyama import Sugiyama


class ToolSugiyama(BaseToolExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade=extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name      = ExtensionName('Sugiyama Automatic Layout')
        self._author    = Author('Nicolas Dubois <nicdub@gmx.ch>')
        self._version   = Version('1.1')

        self._autoSelectAll = False

    def setOptions(self) -> bool:
        """
        Prepare for the tool action.
        This can be used to ask some questions to the user.

        Returns: If False, the import should be cancelled.  'True' to proceed
        """
        return True

    def doAction(self):

        self.logger.info(f'Begin Sugiyama algorithm')

        selectedUmlShapes: UmlShapes = self._frameInformation.selectedUmlShapes

        sugiyama: Sugiyama = Sugiyama(extensionsFacade=self._extensionsFacade, umlFrame=self._frameInformation.umlFrame)
        sugiyama.createInterfaceOglALayout(umlShapes=selectedUmlShapes)

        sugiyama.levelFind()
        sugiyama.addVirtualNodes()
        sugiyama.barycenter()

        # noinspection PyProtectedMember
        self.logger.info(f'Number of hierarchical intersections: {sugiyama._getNbIntersectAll()}')

        sugiyama.addNonHierarchicalNodes()
        sugiyama.fixPositions()

        self._extensionsFacade.extensionModifiedProject()
        self._extensionsFacade.refreshFrame()

        self.logger.info('End Sugiyama algorithm')
