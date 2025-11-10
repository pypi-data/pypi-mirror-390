
from umlextensions.extensiontypes.BaseFormat import BaseFormat

from umlextensions.extensiontypes.ExtensionDataTypes import FileSuffix
from umlextensions.extensiontypes.ExtensionDataTypes import FormatName
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionDescription


class InputFormat(BaseFormat):
    """
    Syntactic sugar
    """
    def __init__(self, formatName: FormatName, fileSuffix: FileSuffix, description: ExtensionDescription):
        super().__init__(formatName=formatName, fileSuffix=fileSuffix, description=description)

