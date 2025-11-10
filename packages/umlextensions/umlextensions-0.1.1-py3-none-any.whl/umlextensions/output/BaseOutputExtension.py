
from logging import Logger
from logging import getLogger

from umlextensions.IExtensionsFacade import IExtensionsFacade
from umlextensions.extensiontypes.BaseExtension import BaseExtension


class BaseOutputExtension(BaseExtension):
    """
        Base class for extensions that can convert UML Diagrams into foreign
        structured data.  Examples include but are not limited to:

        * Mermaid
        * PDF
        * Images (png, jpg, bmp, etc
        * Generate Python code
        * Generate Java code

    """
    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade)
        self.logger: Logger = getLogger(__name__)
