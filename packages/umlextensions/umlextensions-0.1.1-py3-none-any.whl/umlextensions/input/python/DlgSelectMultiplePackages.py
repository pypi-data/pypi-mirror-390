
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import field
from dataclasses import dataclass

from wx import DEFAULT_DIALOG_STYLE
from wx import FD_CHANGE_DIR
from wx import FD_FILE_MUST_EXIST
from wx import FD_MULTIPLE
from wx import FD_OPEN
from wx import FileDialog
from wx import RESIZE_BORDER
from wx import STAY_ON_TOP
from wx import ID_CANCEL
from wx import ID_OK
from wx import OK
from wx import CANCEL

from wx import EVT_BUTTON

from wx import Button
from wx import CommandEvent

from wx.grid import Grid

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from umlextensions.input.InputFormat import InputFormat

ImportModules = NewType('ImportModules', List[str])


def importModulesFactory() -> ImportModules:
    return ImportModules([])


@dataclass
class Package:
    packageName:    str = ''
    importModules:  ImportModules = field(default_factory=importModulesFactory)


ImportPackages = NewType('ImportPackages', List[Package])


class DlgSelectMultiplePackages(SizedDialog):
    """
    TODO:  This might be useful outside of importing Python files.
    """

    def __init__(self, startDirectory: str, inputFormat: InputFormat):

        style: int = RESIZE_BORDER | STAY_ON_TOP | DEFAULT_DIALOG_STYLE
        super().__init__(None, title='Select Multiple Modules', style=style)

        self.logger: Logger = getLogger(__name__)

        self._startDirectory: str         = startDirectory
        self._inputFormat:    InputFormat = inputFormat

        sizedPanel:           SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('vertical')
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._btnMore:    Button = cast(Button, None)
        self._btnCancel:  Button = cast(Button, None)
        self._btnOk:      Button = cast(Button, None)
        self._simpleGrid: Grid   = cast(Grid, None)

        self._layoutSimpleGrid(parent=sizedPanel)
        self._layoutCustomDialogButtonContainer(parent=sizedPanel)

        self._importPackages: ImportPackages = ImportPackages([])
        self._packageCount:   int            = 0
        self._moduleCount:    int            = 0

        self._currentGridRow: int = 0

        self._resizeDialog()

    def _layoutSimpleGrid(self, parent: SizedPanel):

        simpleGrid: Grid = Grid(parent)
        simpleGrid.CreateGrid(numRows=1, numCols=2)

        simpleGrid.SetColLabelValue(0, 'Package Name')
        simpleGrid.SetColLabelValue(1, 'Module Count')

        simpleGrid.AutoSizeColumns()

        self._simpleGrid = simpleGrid

    def _layoutCustomDialogButtonContainer(self, parent: SizedPanel, ):
        """
        Create Ok and Cancel
        Since we want to use a custom button set, we will not use the
        CreateStdDialogBtnSizer here, we'll just create our own panel with
        a horizontal layout and add the buttons to that

        Args:
            parent:
        """
        buttonPanel: SizedPanel = SizedPanel(parent)
        buttonPanel.SetSizerType('horizontal')
        buttonPanel.SetSizerProps(expand=False, halign='right')  # expand False allows aligning right

        #
        # Layout custom buttons here
        #
        self._btnMore   = Button(buttonPanel, label='&More')
        self._btnCancel = Button(buttonPanel, ID_CANCEL, '&Cancel')
        self._btnOk     = Button(buttonPanel, ID_OK, '&Ok')

        self.Bind(EVT_BUTTON, self._onMore,  self._btnMore)
        self.Bind(EVT_BUTTON, self._onOk,    self._btnOk)
        self.Bind(EVT_BUTTON, self._onClose, self._btnCancel)

        self._btnOk.SetDefault()

    @property
    def importPackages(self) -> ImportPackages:
        """
        Only valid if user pressed 'ok'

        Returns: the selected import directories
        """
        return self._importPackages

    @property
    def packageCount(self) -> int:
        return self._packageCount

    @property
    def moduleCount(self) -> int:
        return self._moduleCount

    # noinspection PyUnusedLocal
    def _onMore(self, event: CommandEvent):

        style: int = FD_OPEN | FD_FILE_MUST_EXIST | FD_MULTIPLE | FD_CHANGE_DIR

        with FileDialog(None, "Choose files to import", wildcard=self._composeWildCardSpecification(), defaultDir=self._startDirectory, style=style) as dlg:
            if dlg.ShowModal() == ID_OK:
                importDirectory: Package = Package()

                importDirectory.packageName   = dlg.GetDirectory()
                importDirectory.importModules = ImportModules(dlg.GetFilenames())

                self._packageCount += 1
                currentModuleCount: int = len(importDirectory.importModules)
                self._moduleCount  += currentModuleCount
                self._importPackages.append(importDirectory)
                self._simpleGrid.SetCellValue(self._currentGridRow, 0, importDirectory.packageName)
                self._simpleGrid.SetCellValue(self._currentGridRow, 1, str(currentModuleCount))

                self._simpleGrid.AppendRows(1)
                self._currentGridRow += 1
                self._simpleGrid.AutoSizeColumns()
                self._resizeDialog()
            else:
                self._importPackages = ImportPackages([])

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        """
        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def _onClose(self, event: CommandEvent):
        """
        """
        self.EndModal(CANCEL)

    def _composeWildCardSpecification(self) -> str:

        inputFormat: InputFormat = self._inputFormat

        wildcard: str = (
            f'{inputFormat.formatName} '
            f' (*, {inputFormat.fileSuffix}) '
            f'|*.{inputFormat.fileSuffix}'
        )
        return wildcard

    def _resizeDialog(self):
        """
        A little trick to make sure that you can't resize the dialog to
        less screen space than the controls need
        """
        self.Fit()
        self.SetMinSize(self.GetSize())
