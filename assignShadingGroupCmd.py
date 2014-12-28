import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys

kPluginCmdName = "assignShadingGroup"

# Command
class assignShadingGroupCommand(OpenMayaMPx.MPxCommand):


    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        self.mUndo = []

    def isUndoable(self):
        return True

    def undoIt(self): 
        OpenMaya.MGlobal.displayInfo( "Undo: assignShadingGroup\n" )

        # Reversed for undo :)
        for m in reversed(self.mUndo):
            m.undoIt()

    def redoIt(self): 
        OpenMaya.MGlobal.displayInfo( "Redo: assignShadingGroup\n" )
        
        for m in self.mUndo:
            m.doIt()
        
    def doIt(self,argList):
        
        # Helper function to append new plug without overriding any logical index
        def getNextAvailableLogicalPlug(plug):
            
            indices = OpenMaya.MIntArray()  
            max = -1
            
            if plug.isArray():  
                plug.getExistingArrayAttributeIndices(indices)
                
                for i in range(0, indices.length()):
                    if(indices[i] > max):
                        max = indices[i]
                    
            # 0 if there is no element :)
            return plug.elementByLogicalIndex(max + 1)

        # Helper function to find shading engine
        def getSGNode():
                            
            list = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getActiveSelectionList(list)       
            iter = OpenMaya.MItSelectionList(list)
            
            sgDepNode = OpenMaya.MObject()
            
            while not iter.isDone():
                
                iter.getDependNode(sgDepNode)
                
                if sgDepNode.hasFn(OpenMaya.MFn.kShadingEngine):
                    return sgDepNode
                
                iter.next()
            
            return sgDepNode
            
        list = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(list, ) 
        iter = OpenMaya.MItSelectionList(list)
        
        sgDepNode = getSGNode()
        sgDagSetMemberPlug = OpenMaya.MFnDependencyNode(sgDepNode).findPlug('dagSetMembers')
        
        while(not iter.isDone()):

            # Filter by dag nodes
            if iter.itemType() == OpenMaya.MItSelectionList.kDagSelectionItem:
                
                dagPath = OpenMaya.MDagPath()   
                iter.getDagPath(dagPath)            
                dagPath.extendToShape()
                
                instObjGroupsAttr = OpenMaya.MFnDagNode(dagPath).attribute('instObjGroups')         
                
                instPlugArray = OpenMaya.MPlug(dagPath.node(), instObjGroupsAttr)       
                instPlugArrayElem = instPlugArray.elementByLogicalIndex(dagPath.instanceNumber())
                
                # If instance already has connections, disconnect them
                if instPlugArrayElem.isConnected():
                    
                    connectedPlugs = OpenMaya.MPlugArray()      
                    instPlugArrayElem.connectedTo(connectedPlugs, False, True)

                    mdgModifier = OpenMaya.MDGModifier()
                    self.mUndo.append(mdgModifier)

                    for i in range(connectedPlugs.length()):
                        mdgModifier.disconnect(instPlugArrayElem, connectedPlugs[i])
                    
                    mdgModifier.doIt()                          
                                
                sgDagSetMemberPlugElem = getNextAvailableLogicalPlug(sgDagSetMemberPlug)

                mdgModifier = OpenMaya.MDGModifier()
                self.mUndo.append(mdgModifier)
                mdgModifier.connect(instPlugArrayElem, sgDagSetMemberPlugElem)  
                mdgModifier.doIt()                      
                        
            iter.next()

# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( assignShadingGroupCommand() )
    
# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )