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
		self.camera.setPos(campos[0], campos[1], campos[2])
		self.camera.lookAt(bcenter[0], bcenter[1], bcenter[2])
		self.plane = Plane(Vec3(pvector[0], pvector[1], pvector[2]), Point3(bcenter[0], bcenter[1], bcenter[2]))
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
				pass
			coords.append([pos3d[0], pos3d[1], pos3d[2]])
		coordls['coord'] = coords
		with open(filename, "w") as lujs: json.dump(coordls, lujs)
		exit()

filename = str(sys.argv[1])
fromf = Path(filename)
with open(fromf) as lpts: coordls = json.load(lpts)
bcenter = list(map(int, coordls['bcenter'].split(',')))
campos = list(map(int, coordls['campos'].split(',')))
pvector = [bcenter[0]-campos[0], bcenter[1]-campos[1], bcenter[2]-campos[2]]
pixels = coordls['pixel']

YourClass()
base.taskMgr.run()