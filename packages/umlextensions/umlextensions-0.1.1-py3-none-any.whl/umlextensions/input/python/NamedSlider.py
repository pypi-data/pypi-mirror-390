
from logging import Logger
from logging import getLogger

from wx import ID_ANY
from wx import SL_AUTOTICKS
from wx import SL_HORIZONTAL
from wx import SL_LABELS
from wx import VERTICAL

from wx import Panel
from wx import Size
from wx import SizerFlags
from wx import Slider
from wx import BoxSizer

from wx.lib.sized_controls import SizedPanel
from wx.lib.sized_controls import SizedStaticBox

SLIDER_HEIGHT: int = 100
SLIDER_WIDTH:  int = 300


class NamedSlider(Slider):

    def __init__(self, sizedPanel: SizedPanel, label: str, minValue: int, maxValue: int):
        """
        The reason with have a work around panel
        https://discuss.wxpython.org/t/wxpython-slider-incorrectly-displays-with-sized-panels/36915/10

        Args:
            sizedPanel:
            label:
            minValue:
            maxValue:
        """
        self.logger: Logger = getLogger(__name__)

        namingPanel: SizedStaticBox = SizedStaticBox(sizedPanel, label=label)
        namingPanel.SetSizerType('horizontal')
        namingPanel.SetSizerProps(expand=True, proportion=1)

        workAroundPanel: Panel    = Panel(namingPanel)
        workAroundSizer: BoxSizer = BoxSizer(VERTICAL)
        workAroundPanel.SetSizer(workAroundSizer)

        super().__init__(
            parent=workAroundPanel, id=ID_ANY,
            minValue=minValue, maxValue=maxValue,
            size=Size(width=SLIDER_WIDTH, height=SLIDER_HEIGHT),
            style=SL_HORIZONTAL | SL_AUTOTICKS | SL_LABELS
        )
        flagsExpand: SizerFlags = SizerFlags().Expand().Proportion(1)
        workAroundSizer.Add(window=self, flags=flagsExpand)

    @property
    def value(self) -> int:
        return self.GetValue()

    @value.setter
    def value(self, value: int):
        self.SetValue(value)
