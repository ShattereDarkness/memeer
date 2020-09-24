from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3

# Define a procedure to move the camera.
def spinCameraTask(task):
    angleDegrees = task.time * 6.0
    angleRadians = angleDegrees * (pi / 180.0)
    camera.setPos(20 * sin(angleRadians), -20 * cos(angleRadians), 3)
    camera.setHpr(angleDegrees, 0, 0)
    return Task.cont

ShowBase()
# Load the environment model.
scene = loader.loadModel("models/environment")
# Reparent the model to render.
scene.reparentTo(render)
# Apply scale and position transforms on the model.
scene.setScale(0.25, 0.25, 0.25)
scene.setPos(-8, 42, 0)

# Add the spinCameraTask procedure to the task manager.
taskMgr.add(spinCameraTask, "SpinCameraTask")

# Load and transform the panda actor.
pandaActor = Actor("A20GFLC", {"walk": "A20GFLC-A20g49_02"})
pandaActor.setScale(0.25, 0.25, 0.25)
pandaActor.reparentTo(render)
# Loop its animation.
pandaActor.loop("walk")

base.run()