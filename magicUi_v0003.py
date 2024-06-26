# camera and cone tools: Camera Magic v3.04262024 #
# use at your own risk #
# Line 256,259 import polyCam and 6ftman path need to change path location#
# create 5/29/2020#

# update:4/26/2024


import maya.cmds as cmds
import maya.mel as mel
import re

# incase no TYPE plugin
if not cmds.pluginInfo('Type', loaded=True, query=True):
    cmds.loadPlugin('Type')


def multi_cut():
    cmds.MultiCutTool()


def insert_loop_tool():
    cmds.InsertEdgeLoopTool()


def freeze_transform():
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)


def reverse_normals():
    selected_objects = cmds.ls(selection=True)
    for obj in selected_objects:
        cmds.polyNormal(obj, normalMode=0, userNormalMode=0)


def setClipPlanes():
    """
    Sets the near clip plane to 1 and the far clip plane to 1000000.
    """
    camera_list = cmds.ls(type="camera")
    for cam in camera_list:
        cmds.setAttr(cam + ".nearClipPlane", 1)
        cmds.setAttr(cam + ".farClipPlane", 1000000)


def delete_history():
    cmds.DeleteHistory()


def center_pivot():
    cmds.CenterPivot()


def create_parent_constraint():
    # Get the currently selected objects
    selected = cmds.ls(selection=True)

    if len(selected) < 2:
        print("Please select at least two objects.")
        return

    # Create a parent constraint
    cmds.parentConstraint(selected[0], selected[1], maintainOffset=False)
    cmds.delete(parentConstraint)


def create_parent_constraintMO():
    # Get the currently selected objects
    selected = cmds.ls(selection=True)

    if len(selected) < 2:
        print("Please select at least two objects.")
        return

    # Create a parent constraint
    cmds.parentConstraint(selected[0], selected[1], maintainOffset=True)


def create_locator_at_pivot():
    sel = cmds.ls(sl=1)

    for obj in sel:
        newLoc = cmds.spaceLocator()
        newCon = cmds.parentConstraint(obj, newLoc, mo=0)


def bake_simulation():
    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)
    cmds.bakeResults(sm=True, sr=True, t=(start, end))

    pairblend_nodes = cmds.listConnections(s=True, d=True, type="parentConstraint")
    if pairblend_nodes:
        cmds.delete(pairblend_nodes)


def locControl():
    sel = cmds.ls(sl=1)
    startTime = cmds.playbackOptions(q=True, minTime=True)
    endTime = cmds.playbackOptions(q=True, maxTime=True)

    for obj in sel:
        newLoc = cmds.spaceLocator(n='locCtrl#')
        newCon = cmds.parentConstraint(obj, newLoc, mo=0)
        # bake animation to locator#
        cmds.bakeResults(newLoc, time=(startTime, endTime))
        cmds.delete(cn=True)

        # delete keyframe in original#
        cmds.select(sel)
        cmds.cutKey(sel, s=True)
        # parent original back to locator#
        cmds.parentConstraint(newLoc, sel, mo=True)


def set_camText():
    selected_camera = cmds.ls(sl=True)[0]
    cmds.select(tCams)
    cmds.textField(selCamText, edit=True, text=myCams[0])
    cmds.select(clear=True)
    cmds.select(selected_camera)


def cameraFrustum():
    """
    Toggles the camera frustum visibility of the selected camera.
    """
    # Get the selected camera transform
    selected = cmds.ls(selection=True)
    if not selected:
        cmds.warning("Please select a camera!")
        return

    camera = selected[0]

    # Get the camera shape
    camera_shape = cmds.listRelatives(camera, shapes=True)[0]

    # Get the current visibility state
    is_visible = cmds.getAttr(camera_shape + ".displayCameraFrustum")

    # Set the new visibility state (toggle)
    cmds.setAttr(camera_shape + ".displayCameraFrustum", not is_visible)


def lookThrough():
    # Get all cameras in the scene
    cameras = cmds.ls(type='camera')

    for camera in cameras:
        # Get the image planes attached to the camera
        image_planes = cmds.listConnections(camera + '.imagePlane', source=True, destination=False)

        # If the camera has an image plane
        if image_planes:
            for image_plane in image_planes:
                # Set the 'displayOnlyIfCurrent' attribute to True
                cmds.setAttr(image_plane + '.displayOnlyIfCurrent', True)
    cmds.select(clear=True)


def clipPlane():
    defCams = ['perspShape', 'topShape', 'sideShape', 'frontShape']
    for i in defCams:
        cmds.setAttr((i + '.nearClipPlane'), 1.0)
        cmds.setAttr((i + '.farClipPlane'), 10000000)


