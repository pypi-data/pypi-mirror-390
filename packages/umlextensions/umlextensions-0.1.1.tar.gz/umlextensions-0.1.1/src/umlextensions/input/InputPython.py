
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from wx import OK
from wx import ICON_ERROR
from wx import PD_APP_MODAL
from wx import PD_ELAPSED_TIME

from wx import BeginBusyCursor
from wx import EndBusyCursor
from wx import ProgressDialog
from wx import MessageBox
from wx import MessageDialog

from wx import Yield as wxYield

from umlshapes.ShapeTypes import UmlLinks

from umlshapes.shapes.UmlClass import UmlClass

from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition

from umlshapes.frames.ClassDiagramFrame import ClassDiagramFrame

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.extensiontypes.ExtensionDataTypes import Author
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionDescription
from umlextensions.extensiontypes.ExtensionDataTypes import ExtensionName
from umlextensions.extensiontypes.ExtensionDataTypes import FileSuffix
from umlextensions.extensiontypes.ExtensionDataTypes import FormatName
from umlextensions.extensiontypes.ExtensionDataTypes import Version

from umlextensions.input.InputFormat import InputFormat

from umlextensions.input.BaseInputExtension import BaseInputExtension

from umlextensions.input.python.DlgSelectMultiplePackages import DlgSelectMultiplePackages
from umlextensions.input.python.DlgSelectMultiplePackages import ImportPackages
from umlextensions.input.python.DlgSelectMultiplePackages import Package
from umlextensions.input.python.DlgShapeLayoutParameters import DlgShapeLayoutParameters
from umlextensions.input.python.DlgShapeLayoutParameters import ShapeLayout

from umlextensions.input.python.PythonParseException import PythonParseException
from umlextensions.input.python.PythonToUmlShapes import PythonToUmlShapes
from umlextensions.input.python.PythonToUmlShapes import UmlClassesDict

from umlextensions.input.python.visitor.ParserTypes import PyutClasses

FORMAT_NAME:           FormatName           = FormatName("Python File(s)")
FILE_SUFFIX:           FileSuffix           = FileSuffix('py')
EXTENSION_DESCRIPTION: ExtensionDescription = ExtensionDescription('Python code reverse engineering')

