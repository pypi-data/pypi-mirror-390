
from abc import ABC
from abc import abstractmethod

from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.ShapeTypes import UmlShapeGenre
from umlshapes.pubsubengine.UmlPubSubEngine import UmlPubSubEngine

from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.ExtensionsTypes import FrameInformationCallback
from umlextensions.ExtensionsTypes import SelectedUmlShapesCallback


class IExtensionsFacade(ABC):
    """
    This facade simplifies communication to the UML diagrammer.  This interface serves as a front-facing interface
    that masks the complexity of the UML Diagrammer
    """
    @property
    @abstractmethod
    def umlPubSubEngine(self) -> UmlPubSubEngine:
        pass

    @abstractmethod
    def requestCurrentFrameInformation(self, callback: FrameInformationCallback) -> FrameInformation:
        pass

    @abstractmethod
    def extensionModifiedProject(self):
        pass

    @abstractmethod
    def selectUmlShapes(self):
        pass

    @abstractmethod
    def getSelectedUmlShapes(self, callback: SelectedUmlShapesCallback):
        pass

    @abstractmethod
    def refreshFrame(self):
        pass

    @abstractmethod
    def addShape(self, umlShape: UmlShapeGenre | UmlLinkGenre):
        pass

    @abstractmethod
    def wiggleShapes(self):
        pass
