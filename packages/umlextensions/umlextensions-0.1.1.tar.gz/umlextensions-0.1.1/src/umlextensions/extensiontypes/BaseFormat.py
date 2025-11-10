
from abc import ABC

from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionDescription
from umlextensions.extensiontypes.ExtensionDataTypes import FileSuffix
from umlextensions.extensiontypes.ExtensionDataTypes import FormatName

from umlextensions.extensiontypes.InvalidPluginExtensionException import InvalidPluginExtensionException
from umlextensions.extensiontypes.InvalidPluginNameException import InvalidPluginNameException

DOT:                str = '.'
SPECIAL_CHARACTERS: str = '!@#$%^&*_+-=[]{};:,.<>?/|\'\"'


class BaseFormat(ABC):
    """
    Provides the basic capabilities;  Should not be directly instantiated;
    TODO:  Figure out how to prevent that
    https://stackoverflow.com/questions/7989042/preventing-a-class-from-direct-instantiation-in-python#7990308
    If we do the above; have to figure out how to tests the base functionality in TestBaseFormat
    """
    def __init__(self, formatName: FormatName, fileSuffix: FileSuffix, description: ExtensionDescription):

        if self.__containsSpecialCharacters(formatName):  # TODO Must be a better way
            raise InvalidPluginNameException(f'{formatName}')

        if DOT in fileSuffix:
            raise InvalidPluginExtensionException(f'{fileSuffix}')

        self._name:        FormatName           = formatName
        self._fileSuffix:  FileSuffix           = fileSuffix
        self._description: ExtensionDescription = description

    @property
    def formatName(self) -> FormatName:
        """
        No special characters allowed

        Returns: The Extension's name
        """
        return self._name

    @property
    def fileSuffix(self) -> FileSuffix:
        """
        Returns: The file name suffix (w/o the leading dot '.')
        """
        return self._fileSuffix

    @property
    def description(self) -> ExtensionDescription:
        """
        Returns: The textual description of the extension data  format
        """
        return self._description

    def __containsSpecialCharacters(self, name: FormatName) -> bool:
        for special in SPECIAL_CHARACTERS:
            if special in name:
                return True
        return False
