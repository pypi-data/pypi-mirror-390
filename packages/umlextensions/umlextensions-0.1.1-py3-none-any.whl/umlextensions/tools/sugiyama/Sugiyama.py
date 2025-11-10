
from typing import List
from typing import NewType
from typing import Union
from typing import cast

from logging import Logger
from logging import getLogger

from copy import copy

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from umlshapes.ShapeTypes import UmlLinkGenre
from umlshapes.frames.UmlFrame import UmlFrame
from umlshapes.shapes.UmlNote import UmlNote
from umlshapes.shapes.UmlClass import UmlClass
from umlshapes.links.UmlInterface import UmlInterface
from umlshapes.links.UmlInheritance import UmlInheritance

from umlextensions.ExtensionsPreferences import ExtensionsPreferences

from umlextensions.IExtensionsFacade import IExtensionsFacade

from umlextensions.tools.sugiyama.SugiyamaLink import SugiyamaLink
from umlextensions.tools.sugiyama.SugiyamaNode import SugiyamaNode
from umlextensions.tools.sugiyama.SugiyamaConstants import H_SPACE
from umlextensions.tools.sugiyama.SugiyamaConstants import LEFT_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import UP_MARGIN
from umlextensions.tools.sugiyama.SugiyamaConstants import V_SPACE
from umlextensions.tools.sugiyama.SugiyamaGlobals import SugiyamaGlobals
from umlextensions.tools.sugiyama.RealSugiyamaNode import RealSugiyamaNode
from umlextensions.tools.sugiyama.VirtualSugiyamaNode import VirtualSugiyamaNode

Nodes    = Union[RealSugiyamaNode, VirtualSugiyamaNode]
NodeList = NewType('NodeList', List[Nodes])
Levels   = NewType('Levels', List[NodeList])

HierarchicalGraphNode  = Union[RealSugiyamaNode, VirtualSugiyamaNode]
HierarchicalGraphNodes = NewType('HierarchicalGraphNodes', List[HierarchicalGraphNode])


