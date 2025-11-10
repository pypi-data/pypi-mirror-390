
from typing import List
from typing import Tuple
from typing import cast

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.links.UmlLink import UmlLink

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint

from umlextensions.tools.sugiyama.RealSugiyamaNode import RealSugiyamaNode
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

SyntheticNode = RealSugiyamaNode | VirtualSugiyamaNode


class LayoutInterfaceLink:
    """
    Interface between Uml Links and Layout algorithms.

    Layout algorithms use this interface to access the links on the
    diagram.

    * The interface protects the structure of the diagram.
    * The diagram structure and diagram m methods can be changed.

    Thus, we only need to update is this interface, not the automatic layout algorithm.

    Note:
        This happened in 2025, when Humberto did away with the miniogl home grown code and
        instead used wxPython's wx.lib.ogl code
    """
    def __init__(self, umlLink: UmlLink):
        """

        Args:
            umlLink:
        """
        self._umlLink: UmlLink = umlLink
        self._srcNode: SyntheticNode = cast(SyntheticNode, None)
        self._dstNode: SyntheticNode = cast(SyntheticNode, None)

    @property
    def linkType(self) -> PyutLinkType:
        """
        Return the link type

        Returns: Link type
        """
        return self._umlLink.pyutLink.linkType

    @property
    def source(self) -> SyntheticNode:
        """

        Returns:  the source node.
        """
        return self._srcNode

    @source.setter
    def source(self, node: SyntheticNode):
        """
        Set the source node.

        Args:
            node:  The link source node
        """
        self._srcNode = node

    @property
    def destination(self) -> SyntheticNode:
        """

        Returns: The destination node
        """
        return self._dstNode

    @destination.setter
    def destination(self, node: SyntheticNode):
        """
        Set the destination node.

        Args:
            node: The new link destination
        """
        self._dstNode = node

    def setSrcAnchorPos(self, x: int, y: int):
        """
        Set anchor position (absolute coordinates) on source class.

        Args:
            x:
            y:
        """
        umLink: UmlLink = self._umlLink
        x1, y1, x2, y2 = umLink.GetEnds()

        umLink.SetEnds(x1=x, y1=y, x2=x2, y2=y2)
        # self._umlLink.sourceAnchor.SetPosition(x, y)

    def setDestAnchorPos(self, x: int, y: int):
        """
        Set anchor position (absolute coordinates) on destination class.

        Args:
            x:
            y:
        """
        umLink: UmlLink = self._umlLink
        x1, y1, x2, y2 = umLink.GetEnds()

        umLink.SetEnds(x1=x1, y1=y1, x2=x, y2=y)

        # self._umlLink.destinationAnchor.SetPosition(x, y)

    def getSrcAnchorPos(self):
        """
        Get anchor position (absolute coordinates) on source class.

        Returns:    (int, int) : tuple with (x, y) coordinates
        """
        umLink: UmlLink = self._umlLink
        x1, y1, x2, y2 = umLink.GetEnds()

        return x1, y1
        # return self._umlLink.sourceAnchor.GetPosition()

    def getDestAnchorPos(self):
        """
        Return anchor position (absolute coordinates) on destination class.

        Returns:  (int, int) : tuple with (x, y) coordinates
        """
        umLink: UmlLink = self._umlLink
        x1, y1, x2, y2 = umLink.GetEnds()

        return x2, y2

    # noinspection PyUnusedLocal
    def addControlPoint(self, control: UmlLineControlPoint, last=None):
        """
        Add a control point. If the parameter last present, add a point right after last.
        TODO: the 'last' parameter is used by no one

        Args:
            control:  control point to add
            last:     add control right after last
        """
        # self._oglLink.AddControl(control, last)
        pt: Tuple[int, int] = control.position.x, control.position.y
        self._umlLink.InsertLineControlPoint(point=pt)

    def removeControlPoint(self, controlPoint):
        """
        Remove a control point.

        TODO:  This is not used by the Sugiyama algorithm

        Args:
            controlPoint: control point to remove
        """
        umlLink: UmlLink = self._umlLink

        controlPoints: List[UmlLineControlPoint] = umlLink.GetLineControlPoints()
        controlPoints.remove(controlPoint)

        # self._umlLink.Remove(controlPoint)

    def removeAllControlPoints(self):
        """
        Remove all control points.
        """
        # self._umlLink.ResetControlPoints()
        self._umlLink.DeleteControlPoints()
        # self._umlLink.RemoveAllControlPoints()
