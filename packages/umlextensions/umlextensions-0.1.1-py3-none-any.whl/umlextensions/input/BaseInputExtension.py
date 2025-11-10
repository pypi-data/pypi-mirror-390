
from typing import cast

from logging import Logger
from logging import getLogger

from abc import ABC
from abc import abstractmethod

from wx import DirDialog
from wx import ID_CANCEL
from wx import DD_NEW_DIR_BUTTON

from umlextensions.ExtensionsTypes import FrameInformation
from umlextensions.IExtensionsFacade import IExtensionsFacade
from umlextensions.extensiontypes.BaseExtension import BaseExtension
from umlextensions.input.ImportDirectoryResponse import ImportDirectoryResponse

from umlextensions.input.InputFormat import InputFormat

from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionDescription
from umlextensions.extensiontypes.ExtensionDataTypes import FileSuffix
from umlextensions.extensiontypes.ExtensionDataTypes import FormatName

UNSPECIFIED_NAME:        FormatName           = FormatName('Unspecified Plugin Name')
UNSPECIFIED_FILE_SUFFIX: FileSuffix           = FileSuffix('*')
UNSPECIFIED_DESCRIPTION: ExtensionDescription = ExtensionDescription('Unspecified Extension Description')


class BaseInputExtension(BaseExtension, ABC):
    """
    Interface for extensions that can convert foreign structured
    data into UML Diagrams.  Examples include but are not limited to:

        * DTDs
        * Java code
        * Python code

    """
    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade)
        self._bieLogger: Logger = getLogger(__name__)

        self._inputFormat:      InputFormat      = InputFormat(formatName=UNSPECIFIED_NAME, fileSuffix=UNSPECIFIED_FILE_SUFFIX, description=UNSPECIFIED_DESCRIPTION)
        self._frameInformation: FrameInformation = cast(FrameInformation, None)

    @property
    def inputFormat(self) -> InputFormat:
        """
        Implementations set the protected variable at class construction

        Returns: The input format type; Plugins should return `None` if they do
        not support input operations
        """
        return self._inputFormat

    def askForImportDirectoryName(self) -> ImportDirectoryResponse:
        """
        Called by plugin to ask which directory must be imported

        Returns:  The appropriate response object;  The directory name is valid only if
        response.cancelled is True
        """
        # defaultPath: str = self._pluginAdapter.currentDirectory
        defaultPath: str = ''
        dirDialog: DirDialog = DirDialog(None,
                                         "Choose a directory to import",
                                         defaultPath=defaultPath,
                                         style=DD_NEW_DIR_BUTTON)

        response: ImportDirectoryResponse = ImportDirectoryResponse()
        if dirDialog.ShowModal() == ID_CANCEL:
            response.cancelled     = True
            response.directoryName = ''
        else:
            response.directoryName = dirDialog.GetPath()
            response.cancelled     = False
            # self._pluginAdapter.currentDirectory = response.directoryName    # TODO: Should plugin be doing this?  No

        dirDialog.Destroy()

        return response

    def executeImport(self):
        """
        Called by the extension manager to begin the import process.
        """
        # noinspection PyTypeChecker
        self._extensionsFacade.requestCurrentFrameInformation(callback=self._executeImport)   # type ignore

    def _executeImport(self, frameInformation: FrameInformation):
        """
        The callback necessary to start the import process;
        Args:
            frameInformation:
        """
        assert self.inputFormat is not None, 'Developer error. We cannot import w/o an import format'

        self._frameInformation = frameInformation

        if self._requireActiveFrame is True:
            if frameInformation.frameActive is False:
                self.showNoUmlFrameDialog()
                return
        if self.setImportOptions() is True:
            self.read()

    @abstractmethod
    def setImportOptions(self) -> bool:
        """
        Prepare for the import.
        Use this method to query the end-user for any additional import options

        Returns:
            if False, the import is cancelled
        """
        pass

    @abstractmethod
    def read(self) -> bool:
        """
        Read data from a file;  Presumably, the file was specified on the call
        to setImportOptions
        """
        pass

    def _composeWildCardSpecification(self) -> str:

        inputFormat: InputFormat = self.inputFormat

        # wildcard: str = inputFormat.name + " (*." + inputFormat.extension + ")|*." + inputFormat.description
        wildcard: str = (
            f'{inputFormat.formatName} '
            f' (*, {inputFormat.fileSuffix}) '
            f'|*.{inputFormat.fileSuffix}'
        )
        return wildcard