def defaultCam():
    allCamds = cmds.ls(sl=True)
    cmds.setAttr('imagePlaneShape1.alphaGain', 1)
    cmds.setAttr('imagePlaneShape1.depth', 4500)


def rgbMode():
    # Get all image plane nodes in the scene
    imagePlanes = cmds.ls(type="imagePlane")
    # Loop through each image plane
    for imagePlane in imagePlanes:
        # Set the display mode to "RGB"
        cmds.setAttr(imagePlane + ".displayMode", 2)


def renCam():
    cmds.setAttr('imagePlaneShape1.alphaGain', 0.85)
    cmds.setAttr('imagePlaneShape1.useFrameExtension', 1)
    cmds.setAttr('imagePlaneShape1.frameCache', 350)
    cmds.setAttr('imagePlaneShape1.depth', 2)
    cmds.setAttr((myCams[0] + '.nearClipPlane'), 1.0)
    cmds.setAttr((myCams[0] + '.farClipPlane'), 10000000)
    clipPlane()
    addDisLayer()


def alphaGain():
    gScale = cmds.floatSliderGrp(alGain, pre=2, ss=0.01, q=True, value=True)
    cmds.setAttr('imagePlaneShape1.alphaGain', gScale)


def camLocScale():
    cScale = cmds.floatSliderGrp(camLC, q=True, value=True)
    cmds.setAttr(myCams[0] + '.locatorScale', cScale)


def addDisLayer():
    cmds.createDisplayLayer(name='Camera_#', nr=True)
    cmds.setAttr('Camera*.color', 6)


def createMT():
    sTime = int(cmds.playbackOptions(q=True, min=True))
    eTime = int(cmds.playbackOptions(q=True, max=True))
    # sel = cmds.ls(sl=True)
    cmds.snapshot(tCams, st=sTime, et=eTime, mt=True, n='MotionTrail_#')
    cmds.editRenderLayerMembers('Perspective', 'MotionTrail*')


def addRenLayer():
    cmds.createRenderLayer(tCams, name='geo', nr=True)
    cmds.createRenderLayer(tCams, name='Cone', nr=True)
    cmds.createRenderLayer(tCams, name='Perspective', nr=True)


# all functions declare
def textToSpacedHex(inputText):
    out = []
    for c in inputText:
        hx = f"{ord(c):x}"
        out.append(hx)
    return ' '.join(out)


def numberGenerator(number):
    hexString = textToSpacedHex(number)
    mel.eval('CreatePolygonType')
    t3d_trans = cmds.ls(sl=True)[0]
    t3d_node = cmds.listConnections('%s.message' % t3d_trans)[0]
    t3d_extrude = cmds.listConnections('%s.outputMesh' % t3d_node)[0]
    cmds.setAttr('%s.textInput' % t3d_node, hexString, type='string')
    cmds.setAttr('%s.enableExtrusion' % t3d_extrude, 0)
    cmds.setAttr("%s.fontSize" % t3d_node, 1.5)
    cmds.setAttr("%s.tracking" % t3d_node, -10)
    cmds.setAttr("%s.alignmentMode" % t3d_node, 2)

    return t3d_trans


def createCone():
    mySelection = cmds.ls(selection=True, fl=True)
    groupCones = cmds.group(empty=True, name="cone_grp_#")

    for sel in mySelection:
        selPos = cmds.xform(sel, q=True, ws=True, t=True)
        # create cone
        coneTip = cmds.polyCone(sx=4, sc=1, h=3)
        cmds.xform(coneTip, os=True, piv=(0, 1.5, 0))
        cmds.move(0, -1.5, 0)
        cmds.rotate(0, 0, 180)
        cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
        # create number and position it, use numbering from locator selection instead
        coneNumber = [x for x in re.findall(r'-?\d+\.?\d*', sel)][-1]
        t3d_trans = numberGenerator(coneNumber)
        cmds.move(-0.17, 3, 0, t3d_trans)
        # combine cone and number
        coneNo = cmds.polyUnite(t3d_trans, coneTip[0], cp=False, n='cone_' + coneNumber)
        cmds.delete(ch=True)

        cmds.move(selPos[0], selPos[1], selPos[2], coneNo[0])
        cmds.parent(coneNo[0], groupCones)
        cmds.select(groupCones, hi=True)
        cmds.select('cone_grp*', d=True)
        # cmds.createDisplayLayer(name='cone_group#', nr=True)
        # cmds.setAttr('cone_group*.color', 13)
        # cmds.editRenderLayerMembers('Cone', 'cone_grp*')


