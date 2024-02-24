# -*- coding: utf-8 -*-
# Exploded Assembly Animation workbench for FreeCAD
# (c) 2016 Javier Martínez García
#***************************************************************************
#*   (c) Javier Martínez García 2016                                       *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License (GPL)            *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Lesser General Public License for more details.                   *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************/

from __future__ import division
import os
import time
import FreeCAD
import Part


# Container python folder 'ExplodedAssembly'
class ExplodedAssemblyFolder:
    def __init__(self, obj):
        obj.addProperty('App::PropertyPythonObject', 'InitialPlacements').InitialPlacements = {}
        obj.addProperty('App::PropertyInteger', 'AnimationStep').AnimationStep = 0
        obj.addProperty('App::PropertyInteger', 'CurrentTrajectory').CurrentTrajectory = 0
        obj.addProperty('App::PropertyBool', 'ResetAnimation').ResetAnimation = False
        obj.addProperty('App::PropertyBool', 'InAnimation').InAnimation = False
        obj.addProperty('App::PropertyBool', 'RemoveAllTrajectories').RemoveAllTrajectories = False
        obj.Proxy = self

    def execute(self, fp):
        if fp.ResetAnimation:
            resetPlacement()
            fp.ResetAnimation = False

        if fp.RemoveAllTrajectories:
            fp.RemoveAllTrajectories = False
            for obj in fp.Group:
                FreeCAD.ActiveDocument.removeObject(obj.Name)

            # reset initial placement dict
            fp.InitialPlacements = {}


class ExplodedAssemblyFolderViewProvider:
    def __init__(self, obj):
        obj.Proxy = self

    def getIcon(self):
        __dir__ = os.path.dirname(__file__)
        return __dir__ + '/icons/WorkbenchIcon.svg'


def checkDocumentStructure():
    # checks the existence of the folder 'ExplodedAssembly' and creates it if not
    try:
        folder = FreeCAD.ActiveDocument.ExplodedAssembly

    except:
        folder = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython', 'ExplodedAssembly')
        ExplodedAssemblyFolder(folder)
        ExplodedAssemblyFolderViewProvider(folder.ViewObject)


# Bolt group trajectory ########################################################
class BoltGroupObject:
    def __init__(self, obj):
        obj.addProperty('App::PropertyPythonObject', 'names').names = []
        obj.addProperty('App::PropertyVectorList', 'dir_vectors').dir_vectors = []
        obj.addProperty('App::PropertyVectorList', 'rot_vectors').rot_vectors = []
        obj.addProperty('App::PropertyVectorList', 'rot_centers').rot_centers = []
        #
        obj.addProperty('App::PropertyFloat', 'Distance').Distance = 20.0
        obj.addProperty('App::PropertyFloat', 'Revolutions').Revolutions = 0.0
        obj.addProperty('App::PropertyFloat', 'AnimationStepTime').AnimationStepTime = 0.0
        obj.addProperty('App::PropertyInteger', 'AnimationSteps').AnimationSteps = 20
        obj.Proxy = self

    def onChanged(self, fp, prop):
        pass

    def execute(self, fp):
        resetPlacement()
        goToEnd()
        FreeCAD.ActiveDocument.ExplodedAssembly.CurrentTrajectory = -1

class BoltGroupObjectViewProvider:
    def __init__(self, obj):
        obj.Proxy = self

    def getIcon(self):
        __dir__ = os.path.dirname(__file__)
        return __dir__ + '/icons/BoltGroup.svg'


