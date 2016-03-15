from .. import problems
from .. utils.nodes import idToNode, idToSocket

class NodeNetwork:
    def __init__(self, nodeIDs, forestData):
        self.nodeIDs = nodeIDs
        self.forestData = forestData
        self.type = "Invalid"
        self.name = ""
        self.description = ""
        self.identifier = None
        self.analyse()

    def analyse(self):
        self.findSystemNodes()

        groupNodeAmount = self.groupInAmount + self.groupOutAmount
        loopNodeAmount = self.loopInAmount + self.generatorAmount + self.reassignParameterAmount + self.breakAmount

        self.type = "Invalid"

        if groupNodeAmount + loopNodeAmount + self.scriptAmount == 0:
            self.type = "Main"
        elif self.scriptAmount == 1:
            self.type = "Script"
        elif loopNodeAmount == 0:
            if self.groupInAmount == 0 and self.groupOutAmount == 1:
                self.identifier = self.groupOutputNode.groupInputIdentifier
                if self.identifier == "": self.identifier = None
            elif self.groupInAmount == 1 and self.groupOutAmount == 0:
                self.type = "Group"
            elif self.groupInAmount == 1 and self.groupOutAmount == 1:
                if idToNode(self.groupInputIDs[0]).identifier == idToNode(self.groupOutputIDs[0]).groupInputIdentifier:
                    self.type = "Group"
        elif groupNodeAmount == 0:
            possibleIdentifiers = list({idToNode(nodeID).loopInputIdentifier for nodeID in self.generatorOutputIDs + self.reassignParameterIDs + self.breakIDs})
            if self.loopInAmount == 0 and len(possibleIdentifiers) == 1:
                self.identifier = possibleIdentifiers[0]
            elif self.loopInAmount == 1 and len(possibleIdentifiers) == 0:
                self.type = "Loop"
            elif self.loopInAmount == 1 and len(possibleIdentifiers) == 1:
                if idToNode(self.loopInputIDs[0]).identifier == possibleIdentifiers[0]:
                    self.type = "Loop"

        if self.type == "Script": owner = self.scriptNode
        elif self.type == "Group": owner = self.groupInputNode
        elif self.type == "Loop": owner = self.loopInputNode

        if self.type in ("Group", "Loop", "Script"):
            self.identifier = owner.identifier
            self.name = owner.subprogramName
            self.description = owner.subprogramDescription

            # check if a subprogram invokes itself
            if self.identifier in self.getInvokedSubprogramIdentifiers():
                self.type = "Invalid"
                problems.SubprogramInvokesItself(self).report()

    def findSystemNodes(self):
        self.groupInputIDs = []
        self.groupOutputIDs = []
        self.loopInputIDs = []
        self.generatorOutputIDs = []
        self.reassignParameterIDs = []
        self.breakIDs = []
        self.scriptIDs = []
        self.invokeSubprogramIDs = []

        appendToList = {
            "an_GroupInputNode" :            self.groupInputIDs.append,
            "an_GroupOutputNode" :           self.groupOutputIDs.append,
            "an_LoopInputNode" :             self.loopInputIDs.append,
            "an_LoopGeneratorOutputNode" :   self.generatorOutputIDs.append,
            "an_ReassignLoopParameterNode" : self.reassignParameterIDs.append,
            "an_LoopBreakNode" :             self.breakIDs.append,
            "an_ScriptNode" :                self.scriptIDs.append,
            "an_InvokeSubprogramNode" :      self.invokeSubprogramIDs.append }


        typeByNode = self.forestData.typeByNode
        for nodeID in self.nodeIDs:
            if typeByNode[nodeID] in appendToList:
                appendToList[typeByNode[nodeID]](nodeID)

        self.groupInAmount = len(self.groupInputIDs)
        self.groupOutAmount = len(self.groupOutputIDs)
        self.loopInAmount = len(self.loopInputIDs)
        self.generatorAmount = len(self.generatorOutputIDs)
        self.reassignParameterAmount = len(self.reassignParameterIDs)
        self.breakAmount = len(self.breakIDs)
        self.scriptAmount = len(self.scriptIDs)

    def getInvokedSubprogramIdentifiers(self):
        return list({idToNode(nodeID).subprogramIdentifier for nodeID in self.invokeSubprogramIDs})

    @staticmethod
    def join(networks):
        forestData = next(iter(networks)).forestData

        nodeIDs = []
        for network in networks:
            nodeIDs.extend(network.nodeIDs)
        return NodeNetwork(nodeIDs, forestData)

    def getNodes(self):
        return [idToNode(nodeID) for nodeID in self.nodeIDs]

    def getAnimationNodes(self):
        return [node for node in self.getNodes() if node.isAnimationNode]

    @property
    def treeName(self):
        return next(iter(self.nodeIDs))[0]

    @property
    def nodeTree(self):
        return bpy.data.node_groups[self.treeName]

    @property
    def isSubnetwork(self):
        return self.type in ("Group", "Loop", "Script")

    @property
    def ownerNode(self):
        try: return idToNode(self.forestData.nodeByIdentifier[self.identifier])
        except: return None

    @property
    def groupInputNode(self):
        try: return idToNode(self.groupInputIDs[0])
        except: return None

    @property
    def groupOutputNode(self):
        try: return idToNode(self.groupOutputIDs[0])
        except: return None

    @property
    def loopInputNode(self):
        try: return idToNode(self.loopInputIDs[0])
        except: return None

    @property
    def generatorOutputNodes(self):
        return [idToNode(nodeID) for nodeID in self.generatorOutputIDs]

    @property
    def reassignParameterNodes(self):
        return [idToNode(nodeID) for nodeID in self.reassignParameterIDs]

    @property
    def breakNodes(self):
        return [idToNode(nodeID) for nodeID in self.breakIDs]

    @property
    def scriptNode(self):
        try: return idToNode(self.scriptIDs[0])
        except: return None


    def getSortedAnimationNodes(self):
        '''
        Uses a depth-first search algorithm for topological sorting
        of the directed acyclic graph
        '''

        unmarkedNodes = self.nodeIDs.copy()
        temporaryMarkedNodes = set()
        markedNodes = set()
        sortedListReversed = list()

        def iterDependentNodes(node):
            for socket in self.forestData.socketsByNode[node][1]:
                for otherSocket in self.forestData.linkedSockets[socket]:
                    yield otherSocket[0]

        def visit(node):
            if node in temporaryMarkedNodes:
                print("cycle")
                raise Exception("Cycle")
            if node not in markedNodes:
                temporaryMarkedNodes.add(node)
                for dependentNode in iterDependentNodes(node):
                    visit(dependentNode)
                markedNodes.add(node)
                temporaryMarkedNodes.remove(node)
                sortedListReversed.append(node)

        while unmarkedNodes:
            visit(unmarkedNodes.pop())

        nodes = [idToNode(node) for node in reversed(sortedListReversed)]
        return [node for node in nodes if node.isAnimationNode]
