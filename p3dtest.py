from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import loadPrcFileData
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from direct.gui.DirectGui import *
from panda3d.core import WindowProperties
from direct.interval.ActorInterval import ActorInterval
from panda3d.core import LineSegs
from panda3d.core import NodePath

actdet = {}
actsets = []
outdata = []


def defaultTask(task):
	#print(actor.getPos())
	return Task.cont
	
actions = {}
modelp = 'testgltf.bam'
ShowBase()

actor = Actor('humans/bam files/lady_greek_01.bam', {'act': 'basemodel/nactions/A20GFLC-A20g01_01'})
#model=loader.loadModel(modelp)
actor.reparentTo(render)
actor.setScale(4,4,4)
actor.play('act')
#actor.reparentTo(render)
#actor.setPos(200,200,0)
taskMgr.add(defaultTask, "defaultTask")
base.run()