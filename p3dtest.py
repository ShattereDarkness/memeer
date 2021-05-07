from panda3d.core import WindowProperties
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
from pandac.PandaModules import ClockObject

import time
import json

from panda3d.core import LineSegs
from panda3d.core import NodePath
# from direct.directbase import DirectStart
# import direct.directtools.DirectSelection

lines = LineSegs()
def defaultTask(task):
	ix = task.frame
	lines.moveTo(ix, 1, 0)
	lines.drawTo(ix, 1, 2)
	lines.setThickness(ix*2)
	print("ix and lines", ix, lines)
	node = lines.create()
	np = NodePath(node)
	np.reparentTo(render)
	return Task.cont

ShowBase()
base.disableMouse()
camera.setPos(0, -420, 0)
camera.setHpr(0, 0, 0)

taskMgr.add(defaultTask, "defaultTask")
base.run()