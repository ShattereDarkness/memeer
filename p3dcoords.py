from direct.showbase.ShowBase import ShowBase
from panda3d.core import Plane, Vec3, Point3, CardMaker
from panda3d.core import LPoint2f
import sys
import json
from pathlib import Path
coords = []

class YourClass(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		self.disableMouse()
		self.camera.setPos(0, -120, 0)
		self.camera.lookAt(0, 0, 0)
		y = 0
		self.plane = Plane(Vec3(0, 1, 0), Point3(0, y, 0))
		self.model = loader.loadModel("jack")
		self.model.reparentTo(render)
		cm = CardMaker("blah")
		cm.setFrame(-500, 500, 500, -500)
		render.attachNewNode(cm.generate()).lookAt(0, -1, 0)
		taskMgr.add(self.__getMousePos, "_YourClass__getMousePos")
		
	def __getMousePos(self, task):
		coords = []
		for pixel in pixels:
			mpos = LPoint2f((pixel[0]-250)/250, (250-pixel[1])/250)
			pos3d = Point3()
			nearPoint = Point3()
			farPoint = Point3()
			base.camLens.extrude(mpos, nearPoint, farPoint)
			if self.plane.intersectsLine(pos3d,	render.getRelativePoint(camera, nearPoint),	render.getRelativePoint(camera, farPoint)):
				print ("Mouse ray intersects ground plane at ", mpos, pos3d)
			coords.append([pos3d[0], pos3d[2]])
		coordls['coord'] = coords
		with open(filename, "w") as lujs: json.dump(coordls, lujs)
		exit()

print ('Coordinate List:', str(sys.argv[1]))
filename = str(sys.argv[1])
fromf = Path(filename)
with open(fromf) as lpts: coordls = json.load(lpts)
pixels = coordls['pixel']

print(coords)
YourClass()
base.taskMgr.run()
print("DFSDFSDFASDF")