def poly_cam():
    sel = cmds.ls(sl=1)
    startTime = cmds.playbackOptions(q=True, minTime=True)
    endTime = cmds.playbackOptions(q=True, maxTime=True)
    polyCam = cmds.file("G:\pythonScript\OBJ\camera.obj", i=True, returnNewNodes=True)[0]
    polyCamLoc = cmds.spaceLocator(name="polyCamLocator")[0]
    cmds.parent('polyCamera', 'polyCamLocator')

    for obj in sel:
        newCon = cmds.parentConstraint(obj, polyCamLoc, mo=0)
        # bake animation to locator#
        cmds.bakeResults(polyCamLoc, time=(startTime, endTime))
        cmds.delete(cn=True)


def poly_man():
    cmds.file("G:\pythonScript\OBJ\Male6Foot.obj", i=True, returnNewNodes=True)[0]


def coneSize():
    coneScale = cmds.floatSliderGrp(coneS, q=True, value=True)
    cmds.scale(coneScale, coneScale, coneScale)


def addToLayer():
    cmds.createDisplayLayer(name='cone_group#', nr=True)
    cmds.setAttr('cone_group*.color', 13)
    cmds.editRenderLayerMembers('Cone', 'cone_grp*')


# if UI window  already exists will close and re-open #
if cmds.window("camwindow", q=True, exists=True):
    cmds.deleteUI("camwindow")

camWindow = cmds.window("camwindow", t='Camera Magic v3.04262024', w=300, h=500)

# grab camera attribute and creat variables#
allCams = cmds.ls(type=('camera'), l=True)
Cams = [camera for camera in allCams if
        cmds.camera(cmds.listRelatives(camera, parent=True)[0], startupCamera=True, q=True)]
myCams = list(set(allCams) - set(Cams))
tCams = cmds.listRelatives(myCams, parent=True, fullPath=True)

cmds.columnLayout(adj=True)
cmds.text("***First select Camera***")
cmds.separator(h=20)

selCamText = cmds.textField('Select Camera', w=200)
cmds.button(label='Load Camera', w=50, c='set_camText()')

cmds.text('Set Camera for Render')

cmds.rowLayout(numberOfColumns=6, cw=(100, 100))
# cmds.gridLayout(numberOfColumns=3, cellWidthHeight=(100, 30))

cmds.button(label='Default', w=100, c='defaultCam()')
cmds.button(label='AlphaGain', w=100, c='renCam()')
cmds.button(label='RGBA>RGB', w=100, c='rgbMode()')
cmds.button(label='LookThrough', w=100, c='lookThrough()')
cmds.button(label='clippingPlane', w=100, c='setClipPlanes()')
cmds.button(label='Frustum', w=100, c='cameraFrustum()')

cmds.setParent('..')
cmds.separator(h=20)

# cmds.text('Alpha Gain')
alGain = cmds.floatSliderGrp(label="Alpha Gain", min=0, max=1, pre=2, ss=0.01, field=True, value=0.85, dc='alphaGain()')

cmds.separator(h=20)
camLC = cmds.floatSliderGrp(label="Camera Locator Scale", min=1, max=50, field=True, value=1, dc='camLocScale()')
cmds.separator(h=20)

cmds.button(label='Create 3 Render Layers', c='addRenLayer()')
cmds.separator(h=20)
cmds.button(label='Create Motion Trail', c='createMT()')
cmds.separator(h=20)
cmds.text("***Select Locators***")
cmds.separator(h=20)
cmds.button(label="Create Cone Group", c="createCone()")
cmds.separator(h=20)
coneS = cmds.floatSliderGrp(label="Cones Size", min=0, max=20, field=True, value=1, dc='coneSize()')
cmds.separator(h=20)
cmds.button(label="Add Cones to Layer", c="addToLayer()")
cmds.separator(h=20)
cmds.gridLayout(numberOfColumns=6, cellWidthHeight=(102, 50))
cmds.button(label='Multi Cut', command='multi_cut()')
cmds.button(label='Insert Loop Tool', command='insert_loop_tool()')
cmds.button(label='Freeze Transform', command='freeze_transform()')
cmds.button(label='Delete History', command='delete_history()')
cmds.button(label='Center Pivot', command='center_pivot()')
cmds.button(label='loc2Pivot', command='create_locator_at_pivot()')
cmds.button(label='Constraint', command='create_parent_constraint()')
cmds.button(label='Constraint(MO)', command='create_parent_constraintMO()')
cmds.button(label='Bake it!!', command='bake_simulation()')
cmds.button(label="Reverse Normal", command='reverse_normals()')
cmds.button(label="PolyCam", command='poly_cam()')
cmds.button(label="6ft_man", command='poly_man()')
cmds.button(label="loc Control", command='locControl()')

# cmds.separator(h=20)
# cmds.button(label="Add to Render Layer", c="addRenLayer()")
# cmds.separator(h=20)


cmds.showWindow(camWindow)

