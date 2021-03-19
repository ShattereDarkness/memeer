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
import time
import json
from pandac.PandaModules import ClockObject

props = WindowProperties( )
props.setTitle("For Preview")
ShowBase()
base.disableMouse()
camera.setPos(0, -120, 0)
camera.setHpr(0, 0, 0)

actor = Actor('models/human/A20GFLC', {
	'legs': 'models/human/A20GFLC-A20g77_28',
	'hand': 'models/human/A20GFLC-A20g78_28', 
	'head': 'models/human/A20GFLC-A20g80_28'
})
actor.setScale(0.5, 0.5, 0.5)
actor.reparentTo(render)
actor.makeSubpart("leg", ["LHipJoint", "RHipJoint"])
actor.makeSubpart("hands", ["LeftShoulder", "RightShoulder"])
actor.makeSubpart("torso", ["Neck"], ["LHipJoint", "RHipJoint"])
actor.loop("legs", partName="leg")
actor.loop("head", partName="torso")
actor.loop("hand", partName="hands")

def defaultTask(task):
	return Task.cont

taskMgr.add(defaultTask, "defaultTask")
base.win.requestProperties( props )
base.movie(namePrefix="dd/dd", duration=1000, fps=24, format='png')
base.run()