def createBoltDisassemble():
    # add object to the Document and initialize it
    SDObj = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython','BoltGroup')
    BoltGroupObject(SDObj)
    BoltGroupObjectViewProvider(SDObj.ViewObject)
    # retrieve selection
    selection = FreeCAD.Gui.Selection.getSelectionEx()
    # try to find the face wich its normal gives the disassemble direction
    dir_vector = FreeCAD.Vector(0, 0, 1)
    for sel_obj in selection:
        for subObject in sel_obj.SubObjects:
            try:
                dir_vector = subObject.normalAt(0, 0)
                break
            except:
                pass

    for sel_obj in selection:
        for subObject in sel_obj.SubObjects:
            try:
                if str(subObject.Curve)[0:6] == 'Circle':
                    # append object name
                    SDObj.names.append(sel_obj.Object.Name)
                    # append unmount direction                    
                    SDObj.dir_vectors += [(dir_vector[0], dir_vector[1], dir_vector[2])]
                    # apend rotation axis                    
                    SDObj.rot_vectors += [(dir_vector[0], dir_vector[1], dir_vector[2])]
                    # append rotation center                                        
                    SDObj.rot_centers += [subObject.Curve.Center]
                    # append initial values for distance, revs, steps
                    SDObj.distance.append(10.0)
                    SDObj.revolutions.append(0)
                    SDObj.animation_steps.append(20.0)

            except:
                pass

    EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly
    # add initial placement if this is the first movement of the parts
    for name in SDObj.names:
        try:
            plm = EAFolder.InitialPlacements[name]

        except:
            an_object = FreeCAD.ActiveDocument.getObject(name)
            # prepare object placement for JSON serialization
            # store base placement as vector
            plm = an_object.Placement
            base = (plm.Base[0], plm.Base[1], plm.Base[2])
            # store rotation as a quaternion
            rot = plm.Rotation.Q
            placement = (base, rot)
            EAFolder.InitialPlacements[name] = placement

    # place inside ExplodedAssembly folder and update document
    EAFolder.addObject(SDObj)
    updateTrajectoryLines()
    FreeCAD.ActiveDocument.recompute()


# simple group trajectory ########################################################
class SimpleGroupObject:
    def __init__(self, obj):
        obj.addProperty('App::PropertyPythonObject', 'names').names = []
        obj.addProperty('App::PropertyVectorList', 'dir_vectors').dir_vectors = []
        obj.addProperty('App::PropertyVectorList', 'rot_vectors').rot_vectors = []
        obj.addProperty('App::PropertyVectorList', 'rot_centers').rot_centers = []
        #
        obj.addProperty('App::PropertyFloat', 'Distance').Distance = 20.0
        obj.addProperty('App::PropertyFloat', 'Revolutions').Revolutions = 0.0
        obj.addProperty('App::PropertyFloat', 'AnimationStepTime').AnimationStepTime = 0.0
        obj.addProperty('App::PropertyInteger', 'AnimationSteps').AnimationSteps = 20
        obj.Proxy = self

    def onChanged(self, fp, prop):
        pass

    def execute(self, fp):
        resetPlacement()
        goToEnd()
        FreeCAD.ActiveDocument.ExplodedAssembly.CurrentTrajectory = -1


class SimpleGroupObjectViewProvider:
    def __init__(self, obj):
        obj.Proxy = self

    def getIcon(self):
        __dir__ = os.path.dirname(__file__)
        return __dir__ + '/icons/SimpleGroup.svg'


