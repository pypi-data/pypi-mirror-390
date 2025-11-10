
from logging import Logger
from logging import getLogger

from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlextensions.ExtensionsTypes import FrameInformationCallback
from umlextensions.ExtensionsTypes import SelectedUmlShapesCallback

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.ExtensionsPubSub import ExtensionsMessageType
from umlextensions.ExtensionsPubSub import ExtensionsPubSub


class ExtensionsFacade(IExtensionsFacade):
    """
    This class simplifies communication between the extensions
    and the UML Diagrammer
    """

    def __init__(self, pubSub: ExtensionsPubSub, umlPubSubEngine: UmlPubSubEngine):

        self.logger: Logger = getLogger(__name__)

        self._pubsub:    ExtensionsPubSub = pubSub
        self._umlPubSub: UmlPubSubEngine  = umlPubSubEngine

    @property
    def umlPubSubEngine(self) -> UmlPubSubEngine:
        return self._umlPubSub

    def requestCurrentFrameInformation(self, callback: FrameInformationCallback):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.REQUEST_FRAME_INFORMATION, callback=callback)

    def selectUmlShapes(self):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.SELECT_UML_SHAPES)

    def getSelectedUmlShapes(self, callback: SelectedUmlShapesCallback):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.GET_SELECTED_UML_SHAPES, callback=callback)

    def extensionModifiedProject(self):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.EXTENSION_MODIFIED_PROJECT)

    def refreshFrame(self):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.REFRESH_FRAME)

    def addShape(self, umlShape: UmlShapeGenre | UmlLinkGenre):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.ADD_SHAPE, umlShape=umlShape)

    def wiggleShapes(self):
        self._pubsub.sendMessage(messageType=ExtensionsMessageType.WIGGLE_SHAPES)
