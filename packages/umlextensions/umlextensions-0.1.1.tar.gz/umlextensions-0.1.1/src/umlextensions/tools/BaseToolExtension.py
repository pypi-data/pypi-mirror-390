
from typing import cast

from logging import Logger
from logging import getLogger

from abc import ABC
from abc import abstractmethod

from wx import BeginBusyCursor
from wx import EndBusyCursor

from wx import Yield as wxYield

from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.IExtensionsFacade import IExtensionsFacade
from umlextensions.extensiontypes.BaseExtension import BaseExtension


class BaseToolExtension(BaseExtension, ABC):
    """
    Base class for extensions that can manipulate UML diagrams.  Examples,
    include but are not limited to:

        * Various layouts (Sugiyama, Orthogonal, Force Directed
        * Arranging non crossing links
        * Arranging orthogonal links
    """
    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._frameInformation: FrameInformation = cast(FrameInformation, None)

    def executeTool(self):
        """
        This is used by the Plugin Manger to invoke the tool.  This should NOT
        be overridden
        """
        if self.setOptions() is True:

            if self._autoSelectAll is True:
                self._extensionsFacade.selectUmlShapes()
            self._extensionsFacade.requestCurrentFrameInformation(callback=self._executeTool)

    def _executeTool(self, frameInformation: FrameInformation):

        self._frameInformation = frameInformation

        if frameInformation.frameActive is False:
            self.showNoUmlFrameDialog()
        else:
            self._selectedOglObjects = frameInformation.selectedUmlShapes  # syntactic sugar

            if len(self._selectedOglObjects) == 0 and self._requireSelection is True:
                self.showNoSelectedUmlShapesDialog()
            else:
                BeginBusyCursor()
                wxYield()
                self.doAction()
                EndBusyCursor()

    @abstractmethod
    def setOptions(self) -> bool:
        """
        Prepare for the tool action
        This can be used to query the user for additional plugin options

        Returns: If False, cancel the tool action 'True' to proceed
        """
        pass

    @abstractmethod
    def doAction(self):
        """
        Do the tool's action
        """
        pass