def createSimpleDisassemble():
    # add object to the Document and initialize it
    SDObj = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython', 'SimpleGroup')
    SimpleGroupObject(SDObj)
    SimpleGroupObjectViewProvider(SDObj.ViewObject)
    # retrieve selection
    selection = FreeCAD.Gui.Selection.getSelectionEx()
    # the last face of the last object selected determines the disassemble dir vector
    dir_vector = selection[-1].SubObjects[-1].normalAt(0, 0)
    # the rotation center is the center of mass of the last face selected
    rot_center = selection[-1].SubObjects[-1].CenterOfMass    
    # ignore last object if it cannot be moved, it is only used for positioning
    if FreeCAD.ActiveDocument.getObject(selection[-1].Object.Name) is None:
        del selection[-1]            
    # create trajectory data
    obj_selection = FreeCAD.Gui.Selection.getSelection()
    for i, sel_obj in enumerate(obj_selection):
        if len(obj_selection) > 1 and i == ( len(obj_selection)-1 ):
            # last object only serves as reference
            break        
        SDObj.names.append(sel_obj.Name)
        # append unmount direction        
        SDObj.dir_vectors += [(dir_vector[0], dir_vector[1], dir_vector[2])]
        # apend rotation axis
        SDObj.rot_vectors += [(dir_vector[0], dir_vector[1], dir_vector[2])]
        # append rotation center
        SDObj.rot_centers += [(rot_center[0], rot_center[1], rot_center[2])]

    EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly
    # add initial placement if this is the first move of the parts
    for name in SDObj.names:
        try:
            plm = EAFolder.InitialPlacements[name]

        except:
            an_object = FreeCAD.ActiveDocument.getObject(name)
            # prepare object placement for JSON serialization
            # store base placement as vector
            plm = an_object.Placement
            base = (plm.Base[0], plm.Base[1], plm.Base[2])
            # store rotation as a quaternion
            rot = plm.Rotation.Q
            placement = (base, rot)
            EAFolder.InitialPlacements[name] = placement

    # place inside ExplodedAssembly folder and update document
    EAFolder.addObject(SDObj)
    updateTrajectoryLines()
    FreeCAD.ActiveDocument.recompute()


# wire group trajectory ########################################################
class WireGroupObject:
    def __init__(self, obj):
        obj.addProperty('App::PropertyPythonObject', 'names').names = []
        obj.addProperty('App::PropertyFloat', 'AnimationStepTime').AnimationStepTime = 0.0
        obj.addProperty('App::PropertyInteger', 'AnimationStepsEdge').AnimationStepsEdge = 10
        obj.Proxy = self

    def onChanged(self, fp, prop):
        pass

    def execute(self, fp):
        resetPlacement()
        goToEnd()
        FreeCAD.ActiveDocument.ExplodedAssembly.CurrentTrajectory = -1


class WireGroupObjectViewProvider:
    def __init__(self, obj):
        obj.Proxy = self

    def getIcon(self):
        __dir__ = os.path.dirname(__file__)
        return __dir__ + '/icons/WireTrajectory.svg'


def createWireDisassemble():
    # select the objects and finally the trajectory objects
    # Animation will run over the edges of the trajectory object
    sel_objects = FreeCAD.Gui.Selection.getSelection()[0:-2]
    sel_wire = FreeCAD.Gui.Selection.getSelection()[-1]
    # Initialize object
    WDObj = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython', 'WireGroup')
    WireGroupObject(WDObj)
    #WireGroupObjectViewProvider(WDObj.ViewObject)
    # add object names
    for obj in sel_objects:
        obj_name = obj.Name
        WDObj.names.append(obj_name)

    # add trajectory objecto to this new wire group
    WDObj.addObject(sel_wire)
    # place inside ea folder
    EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly
    EAFolder.addObject(WDObj)
    FreeCAD.ActiveDocument.recompute()





def resetPlacement():
    # restore the placement of all objects
    EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly
    # set everything to its initial position
    for traj in EAFolder.Group:
        for name in traj.names:
            obj = FreeCAD.ActiveDocument.getObject(name)
            # create placement from initial placement list
            plm = EAFolder.InitialPlacements[name]
            base = FreeCAD.Vector(plm[0][0], plm[0][1], plm[0][2])
            rot = FreeCAD.Rotation(plm[1][0], plm[1][1], plm[1][2], plm[1][3])
            obj.Placement = FreeCAD.Placement(base, rot)



