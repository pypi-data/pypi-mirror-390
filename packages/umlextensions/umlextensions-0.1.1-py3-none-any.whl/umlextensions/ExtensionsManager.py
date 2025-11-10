
from typing import cast
from typing import Dict
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from enum import Enum

from dataclasses import field
from dataclasses import dataclass

from wx import OK
from wx import ICON_ERROR

from wx import NewIdRef
from wx import Window
from wx import RichMessageDialog

from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlextensions.ErrorFormatter import ErrorFormatter
from umlextensions.ExtensionsPreferences import ExtensionsPreferences

from umlextensions.ExtensionsFacade import ExtensionsFacade
from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName

from umlextensions.input.BaseInputExtension import BaseInputExtension
from umlextensions.input.InputPython import InputPython
from umlextensions.tools.BaseToolExtension import BaseToolExtension

from umlextensions.tools.ToolSugiyama import ToolSugiyama

from umlextensions.ExtensionsPubSub import ExtensionsPubSub


# Return type from wx.NewIdRef()
WindowId = NewType('WindowId', int)

#
#  Both of these hold the class extension types for the Extension classes
#
ExtensionList  = NewType('ExtensionList',  List[type])
ExtensionIDMap = NewType('ExtensionIDMap', Dict[WindowId, type])

def createExtensionIdMapFactory() -> ExtensionIDMap:
    return ExtensionIDMap({})

class ExtensionMapType(Enum):
    INPUT_MAP  = 'InputMap'
    OUTPUT_MAP = 'OutputMap'
    TOOL_MAP   = 'ToolMap'
    NONE       = 'None'

#
# Some nice syntactic sugar
#
@dataclass
class BaseExtensionMap:
    mapType:        ExtensionMapType = ExtensionMapType.NONE
    extensionIdMap: ExtensionIDMap   = field(default_factory=createExtensionIdMapFactory)

@dataclass
class InputExtensionMap(BaseExtensionMap):
    def __init__(self):
        super().__init__()
        self.mapType = ExtensionMapType.INPUT_MAP

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f'{self.mapType} plugin count: {len(self.extensionIdMap)}'

@dataclass
class ToolExtensionMap(BaseExtensionMap):
    def __init__(self):
        super().__init__()
        self.mapType = ExtensionMapType.TOOL_MAP


TOOL_EXTENSIONS: ExtensionList = ExtensionList(
    [ToolSugiyama]
)
INPUT_EXTENSIONS: ExtensionList = ExtensionList(
    [InputPython]
)

@dataclass
class ExtensionDetails:
    name:    ExtensionName = ExtensionName('')
    author:  str = ''
    version: str = ''

class ExtensionsManager:
    """
    Manages the various extensions provided by this module

        InputExtension
        OutputExtension
        ToolExtension

    Is responsible for:

    * Identifying the extensions
    * Creating Tool, Input, & Output Menu ID References
    * Providing the callbacks that invoke the appropriate methods on the
    appropriate extensions to invoke their functionality.


    By convention prefix the plugin tool module name with the characters 'Tool'
    By convention prefix the plugin input module name with 'Input'
    By convention prefix the plugin output module name with 'Output'

    """
    def __init__(self, umlPubSubEngine: UmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        self._extensionPreferences: ExtensionsPreferences = ExtensionsPreferences()
        self._pubsub:               ExtensionsPubSub      = ExtensionsPubSub()
        self._extensionsFacade:     IExtensionsFacade     = ExtensionsFacade(self._pubsub, umlPubSubEngine=umlPubSubEngine)
        #
        #
        #
        self._inputExtensionsMap:  InputExtensionMap = InputExtensionMap()
        self._toolExtensionsMap:   ToolExtensionMap  = ToolExtensionMap()

        # self._inputExtensionClasses:  ExtensionList = cast(ExtensionList, None)

    @property
    def extensionsPubSub(self) -> ExtensionsPubSub:
        return self._pubsub

    @property
    def inputExtensions(self) -> ExtensionList:
        """
        Get the input extension types.

        Returns:  A copy of the list of input extension classes
        """
        return ExtensionList(INPUT_EXTENSIONS[:])

    @property
    def toolExtensions(self) -> ExtensionList:
        """
        Get the tool Extensions.

        Returns:    A copy of the list of classes (the Extension classes).
        """
        return ExtensionList(TOOL_EXTENSIONS[:])

    @property
    def inputExtensionsMap(self) -> InputExtensionMap:

        if len(self._inputExtensionsMap.extensionIdMap) == 0:
            self._inputExtensionsMap.extensionIdMap = self._mapWxIdsToExtensions(self.inputExtensions)

        return self._inputExtensionsMap

    @property
    def toolExtensionsMap(self) -> ToolExtensionMap:

        if len(self._toolExtensionsMap.extensionIdMap) == 0:
            self._toolExtensionsMap.extensionIdMap = self._mapWxIdsToExtensions(TOOL_EXTENSIONS)

        return self._toolExtensionsMap

    def doImport(self, wxId: WindowId) -> ExtensionDetails:
        """
        Args:
            wxId:       The ID ref of the menu item
        """
        idMap:             ExtensionIDMap     = self.inputExtensionsMap.extensionIdMap
        clazz:             type               = idMap[wxId]
        extensionInstance: BaseInputExtension = clazz(extensionsFacade=self._extensionsFacade)

        try:
            extensionInstance.executeImport()
        except (ValueError, Exception) as e:
            self._processError(e, dialogTitle='Input Extension Error')

        return ExtensionDetails(name=extensionInstance.name, version=extensionInstance.version, author=extensionInstance.author)

    def doToolAction(self, wxId: WindowId) -> ExtensionDetails:
        """
        Args:
            wxId:   The ID ref of the menu item
        """
        idMap:        ExtensionIDMap    = self.toolExtensionsMap.extensionIdMap
        clazz:        type              = idMap[wxId]
        toolInstance: BaseToolExtension = clazz(extensionsFacade=self._extensionsFacade)

        try:
            toolInstance.executeTool()
        except (ValueError, Exception) as e:
            self._processError(e, dialogTitle='Tool Extension Error')

        return ExtensionDetails(name=toolInstance.name, version=toolInstance.version, author=toolInstance.version)

    def _processError(self, e: Exception, dialogTitle: str):
        """
        Common error handler for extensions
        Args:
            e:
            dialogTitle:
        """
        errorMessage: str = ErrorFormatter.getErrorMessage()
        fs:           str = ErrorFormatter.getErrorStack(e)
        self.logger.error(fs)
        #
        # TODO: Build my own dialog so I can set the detailed text font
        booBoo: RichMessageDialog = RichMessageDialog(cast(Window, None),
                                                      message=errorMessage,
                                                      caption=dialogTitle,
                                                      style=ICON_ERROR | OK
                                                      )
        booBoo.ShowDetailedText(fs)
        booBoo.ShowModal()

    def _mapWxIdsToExtensions(self, extensionList: ExtensionList) -> ExtensionIDMap:
        """

        Args:
            extensionList:   List of the extensions to map

        Returns:  A map of window IDs to their associated extension types
        """

        pluginMap: ExtensionIDMap = ExtensionIDMap({})

        nb: int = len(extensionList)

        for x in range(nb):
            wxId: WindowId = NewIdRef()

            pluginMap[wxId] = extensionList[x]

        return pluginMap
