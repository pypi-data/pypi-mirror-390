from typing import List

from umlshapes.frames.UmlFrame import UmlFrame

from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPoint
from umlshapes.shapes.UmlLineControlPoint import UmlLineControlPointType

from umlextensions.tools.sugiyama.LayoutInterfaceLink import LayoutInterfaceLink
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

#
# TODO: Figure out how to get that value here
# This is controlled by a UML Shapes preference
#
SUGIYAMA_CONTROL_POINT_SIZE: int = 4


class SugiyamaLink(LayoutInterfaceLink):
    """
    SugiyamaLink: link of the Sugiyama graph.

    Instantiated by: ../ToSugiyama.py

    :author: Nicolas Dubois
    :contact: nicdub@gmx.ch
    :version: $Revision: 1.4 $
    """
    def __init__(self, umlLink, umlFrame: UmlFrame):
        """

        Args:
            umlLink:
            umlFrame:
        """
        # ALayoutLink.__init__(self, oglObject)
        self._umlFrame: UmlFrame = umlFrame
        super().__init__(umlLink)
        self.__virtualNodes: List[VirtualSugiyamaNode] = []

    def fixControlPoints(self):
        """
        Fix a graphical path with control points.

        @author Nicolas Dubois
        """
        # Clear the actual control points of the link (not the anchor points)
        self.removeAllControlPoints()

        # Current x coordinate of the link
        x = self.getSrcAnchorPos()[0]

        # For all virtual nodes, add control points to pass through
        for virtualNode in self.__virtualNodes:
            #  ~ print "Virtual node"
            (xVNode, yVNode) = virtualNode.getPosition()
            # If link goes to up-left
            if x > xVNode:
                # Find the first real node on the right of the virtual node
                neighbor = virtualNode.getRightNode()
                #
                # Don't like embedded imports, but need to avoid cyclical dependency
                # from pyutplugins.toolplugins.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode
                from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

                while isinstance(neighbor, VirtualSugiyamaNode) and neighbor is not None:

                    # Try next neighbor
                    neighbor = neighbor.getRightNode()

                # If real node found
                if neighbor is not None:
                    # ctrlPoint = ControlPoint(xVNode, neighbor.getPosition()[1] + neighbor.getSize()[1])
                    ctrlPoint = UmlLineControlPoint(umlFrame=self._umlFrame,
                                                    umlLink=self._umlLink,
                                                    controlPointType=UmlLineControlPointType.LINE_POINT,
                                                    size=SUGIYAMA_CONTROL_POINT_SIZE,
                                                    x=xVNode,
                                                    y=neighbor.getPosition()[1] + neighbor.getSize()[1]
                                                    )
                    self.addControlPoint(ctrlPoint)

            else:   # If link goes to up-right
                # Don't like embedded imports, but need to avoid cyclical dependency
                # from pyutplugins.toolplugins.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode
                from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

                # Find the first real node on the left of the virtual node
                neighbor = virtualNode.getLeftNode()
                while isinstance(neighbor, VirtualSugiyamaNode) and neighbor is not None:

                    # Try next neighbor
                    neighbor = neighbor.getLeftNode()

                # If real node found
                if neighbor is not None:
                    # def __init__(self, x: int, y: int, parent=None):

                    # ctrlPoint = ControlPoint(xVNode, neighbor.getPosition()[1] + neighbor.getSize()[1])
                    ctrlPoint = UmlLineControlPoint(umlFrame=self._umlFrame,
                                                    umlLink=self._umlLink,
                                                    controlPointType=UmlLineControlPointType.LINE_POINT,
                                                    size=SUGIYAMA_CONTROL_POINT_SIZE,
                                                    x=xVNode,
                                                    y=neighbor.getPosition()[1] + neighbor.getSize()[1]
                                                    )
                    self.addControlPoint(ctrlPoint)

            ctrlPoint = UmlLineControlPoint(umlFrame=self._umlFrame,
                                            umlLink=self._umlLink,
                                            controlPointType=UmlLineControlPointType.LINE_POINT,
                                            size=SUGIYAMA_CONTROL_POINT_SIZE,
                                            x=xVNode,
                                            y=yVNode
                                            )
            self.addControlPoint(ctrlPoint)

    def addVirtualNode(self, node: VirtualSugiyamaNode):
        """
        Add a virtual node.

        A virtual node is inserted in long links which cross a level. If the
        link crosses more than one level, insert virtual nodes, ordered
        from source to destination (son to father - bottom-up).

        @param VirtualSugiyamaNode node : virtual node
        @author Nicolas Dubois
        """
        self.__virtualNodes.append(node)