def runAnimation(start=0, end=0, mode='complete', direction='forward'):
    # runs the animation from a start step number to the end step number
    # mode: 'complete', 'toPoint'
    # 'complete' means forward from start to end and backwars if already in end
    # 'forward' means disassemble from start to end
    # 'backward' means assemble from start to end
    # 'toPoint' means go to an especific end point without animation
    # toggle 'InAnimation variable' to disable other icons temporally
    FreeCAD.ActiveDocument.ExplodedAssembly.InAnimation = True
    # # complete mode
    # start animation
    EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly.Group
    if mode == 'complete':
        number_of_trajectories = len(EAFolder)

    elif mode == 'toPoint':
        number_of_trajectories = len(EAFolder) - start - end

    traj_iterator = range(number_of_trajectories)
    if direction == 'backward':
        traj_iterator = range(number_of_trajectories-1, -1, -1)

    animation_paused = False
    for r in traj_iterator:
        # break animation loop if not InAnimation (this is where pause animation takes place):
        EA = FreeCAD.ActiveDocument.ExplodedAssembly
        if not(EA.InAnimation):
            animation_paused = True
            break

        if direction == 'forward':
            traj = EAFolder[r+start]
            # set current stop point
            EA.CurrentTrajectory = r+start

        elif direction == 'backward':
            traj = EAFolder[r]
            # set current stop point
            EA.CurrentTrajectory = r-1

        # highligh current trajectory
        FreeCAD.Gui.Selection.addSelection(traj)
        # If trajectory is a bolt group or simple group:
        if traj.Name[0:11] == 'SimpleGroup' or traj.Name[0:9] == 'BoltGroup':
            # buffer objects
            objects = []
            for name in traj.names:
                objects.append(FreeCAD.ActiveDocument.getObject(name))

            inc_D = traj.Distance / float(traj.AnimationSteps)
            inc_R = traj.Revolutions / float(traj.AnimationSteps)
            if direction == 'backward':
                inc_D = inc_D*-1.0
                inc_R = inc_R*-1.0

            for i in range(traj.AnimationSteps):
                if i == 0:
                    dir_vectors = []
                    rot_vectors = []
                    rot_centers = []
                    for s in range(len(objects)):
                        dir_vectors.append(FreeCAD.Vector(tuple(traj.dir_vectors[s])))
                        rot_vectors.append(FreeCAD.Vector(tuple(traj.rot_vectors[s])))
                        rot_centers.append(FreeCAD.Vector(tuple(traj.rot_centers[s])))

                for n in range(len(objects)):
                    obj = objects[n]
                    obj_base = dir_vectors[n]*inc_D
                    obj_rot = FreeCAD.Rotation(rot_vectors[n], inc_R*360.0)
                    obj_rot_center = rot_centers[n]
                    incremental_placement = FreeCAD.Placement(obj_base, obj_rot, obj_rot_center)
                    obj.Placement = incremental_placement.multiply(obj.Placement)

                FreeCAD.Gui.updateGui()
                time.sleep(traj.AnimationStepTime)

        else:
            # if traj is a WireGroup object
            steps = traj.AnimationStepsEdge
            edges = traj.Shape.Edges
            for edge in edges:
                points = edge.discretize(steps)
                vectors = []
                for i in range(len(points)-1):
                    pa = points[i]
                    pb = points[i+1]
                    v = (pb[0]+pa[0], pb[1]+pa[1], pb[2]+pa[2])
                    vectors.append(v)

            if direction == 'backward':
                vectors.reverse()

            for v in vectors:
                for i in range((len(traj.names))):
                    obj = FreeCAD.ActiveDocument.getObject(traj.names[i])
                    # incremental placement
                    obj.Placement.x = obj.Placement.x + v[0]
                    obj.Placement.y = obj.Placement.y + v[1]
                    obj.Placement.z = obj.Placement.z + v[2]

                FreeCAD.Gui.udpateGui()
                time.sleep(traj.AnimationStepTime)


        # clear selection
        FreeCAD.Gui.Selection.clearSelection()

    # set pointer to current trajectory index
    EA = FreeCAD.ActiveDocument.ExplodedAssembly
    # toggle InAnimation to activate icons deactivated before
    EA.InAnimation = False
    # set CurrentTrajectory number
    if not(animation_paused):
        if direction == 'forward' and end == 0:
            EA.CurrentTrajectory = -1

        if direction == 'backward' and start == 0:
            EA.CurrentTrajectory = 0



