import os.path
from os import path
import sys
from pprint import pprint

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath

from panda3d.core import loadPrcFileData
loadPrcFileData("", "win-size 640 480")

def defaultTask(task):
	return Task.cont

ShowBase()
base.disableMouse()
camera.setPos(0, -100, 0)
camera.setHpr(0, 0, 0)
model = loader.loadModel('portfolio/model/narrator')
model.setPos(36,0,27)
model.reparentTo(render)
base.run()