class InputPython(BaseInputExtension):

    def __init__(self, extensionsFacade: IExtensionsFacade):

        super().__init__(extensionsFacade)
        self.logger: Logger = getLogger(__name__)

        self._name    = ExtensionName('Python to UML')
        self._author  = Author('Humberto A. Sanchez II')
        self._version = Version('3.0')

        self._inputFormat  = InputFormat(formatName=FORMAT_NAME, fileSuffix=FILE_SUFFIX, description=EXTENSION_DESCRIPTION)

        self._packageCount:   int = 0
        self._moduleCount:    int = 0
        self._importPackages: ImportPackages = ImportPackages([])

        self._readProgressDlg: ProgressDialog = cast(ProgressDialog, None)

    def setImportOptions(self) -> bool:
        """
        We do need to ask for the input file names

        TODO:  super complicated if else logic

        Returns:  'True', we support import
        """
        if isinstance(self._frameInformation.umlFrame, ClassDiagramFrame) is True:
            startDirectory: str = self._preferences.startDirectory
            with DlgSelectMultiplePackages(startDirectory=startDirectory, inputFormat=self.inputFormat) as dlg:
                if dlg.ShowModal() == OK:
                    self._packageCount   = dlg.packageCount
                    self._moduleCount    = dlg.moduleCount
                    self._importPackages = dlg.importPackages
                    #
                    # Ensure we picked at least 1
                    if self._packageCount == 0:
                        return False
                    else:
                        return True
                else:
                    return False
        else:
            booBoo: MessageDialog = MessageDialog(parent=None,
                                                  message='The import to frame must be a class diagram frame',
                                                  caption='Error!',
                                                  style=OK | ICON_ERROR
                                                  )
            booBoo.ShowModal()
            return False

    def read(self) -> bool:

        BeginBusyCursor()
        wxYield()
        status: bool = True
        try:
            self._readProgressDlg = ProgressDialog('Parsing Files', 'Starting', parent=None, style=PD_APP_MODAL | PD_ELAPSED_TIME)

            # reverseEngineer: ReverseEngineerPythonV3 = ReverseEngineerPythonV3()
            # Should the extensions know about the UML pub/sub Engine ???
            #
            self._readProgressDlg.SetRange(self._moduleCount)

            classDiagramFrame: ClassDiagramFrame = cast(ClassDiagramFrame, self._frameInformation.umlFrame)
            pythonToUmlShapes: PythonToUmlShapes = PythonToUmlShapes(classDiagramFrame=classDiagramFrame, umlPubSubEngine=self._extensionsFacade.umlPubSubEngine)

            pyutClasses: PyutClasses = self._collectPyutClassesInPass1(pythonToUmlShapes=pythonToUmlShapes)
            pyutClasses              = self._enhancePyutClassesInPass2(pythonToUmlShapes=pythonToUmlShapes, pyutClasses=pyutClasses)

            umlClassesDict: UmlClassesDict = pythonToUmlShapes.generateUmlClasses(pyutClasses)
            pythonToUmlShapes.generateLinks(umlClassesDict)

            self._readProgressDlg.Destroy()
            self._layoutUmlClasses(umlClasses=list(umlClassesDict.values()))
            self._layoutLinks(oglLinks=pythonToUmlShapes.umlLinks)

        except (ValueError, Exception, PythonParseException) as e:
            self._readProgressDlg.Destroy()
            MessageBox(f'{e}', 'Error', OK | ICON_ERROR)
            status = False
        else:
            self._extensionsFacade.extensionModifiedProject()
        finally:
            EndBusyCursor()
            self._extensionsFacade.refreshFrame()
            wxYield()

        self._extensionsFacade.wiggleShapes()

        return status

    def _collectPyutClassesInPass1(self, pythonToUmlShapes: PythonToUmlShapes) -> PyutClasses:

        cumulativePyutClasses: PyutClasses = PyutClasses({})
        for directory in self._importPackages:
            importPackage: Package = cast(Package, directory)

            currentPyutClasses: PyutClasses = pythonToUmlShapes.pass1(directoryName=importPackage.packageName,
                                                                      files=importPackage.importModules,
                                                                      progressCallback=self._readProgressCallback)

            cumulativePyutClasses = PyutClasses(cumulativePyutClasses | currentPyutClasses)

        return cumulativePyutClasses

    def _enhancePyutClassesInPass2(self, pythonToUmlShapes: PythonToUmlShapes, pyutClasses: PyutClasses) -> PyutClasses:

        updatedPyutClasses: PyutClasses = PyutClasses({})
        for directory in self._importPackages:
            importPackage: Package = cast(Package, directory)

            updatedPyutClasses = pythonToUmlShapes.pass2(directoryName=importPackage.packageName,
                                                         files=importPackage.importModules,
                                                         pyutClasses=pyutClasses,
                                                         progressCallback=self._readProgressCallback)

        return updatedPyutClasses

    def _readProgressCallback(self, currentFileCount: int, msg: str):
        """

        Args:
            currentFileCount:   The current file # we are working pm
            msg:    An updated message
        """

        self._readProgressDlg.Update(currentFileCount, msg)

    def _layoutUmlClasses(self, umlClasses: List[UmlClass]):
        """
        Organize by vertical descending sizes

        Args:
            umlClasses
        """
        # Sort by descending height
        # noinspection PyProtectedMember
        sortedUmlClasses = sorted(umlClasses, key=lambda umlClassToSort: umlClassToSort.GetHeight(), reverse=True)

        with DlgShapeLayoutParameters() as dlg:
            if dlg.ShowModal() == OK:
                self.logger.info('Ok')

            # x: int = 20     # startX
            # y: int = 20     # startY
            shapeLayout: ShapeLayout = dlg.shapeLayout
            x: int = shapeLayout.startX
            y: int = shapeLayout.startY

            incY: int = 0
            for umlClass in sortedUmlClasses:
                #  incX, sy = oglClass.GetSize()
                size: UmlDimensions = umlClass.size
                incX = size.width
                sy   = size.height
                incX += shapeLayout.xIncrement         # xIncrement
                sy += 20
                incY = max(incY, int(sy))              # find good coordinates
                if x + incX >= shapeLayout.maximumX:   # maximumX
                    x = 20
                    y += incY
                    incY = int(sy)

                # oglClass.SetPosition(x, y)
                umlClass.position = UmlPosition(x=x, y=y)
                x += incX
                # self._pluginAdapter.addShape(shape=oglClass)
                self._extensionsFacade.addShape(umlShape=umlClass)

    def _layoutLinks(self, oglLinks: UmlLinks):
        for oglLink in oglLinks:
            self._extensionsFacade.addShape(oglLink)
