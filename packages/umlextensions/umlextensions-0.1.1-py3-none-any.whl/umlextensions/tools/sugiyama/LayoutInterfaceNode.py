
from typing import Tuple
from typing import cast

from dataclasses import dataclass

from umlshapes.mixins.TopLeftMixin import TopLeftMixin
from umlshapes.types.UmlDimensions import UmlDimensions
from umlshapes.types.UmlPosition import UmlPosition

@dataclass
class LayoutPosition:
    x: int
    y: int


class LayoutInterfaceNode:
    """
    Interface between UML Shapes and Layout algorithms.
    """
    def __init__(self, umlShape):
        """

        Args:
            umlShape: interfaced UML Shape
        """
        self._umlShape = umlShape

    @property
    def name(self) -> str:
        """
        The class name

        Returns: name of the class
        """
        return self._umlShape.pyutClass.name

    @property
    def size(self) -> Tuple[int, int]:
        """
        Return the class size.

        Returns: (int, int): tuple (width, height)
        """
        umlDimensions: UmlDimensions = cast(TopLeftMixin, self._umlShape).size
        return umlDimensions.width, umlDimensions.height

    @property
    def position(self) -> LayoutPosition:
        """
        Get class position.

        Returns: The layout position
        """
        umlPosition: UmlPosition = cast(TopLeftMixin, self._umlShape).position
        return LayoutPosition(x=umlPosition.x, y=umlPosition.y)

    @position.setter
    def position(self, layoutPosition: LayoutPosition):
        """
        Set the class position.

        Args:
            layoutPosition
        """
        umlPosition: UmlPosition = UmlPosition(x=layoutPosition.x, y=layoutPosition.y)
        cast(TopLeftMixin, self._umlShape).position = umlPosition
