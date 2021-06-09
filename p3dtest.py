import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.filter.CommonFilters import CommonFilters
alight = AmbientLight('amibent') 
alight.setColor(VBase4(3, 3, 3, 1)) 
alnp = render.attachNewNode(alight)
plight = PointLight('point')
plight.setColor(VBase4(0.8, 0.8, 0.8, 1))
plnp = render.attachNewNode(plight)
plnp.setPos(0, 0, 1)
render.setLight(alnp)
pnda = loader.loadModel("panda")
pnda.reparentTo(plnp)
pnda2 = loader.loadModel("panda")
pnda2.reparentTo(render)
pnda2.setPos(0,0,-10)
base.camera.lookAt(pnda)
fltr = CommonFilters(base.win, base.cam)
fltr.setBloom()
#fltr.setGammaAdjust(1.5)
#fltr.setAmbientOcclusion()
#fltr.setBlurSharpen(2)
#fltr.setInverted()
#fltr.setCartoonInk(separation=1, color=(0, 0, 0, 1))
#fltr.setVolumetricLighting(pnda, 32, 5.0, 0.1, 0.1)
run()

# from direct.showbase.ShowBase import ShowBase
# from panda3d.core import Plane, Vec3, Point3, CardMaker
# from panda3d.core import WindowProperties
# from panda3d.core import LPoint2f

# class YourClass(ShowBase):
  # def __init__(self):
    # ShowBase.__init__(self)
    # self.disableMouse()
    # self.camera.setPos(0, 0, -120)
    # self.camera.lookAt(0, 0, 0)
    # z = 0
    # self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, z))
    # self.model = loader.loadModel("jack")
    # self.model.reparentTo(render)
    # cm = CardMaker("blah")
    # cm.setFrame(-100, 100, -100, 100)
    # render.attachNewNode(cm.generate()).lookAt(0, 0, -1)
    # taskMgr.add(self.__getMousePos, "_YourClass__getMousePos")
  
  # def __getMousePos(self, task):
    # if base.mouseWatcherNode.hasMouse():
      # mpos = base.mouseWatcherNode.getMouse()
    # for mpos in (LPoint2f(1, 1), LPoint2f(0, 0), LPoint2f(1, 0), LPoint2f(0, 1)):
      # pos3d = Point3()
      # nearPoint = Point3()
      # farPoint = Point3()
      # base.camLens.extrude(mpos, nearPoint, farPoint)
      # if self.plane.intersectsLine(pos3d,
          # render.getRelativePoint(camera, nearPoint),
          # render.getRelativePoint(camera, farPoint)):
        # print ("Mouse ray intersects ground plane", mpos, " at ", pos3d)
        # self.model.setPos(render, pos3d)
    # exit(1)
    # return task.done

# YourClass()
# props = WindowProperties( )
# props.setSize(900, 600) 
# base.win.requestProperties(props) 
# base.taskMgr.run()
# from direct.showbase.ShowBase import ShowBase
# from direct.task import Task
# from direct.actor.Actor import Actor
# from direct.interval.IntervalGlobal import Sequence
# from panda3d.core import Point3
# from direct.gui.OnscreenText import OnscreenText
# from panda3d.core import loadPrcFileData
# from direct.gui.OnscreenImage import OnscreenImage
# from panda3d.core import TransparencyAttrib
# from direct.gui.DirectGui import *
# from panda3d.core import WindowProperties
# from direct.interval.ActorInterval import ActorInterval
# from panda3d.core import LineSegs
# from panda3d.core import NodePath

# actdet = {}
# actsets = []
# outdata = []


# def defaultTask(task):
	# #print(actor.getPos())
	# return Task.cont
	
# actions = {}
# modelp = 'testgltf.bam'
# ShowBase()

# actor = Actor('humans/bam files/lady_greek_01.bam', {'act': 'basemodel/nactions/A20GFLC-A20g01_01'})
# #model=loader.loadModel(modelp)
# actor.reparentTo(render)
# actor.setScale(4,4,4)
# actor.play('act')
# #actor.reparentTo(render)
# #actor.setPos(200,200,0)
# taskMgr.add(defaultTask, "defaultTask")
# base.run()