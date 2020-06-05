# camera and cone tools #
# use at your own risk #
# create 5/29/2020#

# update:6/5/2020 (connect to github)



import maya.cmds as cmds
import maya.mel as mel
import re

# incase no TYPE plugin
if not cmds.pluginInfo('Type', loaded=True, query=True):
    cmds.loadPlugin('Type')

# if UI window  already exists will close and re-open #
if cmds.window(camWindow, q=True, exists=True):
    cmds.deleteUI(camWindow)

allCams = cmds.ls(type=('camera'), l=True)
print
allCams
Cams = [camera for camera in allCams if
        cmds.camera(cmds.listRelatives(camera, parent=True)[0], startupCamera=True, q=True)]
myCams = list(set(allCams) - set(Cams))
tCams = cmds.listRelatives(myCams, parent=True, fullPath=True)
print
myCams

camWindow = cmds.window(t='Camera Magic v1.0', w=300, h=500)

cmds.columnLayout(adj=True)
cmds.text("***First select Camera***")
cmds.separator(h=20)

selCamText = cmds.textField('Select Camera', w=200)
cmds.button(label='Load Camera', w=50, c='set_camText()')

cmds.text('Set Camera for Render')

cmds.rowLayout(numberOfColumns=2, cw=(150, 150))

cmds.button(label='Default', w=200, c='defaultCam()')
cmds.button(label='Render', w=200, c='renCam()')
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
# cmds.separator(h=20)
# cmds.button(label="Add to Render Layer", c="addRenLayer()")
# cmds.separator(h=20)


cmds.showWindow(camWindow)


def set_camText():
    cmds.select(tCams)
    cmds.textField(selCamText, edit=True, text=myCams[0])


def defaultCam():
    cmds.setAttr('imagePlaneShape1.alphaGain', 1)
    cmds.setAttr('imagePlaneShape1.depth', 4500)


def renCam():
    cmds.setAttr('imagePlaneShape1.alphaGain', 0.85)
    cmds.setAttr('imagePlaneShape1.useFrameExtension', 1)
    cmds.setAttr('imagePlaneShape1.frameCache', 350)
    cmds.setAttr('imagePlaneShape1.depth', 2)
    cmds.setAttr((myCams[0] + '.nearClipPlane'), 1.0)
    cmds.setAttr((myCams[0] + '.farClipPlane'), 10000000)
    addDisLayer()


def alphaGain():
    gScale = cmds.floatSliderGrp(alGain, pre=2, ss=0.01, q=True, value=True)
    cmds.setAttr('imagePlaneShape1.alphaGain', gScale)


def fClipPlane():
    cmds.setAttr((myCams[0] + '.nearClipPlane'), 1.0)
    cmds.setAttr((myCams[0] + '.farClipPlane'), 10000000)


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
        hx = c.encode('hex')
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


def coneSize():
    coneScale = cmds.floatSliderGrp(coneS, q=True, value=True)
    print
    coneScale
    cmds.scale(coneScale, coneScale, coneScale)


def addToLayer():
    cmds.createDisplayLayer(name='cone_group#', nr=True)
    cmds.setAttr('cone_group*.color', 13)
    cmds.editRenderLayerMembers('Cone', 'cone_grp*')