def goToEnd():
    # start animation
    EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly.Group
    for traj in EAFolder:
        objects = []
        for name in traj.names:
            objects.append(FreeCAD.ActiveDocument.getObject(name))

        inc_D = traj.Distance / float(1)
        inc_R = traj.Revolutions / float(1)
        for n in range(len(objects)):
            obj = objects[n]
            obj_base = traj.dir_vectors[n]*inc_D
            obj_rot = FreeCAD.Rotation(traj.rot_vectors[n], inc_R*360)
            obj_rot_center = traj.rot_centers[n]
            incremental_placement = FreeCAD.Placement(obj_base, obj_rot, obj_rot_center)
            obj.Placement = incremental_placement.multiply(obj.Placement)

    FreeCAD.Gui.updateGui()


def goToSelectedTrajectory():
    # retrieve selection
    traj_name = FreeCAD.Gui.Selection.getSelectionEx()[0].Object.Name
    # start animation
    EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly.Group
    for r in range(len(EAFolder)):
        traj = EAFolder[r]
        objects = []
        update_gui = False
        for name in traj.names:
            objects.append(FreeCAD.ActiveDocument.getObject(name))

        if traj_name == traj.Name:
            inc_D = traj.Distance / float(traj.AnimationSteps)
            inc_R = traj.Revolutions / float(traj.AnimationSteps)
            animation_range = traj.AnimationSteps
            update_gui = True

        else:
            inc_D = traj.Distance / float(1)
            inc_R = traj.Revolutions / float(1)
            animation_range = 1

        for i in range(animation_range):
            if i == 0:
                dir_vectors = []
                rot_vectors = []
                rot_centers = []
                for s in range(len(objects)):
                    dir_vectors.append(FreeCAD.Vector(tuple(traj.dir_vectors[s])))
                    rot_vectors.append(FreeCAD.Vector(tuple(traj.rot_vectors[s])))
                    rot_centers.append(FreeCAD.Vector(tuple(traj.rot_centers[s])))

            for n in range(len(objects)):
                obj = objects[n]
                obj_base = dir_vectors[n]*inc_D
                obj_rot = FreeCAD.Rotation(rot_vectors[n], inc_R*360)
                obj_rot_center = rot_centers[n]
                incremental_placement = FreeCAD.Placement(obj_base, obj_rot, obj_rot_center)
                obj.Placement = incremental_placement.multiply(obj.Placement)

            if update_gui:
                FreeCAD.Gui.updateGui()

        if traj_name == traj.Name:
            # exit once selected trajectory has been reached
            break

    # set current trajectory cursor to current trajectory
    FreeCAD.ActiveDocument.ExplodedAssembly.CurrentTrajectory = r

def placeBeforeSelectedTrajectory():
    # select the trajectoreis you want to reallocate and finally,
    # the trajectory before wich you want to place them
    sel_traj = FreeCAD.Gui.Selection.getSelectionEx()
    # retrieve EA folder
    EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly
    # create an auxiliary folder to re organizate exploded assembly
    aux_folder = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroup','ea_aux')
    before_traj = sel_traj[-1].Object
    for traj in EAFolder.Group:
        if traj.Name == before_traj.Name:
            for sel in sel_traj:
                aux_folder.addObject(sel.Object)

        elif traj.Name != before_traj.Name:
            add_traj = True
            for sel in sel_traj:
                if traj.Name == sel.Object.Name:
                    add_traj = False
                    break

            if add_traj:
                aux_folder.addObject(traj)

    # save the attributes of EAFolder'
    EAF_InitialPlacements = EAFolder.InitialPlacements
    EAF_CurrentTrajectory = EAFolder.CurrentTrajectory
    EAF_ResetAnimation = EAFolder.ResetAnimation
    EAF_InAnimation = EAFolder.InAnimation
    EAF_RemoveAllTrajectories = EAFolder.RemoveAllTrajectories
    FreeCAD.ActiveDocument.removeObject(EAFolder.Name)
    # create the EAFolder
    EAFolder = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython', 'ExplodedAssembly')
    ExplodedAssemblyFolder(EAFolder)
    ExplodedAssemblyFolderViewProvider(EAFolder.ViewObject)
    # restore its content
    for traj in aux_folder.Group:
        EAFolder.addObject(traj)

    EAFolder.InitialPlacements = EAF_InitialPlacements
    EAFolder.CurrentTrajectory = EAF_CurrentTrajectory
    EAFolder.ResetAnimation = EAF_ResetAnimation
    EAFolder.InAnimation = EAF_InAnimation
    EAFolder.RemoveAllTrajectories = EAF_RemoveAllTrajectories
    # remove auxiliary folder
    FreeCAD.ActiveDocument.removeObject(aux_folder.Name)
    # recompute document
    FreeCAD.ActiveDocument.recompute()
    FreeCAD.Gui.updateGui()


