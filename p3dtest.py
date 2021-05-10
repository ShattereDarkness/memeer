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
from direct.interval.ActorInterval import ActorInterval

import time
import json

from panda3d.core import LineSegs
from panda3d.core import NodePath
# from direct.directbase import DirectStart
# import direct.directtools.DirectSelection

model = {}
def defaultTask(task):
	if task.frame == 0:
		actor = Actor("demo/model/lady", {"run": "demo/model/action/lady__run"})
		actor.setPos(0, 0, 0)
		actor.reparentTo(render)
		myInterval = actor.actorInterval ("run", loop = 1, startFrame = 1, endFrame = 60)
		myInterval.start()
	return Task.cont

ShowBase()
base.disableMouse()
camera.setPos(0, -120, 0)
camera.setHpr(0, 0, 0)

taskMgr.add(defaultTask, "defaultTask")
base.run()