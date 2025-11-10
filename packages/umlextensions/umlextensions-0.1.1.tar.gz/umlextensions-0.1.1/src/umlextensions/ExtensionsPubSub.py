
from typing import Callable
from typing import NewType

from logging import Logger
from logging import getLogger

from enum import Enum

from codeallybasic.BasePubSubEngine import BasePubSubEngine
from codeallybasic.BasePubSubEngine import Topic

class ExtensionsMessageType(Enum):
    REQUEST_FRAME_INFORMATION  = 'Request Frame Information'
    REFRESH_FRAME              = 'Refresh Frame'
    EXTENSION_MODIFIED_PROJECT = 'Extension Modified Project'
    SELECT_UML_SHAPES          = 'Select UML Shapes'
    ADD_SHAPE                  = 'Add Shape'
    GET_SELECTED_UML_SHAPES    = 'Get Selected UML Shapes'
    WIGGLE_SHAPES              = 'Wiggle Shapes'


AdapterId = NewType('AdapterId', str)

EXTENSIONS_ID: AdapterId = AdapterId('sodas-teamwork-rushes-toads')


class ExtensionsPubSub(BasePubSubEngine):
    """
    Since you are using this specific pub sub engine this module uses the message
    types specifically associated with this module.  The messages
    and the UML Diagrammer needs to use this engine to subscribe to the particular message
    """
    def __init__(self):
        super().__init__()
        self.logger: Logger = getLogger(__name__)

    # def subscribe(self, messageType: ExtensionsMessageType, adapterId: AdapterId, listener: Callable):
    def subscribe(self, messageType: ExtensionsMessageType, listener: Callable):
        self._subscribe(topic=Topic(messageType.value), listener=listener)

    # def sendMessage(self, messageType: ExtensionsMessageType, adapterId: AdapterId, **kwargs):
    def sendMessage(self, messageType: ExtensionsMessageType, **kwargs):
        self._sendMessage(topic=Topic(messageType.value), **kwargs)