def modifyIndividualObjectTrajectory():
    # multi direction for simple trajectory(at the moment)
    # selection:    trajectory_obj + shape + normal direction
    # selection:    trajectory_obj + normal_direction(selected over the shape)
    sel_traj = FreeCAD.Gui.Selection.getSelectionEx()[0].Object
    sel_objects = FreeCAD.Gui.Selection.getSelectionEx()[1:]
    if len(sel_objects) == 1:
        obj_name = sel_objects[0].Object.Name
        sel_face = sel_objects[0].SubObjects[0]

    else:
        obj_name = sel_objects[0].Object.Name
        sel_face = sel_objects[1].SubObjects[0]

    for i in range(len(sel_traj.names)):
        name = sel_traj.names[i]
        if obj_name == name:
            # if selected trajectory is a simple trajectory:
            if sel_traj.Name[0:11] == 'SimpleGroup':
                # asign new explosion direction to sel normal
                v = sel_face.normalAt(0,0)
                sel_traj.dir_vectors[i] = (v[0], v[1], v[2])
                break

            # if selected trajectory is a bolt group
        elif sel_traj.Name[0:9] == 'BoltGroup':
                # assign new exploded direction, rotation centre and vector
                v = sel_face.normalAt(0,0)
                c = sel_face.CenterOfMass
                sel_traj.dir_vectors[i] = (v[0], v[1], v[2])
                sel_traj.rot_vectors[i] = (v[0], v[1], v[2])
                sel_traj.rot_centers[i] = (c[0], c[1], c[2])
                break



def updateTrajectoryLines():
    # TODO this is disabled because is no longer accurate and needs conversion to new placement
    # goes to a try/except until solved
    #return
    try:
        EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly.Group
        # remove all the previous trajectory lines
        for traj in EAFolder:
            for lines in traj.Group:
                FreeCAD.ActiveDocument.removeObject(lines.Name)

        # re-draw all trajectories
        for traj in EAFolder:
            lines_compound = []
            objects = []
            for name in traj.names:
                objects.append(FreeCAD.ActiveDocument.getObject(name))

            inc_D = traj.Distance
            dir_vectors = []
            rot_centers = []
            for s in range(len(objects)):
                dir_vectors.append(FreeCAD.Vector(tuple(traj.dir_vectors[s])))
                rot_centers.append(FreeCAD.Vector(tuple(traj.rot_centers[s])))

            for n in range(len(objects)):
                pa = rot_centers[n]# objects[n].Placement.Base
                pb = rot_centers[n] + dir_vectors[n]*inc_D
                lines_compound.append(Part.makeLine(pa, pb))

            l_obj = FreeCAD.ActiveDocument.addObject('Part::Feature','trajectory_line')
            l_obj.Shape = Part.makeCompound(lines_compound)
            l_obj.ViewObject.DrawStyle = "Dashed"
            l_obj.ViewObject.LineWidth = 1.0
            traj.addObject(l_obj)
    except Exception as e:
        print("Trajectory Line exception:",e)
    
    FreeCAD.Gui.updateGui()



def visibilityTrajectoryLines(show):
    # show or hide trajectory lines
    EAFolder = FreeCAD.ActiveDocument.ExplodedAssembly.Group
    for traj in EAFolder:
        for lines in traj.Group:
            lines.ViewObject.Visibility = show
