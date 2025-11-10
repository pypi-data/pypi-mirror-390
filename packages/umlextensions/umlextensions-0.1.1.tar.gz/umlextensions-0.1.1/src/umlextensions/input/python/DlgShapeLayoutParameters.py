
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from wx import CANCEL
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import ID_CANCEL
from wx import ID_OK
from wx import OK
from wx import DEFAULT_DIALOG_STYLE
from wx import STAY_ON_TOP

from wx import CommandEvent
from wx import Size
from wx import Window
from wx import StdDialogButtonSizer

from wx.lib.sized_controls import SizedDialog
from wx.lib.sized_controls import SizedPanel

from umlextensions.ExtensionsPreferences import ExtensionsPreferences
from umlextensions.input.python.NamedSlider import NamedSlider


@dataclass
class ShapeLayout:
    startX:     int = 0
    startY:     int = 0
    xIncrement: int = 0
    maximumX:   int = 0

class DlgShapeLayoutParameters(SizedDialog):
    def __init__(self, parent: Window = None):

        style: int = STAY_ON_TOP | DEFAULT_DIALOG_STYLE

        super().__init__(parent=parent, title='Layout Parameters', style=style, size=Size(width=300, height=600))

        self.logger: Logger = getLogger(__name__)

        self._extensionPrefs: ExtensionsPreferences = ExtensionsPreferences()

        sizedPanel: SizedPanel = self.GetContentsPane()
        sizedPanel.SetSizerType('vertical')
        sizedPanel.SetSizerProps(expand=True, proportion=1)

        self._startX:     NamedSlider = cast(NamedSlider, None)
        self._startY:     NamedSlider = cast(NamedSlider, None)
        self._xIncrement: NamedSlider = cast(NamedSlider, None)
        self._maximumX:   NamedSlider = cast(NamedSlider, None)

        self._shapeLayout: ShapeLayout = ShapeLayout(
            startX=self._extensionPrefs.startX,
            startY=self._extensionPrefs.startY,
            xIncrement=self._extensionPrefs.xIncrement,
            maximumX=self._extensionPrefs.maximumX
        )
        self._layoutControls(parentPanel=sizedPanel)
        self._layoutStandardOkCancelButtonSizer()

        self._setControlValues()
        # CallAfter(self._resizeDialog)
        # self._resizeDialog()

    @property
    def shapeLayout(self) -> ShapeLayout:
        return self._shapeLayout

    def _layoutControls(self, parentPanel: SizedPanel):
        """
        Args:
            parentPanel:
        """
        self._startX     = NamedSlider(sizedPanel=parentPanel, label='Shape Start X',     minValue=20,   maxValue=500)
        self._startY     = NamedSlider(sizedPanel=parentPanel, label='Shape Start Y',     minValue=20,   maxValue=500)
        self._xIncrement = NamedSlider(sizedPanel=parentPanel, label='Shape X Increment', minValue=20,   maxValue=500)
        self._maximumX   = NamedSlider(sizedPanel=parentPanel, label='Maximum X',         minValue=3000, maxValue=20000)

    def _setControlValues(self):

        self._startX.value     = self._shapeLayout.startX
        self._startY.value     = self._shapeLayout.startY
        self._xIncrement.value = self._shapeLayout.xIncrement
        self._maximumX.value   = self._shapeLayout.maximumX

    def _layoutStandardOkCancelButtonSizer(self):
        """
        Call this last when creating controls;  Will take care of
        adding callbacks for the Ok and Cancel buttons
        """
        buttSizer: StdDialogButtonSizer = self.CreateStdDialogButtonSizer(OK | CANCEL)

        self.SetButtonSizer(buttSizer)
        self.Bind(EVT_BUTTON, self._onOk,    id=ID_OK)
        self.Bind(EVT_BUTTON, self._onClose, id=ID_CANCEL)
        self.Bind(EVT_CLOSE,  self._onClose)

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        Save the values in the component return value and persist them in the preferences
        Args:
            event:
        """

        self._extensionPrefs.startX     = self._startX.value
        self._extensionPrefs.startY     = self._startY.value
        self._extensionPrefs.xIncrement = self._xIncrement.value
        self._extensionPrefs.maximumX   = self._maximumX.value

        self._shapeLayout.startX     = self._startX.value
        self._shapeLayout.startY     = self._startY.value
        self._shapeLayout.xIncrement = self._xIncrement.value
        self._shapeLayout.maximumX   = self._maximumX.value

        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def _onClose(self, event: CommandEvent):
        self.EndModal(CANCEL)

    def _resizeDialog(self):
        """
        A little trick to make sure that you can't resize the dialog to
        less screen space than the controls need
        """
        self.Fit()
        self.SetMinSize(self.GetSize())