class Sugiyama:
    """
    Automatic layout algorithm based on Sugiyama levels.

    This algorithm will change the class and links positions (not the
    structure). This plugin gives good result with diagrams that contain
    a lot of hierarchical relations (inheritance and interface), and poor
    association relations.

    """

    def __init__(self, umlFrame: UmlFrame, extensionsFacade: IExtensionsFacade):

        self.logger: Logger = getLogger(__name__)

        self._extensionsFacade: IExtensionsFacade     = extensionsFacade
        self._umlFrame:         UmlFrame              = umlFrame
        self._preferences:      ExtensionsPreferences = ExtensionsPreferences()

        # Sugiyama nodes and links
        self.__realSugiyamaNodesList: List[RealSugiyamaNode] = []   # List of all RealSugiyamaNode's
        self._sugiyamaLinksList:      List[SugiyamaLink]     = []   # List of all SugiyamaLink's

        #  Hierarchy graph
        #  List of Real and Virtual Sugiyama nodes that take part in hierarchy
        # self._hierarchyGraphNodesList:    List[Union[RealSugiyamaNode, VirtualSugiyamaNode]] = []
        self._hierarchyGraphNodesList: HierarchicalGraphNodes = HierarchicalGraphNodes([])
        #  List of Sugiyama nodes that are not in a hierarchy
        self._nonHierarchyGraphNodesList: List[VirtualSugiyamaNode] = []
        self._nonHierarchyGraphLinksList: List[SugiyamaLink]        = []

        #  All nodes of the hierarchy are assigned to a level.
        #  A level is a list of nodes (real or virtual).
        # nodeList: NodeList = NodeList([])
        self._levels: Levels = Levels([])   # List of levels

    @property
    def levels(self) -> Levels:
        """
        For testability and security you only get a copy

        Returns:  Internal levels structure
        """
        levels: Levels = copy(self._levels)
        return levels

    def createInterfaceOglALayout(self, umlShapes):
        """
        Create the interface between oglObjects and Automatic Layout
        structure. A RealSugiyamaNode is created for each class, and a
        SugiyamaLink is created for each relation in the UML diagram.

        Args:
            umlShapes:  The UML Shapes on the diagram
        """
        # Dictionary for oglObjects fast research
        # Key = OglObject, Value = RealSugiyamaNode
        dictOgl     = {}                # type: ignore
        # Dictionary for RealSugiyamaNode that takes part in hierarchy
        # Key = OglObject, Value = None
        dictSugiyamaHierarchy = {}      # type: ignore

        def createSugiyamaNode(theOglObject, theDictOgl):
            """
            Internal function for creating a RealSugiyamaNode and add it to
            self.__realSugiyamaNodesList and to dictOgl
            Args:
                theOglObject:
                theDictOgl:
            """
            # Create RealSugiyamaNode only if not already done
            if theOglObject not in theDictOgl:
                node = RealSugiyamaNode(theOglObject)
                self.__realSugiyamaNodesList.append(node)
                theDictOgl[theOglObject] = node

        def addNode2HierarchyGraph(theSugiyamaNode, theDictSugiyamaHierarchy):
            """
            Internal function for adding nodes that take part in hierarchy in
            the __hierarchyGraphNodesList.

            Args:
                theSugiyamaNode:
                theDictSugiyamaHierarchy:
            """
            if theSugiyamaNode not in theDictSugiyamaHierarchy:
                theDictSugiyamaHierarchy[theSugiyamaNode] = None
                self._hierarchyGraphNodesList.append(theSugiyamaNode)

        # For each OglObject or OglLink, create a specific interface
        for oglObject in umlShapes:

            # Class or Note :
            if isinstance(oglObject, UmlClass) or isinstance(oglObject, UmlNote):
                createSugiyamaNode(oglObject, dictOgl)
            # Links
            elif isinstance(oglObject, UmlLinkGenre):

                # Get source and destination oglObject
                srcOglClass = oglObject.sourceShape
                dstOglClass = oglObject.destinationShape

                # If the classes have not a RealSugiyamaNode attributed yet
                createSugiyamaNode(srcOglClass, dictOgl)
                createSugiyamaNode(dstOglClass, dictOgl)

                # Fix relations between nodes
                link = SugiyamaLink(umlLink=oglObject, umlFrame=self._umlFrame)
                self._sugiyamaLinksList.append(link)
                srcSugiyamaNode = dictOgl[srcOglClass]
                dstSugiyamaNode = dictOgl[dstOglClass]

                link.source      = srcSugiyamaNode
                link.destination = dstSugiyamaNode

                # If hierarchical link
                if isinstance(oglObject, UmlInheritance) or isinstance(oglObject, UmlInterface):

                    srcSugiyamaNode.addParent(dstSugiyamaNode, link)
                    dstSugiyamaNode.addChild(srcSugiyamaNode, link)

                    # Add nodes in list of hierarchical nodes
                    addNode2HierarchyGraph(srcSugiyamaNode, dictSugiyamaHierarchy)
                    addNode2HierarchyGraph(dstSugiyamaNode, dictSugiyamaHierarchy)

                # Non-hierarchical links
                else:

                    # Add link between source and destination interface
                    srcSugiyamaNode.addNonHierarchicalLink(dstSugiyamaNode, link)
                    dstSugiyamaNode.addNonHierarchicalLink(srcSugiyamaNode, link)

                    # Add link into non-hierarchical links' list
                    self._nonHierarchyGraphLinksList.append(link)

        # Create list of non-hierarchical nodes

        # For each class or note
        for sugiyamaNode in list(dictOgl.values()):
            # If not in hierarchy
            if sugiyamaNode not in dictSugiyamaHierarchy:
                self._nonHierarchyGraphNodesList.append(sugiyamaNode)

    def levelFind(self) -> bool:
        """
        Compute the best hierarchical level for each node.

        Returns: `True` if we computed the best, else `False` if there is a
        cycle in hierarchical links
        """
        nodesList: HierarchicalGraphNodes = self._hierarchyGraphNodesList
        # Fix nodes indexes corresponding to matrix column and line index
        nbNodes = len(nodesList)  # Number of nodes in hierarchy
        for i in range(nbNodes):
            nodesList[i].setIndex(i)
        # Initialize the boolean matrix
        #
        # Example of use:
        #
        #      |A|B|C
        #     -+-+-+-
        #     A|0|0|1 <-- that 1 means A is C's father
        #     -+-+-+-     and is on coordinates matrix[2][0]
        #     B|0|0|0
        #     -+-+-+-     matrix[column][line]
        #     C|0|1|0
        #
        #
        # noinspection PyUnusedLocal
        matrix = [[0 for el in range(nbNodes)] for el2 in range(nbNodes)]
        # Fill matrix
        # For each node in graph
        for node in nodesList:
            # For each father
            for (father, link) in node.getParents():
                # Mark relation with a '1' on coordinates[index Son][index Father]
                matrix[node.getIndex()][father.getIndex()] = 1      # type: ignore
        # Define levels

        # Sum each column of the matrix
        # Old code would not pass mypy or pycharm_projects
        # sumColumns = [None for el in range(nbNodes)]
        # el not used
        # noinspection PyUnusedLocal
        sumColumns: List[int] = [0 for el in range(nbNodes)]
        for i in range(nbNodes):
            sumColumns[i] = 0
            for el in matrix[i]:
                sumColumns[i] += el

        # Index of nodes that are not in any level yet
        indexNodes = list(range(nbNodes))
        # While not all nodes have an attributed level
        # while indexNodes != []:
        while indexNodes:
            # level = []  # Current level
            level: NodeList = NodeList([])
            indexNodesNotSel = indexNodes[:]
            indexNodesSel = []

            # For all nodes that haven't an attributed level
            for i in indexNodes:
                # When the sum of his matrix column is 0, that means he has no
                # parent or his parents are already in a level
                if sumColumns[i] == 0:
                    # The node is attributed on the current level
                    # Update the lists of selected nodes
                    indexNodesSel.append(i)
                    indexNodesNotSel.remove(i)
            # If no nodes is selected, there is a cycle in hierarchical links
            # if indexNodesSel == []:
            if not indexNodesSel:
                return False

            # For all the current level's nodes
            for i in indexNodesSel:
                level.append(nodesList[i])
                # Update the sum of the columns when we remove the line of the
                # node in the matrix
                for j in indexNodesNotSel:
                    sumColumns[j] -= matrix[j][i]
            # Update the list of the nodes that haven't a level yet
            indexNodes = indexNodesNotSel[:]
            # Add the current level to the list
            self._levels.append(level)

        # Fix nodes index and level for each node
        for idx in range(len(self._levels)):
            level = self._levels[idx]
            for i in range(len(level)):
                node = level[i]
                node.setIndex(i)
                node.setLevel(idx)

        # No error
        return True

    def addVirtualNodes(self):
        """
        Add a virtual node by level crossed between fathers and sons that are
        separated by more than one level.
        """
        # Internal function for updating a sons or fathers list
        def updateLink(nodesList, zLink, newNode):
            """
            Find the tuple (node, link2) in nodesList where link == link2 and
            replace node by newNode.
            """
            for i in range(len(nodesList)):
                (node, link2) = nodesList[i]
                if zLink == link2:
                    nodesList[i] = (newNode, zLink)
                    break

        # Add virtual nodes between a father and one of his sons
        def addVirtualNodesOnHierarchicalLink(zLink):

            srcNode = zLink.source
            dstNode = zLink.destination
            dstNodeLevel = dstNode.getLevel()

            # List of level index between dstNode and srcNode
            indexLevels = list(range(dstNodeLevel + 1, srcNode.getLevel()))

            # Continue only if there is at least one level between the two
            # nodes
            if len(indexLevels) == 0:
                return
            # noinspection PyUnusedLocal
            # For each crossed level, add a virtual node
            virtualNodes = [VirtualSugiyamaNode() for el in indexLevels]

            # Fix level
            for i in range(len(virtualNodes)):
                virtualNode: VirtualSugiyamaNode = virtualNodes[i]
                virtualNode.setLevel(dstNodeLevel + i + 1)

            # Fix relation between virtual nodes
            for i in range(len(virtualNodes) - 1):
                virtualNodes[i].addChild(virtualNodes[i + 1], zLink)
                virtualNodes[i + 1].addParent(virtualNodes[i], zLink)

            # Fix relations between virtual and real nodes
            virtualNodes[-1].addChild(srcNode, zLink)
            virtualNodes[0].addParent(dstNode, zLink)

            updateLink(dstNode.getChildren(), zLink, virtualNodes[0])
            updateLink(srcNode.getParents(), zLink, virtualNodes[-1])

            # Add virtual nodes in levels
            for i in range(len(virtualNodes)):
                level = self._levels[dstNodeLevel + i + 1]
                level.append(virtualNodes[i])
                # Fix index of the virtual node
                level[-1].setIndex(len(level) - 1)

            # Add virtual nodes in link in order bottom to top
            for i in range(len(virtualNodes) - 1, -1, -1):
                zLink.addVirtualNode(virtualNodes[i])

        # For all links
        for link in self._sugiyamaLinksList:
            # If hierarchical link
            if link.linkType == PyutLinkType.INHERITANCE or link.linkType == PyutLinkType.INTERFACE:

                # Add virtual nodes
                addVirtualNodesOnHierarchicalLink(link)

    def barycenter(self):
        """
        Find nodes index for minimizing hierarchical links crossing.
        """
        MAX_ITER = 20

        while self._getNbIntersectAll() > 0 and MAX_ITER > 0:

            # Downward phase

            # For each level except first
            for i in range(1, len(self._levels)):

                # Compute parents down-barycenter
                if i > 0:
                    self._downBarycenterLevel(i - 1)
                # Compute sons up-barycenter
                if i < len(self._levels) - 1:
                    self._upBarycenterLevel(i + 1)

                # Compute up-barycenter on current level
                self._upBarycenterLevel(i)
                self._sortLevel(i)
                self._shiftSameBarycenter(i)

            # Upward phase

            if self._getNbIntersectAll() > 0:

                indexList = list(range(len(self._levels) - 1))
                indexList.reverse()
                for i in indexList:

                    self._downBarycenterLevel(i)
                    self._sortLevel(i)
                    self._shiftSameBarycenter(i)

                MAX_ITER -= 1

    def addNonHierarchicalNodes(self):
        """
        Add non-hierarchical nodes into levels.
        """
        # Vocabulary:
        # Internal node: nodes present in levels
        # External node: nodes not present in levels yet

        # Dictionary internalNodes externalNodes:
        # Keys are internal respectively external nodes
        # Values :
        #   - externalNodes : # of zLink to internal nodes
        internalNodes = {}  # type: ignore
        externalNodes = {}

        # Make dictionary of internal nodes
        for node in self._hierarchyGraphNodesList:
            internalNodes[node] = None

        # Make dictionary of external nodes
        for node in self._nonHierarchyGraphNodesList:
            # Count zLink to internal nodes
            count = 0
            for (dstNode, link) in node.getNonHierarchicalLink():
                if dstNode in internalNodes:
                    count += 1

            # Add node to externalNodes
            externalNodes[node] = count

        # If there is no level (no inheritance or realisation) but there are
        # nodes to put in, create new level
        if not self._levels and externalNodes:
            # Add one level for nodes
            self._levels.append(NodeList([]))

        # Function for getting node that has most connections to internal
        # nodes
        def mostConnection(zExternalNodes):

            maxNode    = None
            maxNbLinks = -1
            for (nbLinkNode, nbLinks) in list(zExternalNodes.items()):
                # If current node has more connections
                if nbLinks > maxNbLinks:
                    maxNode    = nbLinkNode
                    maxNbLinks = nbLinks

            return maxNode
        # Function for evaluating best level and best index for an external
        # node

        def bestPos(zExtNode, zInternalNodes):
            """
            Evaluate average of level of linked nodes
            Args:
                zExtNode:
                zInternalNodes:

            Returns: (level, index)
            """
            nb:        int = 0
            summation: int = 0
            nodes     = []  # List of connected internal nodes

            # For all non-hierarchical links
            for (zDstNode, zLink) in zExtNode.getNonHierarchicalLink():
                # If node linked to internal nodes
                if zDstNode in zInternalNodes:
                    # Add connected node to list
                    nodes.append(zDstNode)
                    # Add level to sum and count number of zLink
                    summation += zDstNode.getLevel()
                    nb += 1
            # If no zLink to internal nodes
            # if nodes == []:
            if not nodes:
                return None, None

            # Find closer node to average position
            avgLevel = summation // nb
            levelNodes = []  # List of nodes on same level
            bestLevel = None
            # Fix best level on first node
            if nodes:
                bestLevel = nodes[0].getLevel()

            # For all connected internal nodes
            for connectedInternalNode in nodes:
                nodeLevel = connectedInternalNode.getLevel()

                # If current node is on bestLevel
                if nodeLevel == bestLevel:
                    levelNodes.append(connectedInternalNode)

                # Else if current node is nearer to average position or
                # is at same distance but with less nodes on level
                # TODO Refactor this test to a method
                elif abs(nodeLevel - avgLevel) < abs(bestLevel - avgLevel) or (abs(nodeLevel - avgLevel) == abs(bestLevel - avgLevel) and       # type: ignore
                                                                               len(self._levels[nodeLevel]) < len(self._levels[bestLevel])):    # type: ignore

                    # Store best level
                    bestLevel = nodeLevel

                    # Start new list of nodes on new best level
                    levelNodes = [connectedInternalNode]

            # Return average of nodes' level
            return bestLevel, levelNodes[len(levelNodes) // 2].getIndex()

        # Function for getting level that has fewer nodes.
        def getLessFilledLevel():

            lessLevel = 0  # Index of level that has less node in it
            nb = len(self._levels[lessLevel])

            for x in range(1, len(self._levels)):
                if len(self._levels[x]) < nb:
                    lessLevel = x
                    nb = len(self._levels[x])

            return lessLevel

        # Function to move a node from internal to external nodes.
        def moveExternal2Internal(zNode, zInternalNodes, zExternalNodes):

            # Remove node from external nodes
            del zExternalNodes[zNode]

            # Add node to internal nodes
            zInternalNodes[zNode] = None

            # For all his linked external nodes, update their counter
            # zExtNode = None   NOT USED
            for (zDstNode, zLink) in zNode.getNonHierarchicalLink():
                if zDstNode in zExternalNodes:
                    zExternalNodes[zDstNode] += 1

        # While there are nodes still not in hierarchy
        while externalNodes:
            # Get external node that has most connections to internalNodes
            extNode = mostConnection(externalNodes)

            self.logger.info(f'extNode.getName(): `{extNode.getName()}`')
            # Evaluate best level and index for the node
            (level, index) = bestPos(extNode, internalNodes)

            # If node has no connection to internal node
            if level is None:
                # Find level that is less filled of nodes
                level = getLessFilledLevel()
                index = len(self._levels[level])

            # Add node in levels
            extNode.setLevel(level)
            extNode.setIndex(index)
            self._levels[level].insert(index, extNode)
            # Shift index attributes on right
            for i in range(index + 1, len(self._levels[level])):
                self._levels[level][i].setIndex(i)

            # Move node from external to internal nodes
            moveExternal2Internal(extNode, internalNodes, externalNodes)

    def fixPositions(self):
        """
        Compute coordinates for nodes and links.
        """
        self._fixNodesNeighbors()
        self._fixNodesPositions()
        self._fixLinksPositions()

    def _downBarycenterLevel(self, indexLevel):
        """
        Compute down barycenter (from sons) for all nodes on level.

        Args:
            indexLevel:   The index level
        """
        level = self._levels[indexLevel]
        for node in level:
            node.downBarycenterIndex()

    def _upBarycenterLevel(self, indexLevel):
        """
        Compute up barycenter (from parents) for all nodes on level.

        @param indexLevel : index of level
        @author Nicolas Dubois
        """
        level = self._levels[indexLevel]
        for node in level:
            node.upBarycenterIndex()

    def _shiftSameBarycenter(self, indexLevel):
        """
        Do a left circular shifting on nodes with same barycenter on a level.

        For each group of nodes which have the same pre-calculated value, do a
        left circular shifting of the nodes.

        @param indexLevel : index of level
        @author Nicolas Dubois
        """
        level = self._levels[indexLevel]

        # Save current level
        levelSaved = level[:]
        # Count crossings
        nbIntersections = self._getNbIntersectAll()

        # Shift same barycenter
        for i in range(len(level) - 1):
            if level[i].getBarycenter() is not None and level[i].getBarycenter() == level[i + 1].getBarycenter():

                level.insert(i, level.pop(i + 1))
                # Fix index
                level[i].setIndex(i)
                level[i + 1].setIndex(i + 1)

        # If new order give more intersections, return to old order
        if self._getNbIntersectAll() > nbIntersections:
            self._levels[indexLevel] = levelSaved
            for i in range(len(levelSaved)):
                levelSaved[i].setIndex(i)

    def _sortLevel(self, indexLevel):
        """
        Sort nodes on a level according to pre-calculated barycenter value.
        Nodes that don't have a barycenter value keep their place.

        Args:
            indexLevel:  index of level in self.__levels to sort
        """
        level = self._levels[indexLevel]
        levelCopy = level[:]

        nbIntersect = self._getNbIntersectAll()

        # Get list of nodes who have a barycenter value
        listIndex = []
        for i in range(len(levelCopy)):
            if levelCopy[i].getBarycenter() is not None:
                listIndex.append(i)

        # Create list of nodes to sort
        listNodes = []
        for i in listIndex:
            listNodes.append(levelCopy[i])

        # Sort list of nodes
        listNodes.sort(key=SugiyamaGlobals.cmpBarycenter)

        # Put sorted list in levelCopy
        for i in range(len(listNodes)):
            levelCopy[listIndex[i]] = listNodes[i]

        # Fix indexes
        for i in range(len(levelCopy)):
            levelCopy[i].setIndex(i)

        # If there are more intersections than before, keep original order
        nbIntersect2 = self._getNbIntersectAll()
        if nbIntersect < nbIntersect2:
            # Fix indexes
            for i in range(len(level)):
                level[i].setIndex(i)
        else:
            # Else set new order
            self._levels[indexLevel] = levelCopy
        # nbIntersect3 = self.__getNbIntersectAll()    NOT USED

    def _getNbIntersectAll(self):
        """

        Returns:  The number of intersections between hierarchy relations.
        """
        count = 0
        for i in range(len(self._levels) - 1):
            count += self._getNbIntersect2Levels(i)

        return count

    def _getNbIntersect2Levels(self, upperLevel):
        """
        The two levels index are [upperLevel] and [upperLevel + 1].

        Args:
            upperLevel:  index of upper level

        Returns: The intersections number of hierarchical links between two levels.
        """
        # Get nodes from the level
        nodes = self._levels[upperLevel]

        # Count intersect
        count = 0

        # For each node of the layer
        for indFatherL in range(len(nodes) - 1):
            # For each son of the current node
            for (sonL, link) in nodes[indFatherL].getChildren():

                # Check intersect with all next parents
                indFatherR = indFatherL + 1
                while indFatherR < len(nodes):
                    for (sonR, rLink) in nodes[indFatherR].getChildren():
                        # If intersect
                        if sonL.getIndex() > sonR.getIndex():
                            count += 1
                    indFatherR += 1

        return count

    def _fixNodesNeighbors(self):
        """
        For each node, fix his right neighbor.

        @author Nicolas Dubois
        """
        # For each node, fix his neighbors if he has, None else
        for level in self._levels:
            nbNodes = len(level)

            for i in range(nbNodes - 1):
                level[i + 1].setLeftNode(level[i])
                level[i].setRightNode(level[i + 1])

            # For first and last nodes of the level
            level[0].setLeftNode(None)      # type: ignore
            level[nbNodes - 1].setRightNode(cast(SugiyamaNode, None))

    def _fixNodesPositions(self):

        # Compute start positions packed on left
        y: int = UP_MARGIN
        for level in self._levels:
            x:         int = LEFT_MARGIN
            maxHeight: int = 0

            for node in level:
                (width, height) = node.getSize()
                node.setPosition(x, y)
                x += width + H_SPACE
                maxHeight = max(maxHeight, height)
            y += maxHeight + V_SPACE

        if self._preferences.sugiyamaStepByStep is True:
            SugiyamaGlobals.waitKey(self._extensionsFacade, optionalMessage=None)
        else:
            self.logger.info(f'.__fixNodesPositions() is complete')

        # While nodes have to be moved
        moved: bool = True
        while moved:
            moved = False
            # Compute average coordinates for each node
            for level in self._levels:
                for node in level:
                    if node.balance():
                        moved = True
                        msg: str = f'LEVEL - node: {node} {level}'
                        if self._preferences.sugiyamaStepByStep is True:
                            SugiyamaGlobals.waitKey(self._extensionsFacade, msg)
                        else:
                            self.logger.info(msg)

    def _fixLinksPositions(self):
        """
        Compute links new positions.
        """
        # For each hierarchical link, fix anchors coordinates
        for level in self._levels:
            for node in level:
                node.fixAnchorPos()

        # For each hierarchical link, add control points to pass through
        # each virtual node
        for link in self._sugiyamaLinksList:
            link.fixControlPoints()
