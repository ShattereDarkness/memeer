from direct.showbase.ShowBase import ShowBase
from panda3d.core import Plane, Vec3, Point3, CardMaker, LPoint2f
from panda3d.core import WindowProperties
from panda3d.core import LPoint2f
import sys
count = 0

def print_message (poslst):
    print ("Checking for \n\tCenter as ", bcenter, "\n\tCamera position as ", campos, "\n\tScreen Size as ", scrsize)
    print ("Top left coordinates:", list(poslst[0]))
    print ("Top right coordinates:", list(poslst[1]))
    print ("Bottom right coordinates:", list(poslst[2]))
    print ("Bottom left coordinates:", list(poslst[3]))
    maxlen = ((poslst[0][0]-poslst[1][0])**2+(poslst[0][1]-poslst[1][1])**2+(poslst[0][2]-poslst[1][2])**2)**0.5
    maxwid = ((poslst[1][0]-poslst[2][0])**2+(poslst[1][1]-poslst[2][1])**2+(poslst[1][2]-poslst[2][2])**2)**0.5
    print ("Maximum visible object length: ", str(maxlen))
    print ("Maximum visible object width: ", str(maxwid))

class YourClass(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.camera.setPos(campos[0], campos[1], campos[2])
        self.camera.lookAt(bcenter[0], bcenter[1], bcenter[2])
        self.plane = Plane(Vec3(pvector[0], pvector[1], pvector[2]), Point3(bcenter[0], bcenter[1], bcenter[2]))
        taskMgr.add(self.__getMousePos, "_YourClass__getMousePos")
        
    def __getMousePos(self, task):
        poslst = []
        for mpos in (LPoint2f(-1, -1), LPoint2f(1, -1), LPoint2f(1, 1), LPoint2f(-1, 1)):
            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()
            base.camLens.extrude(mpos, nearPoint, farPoint)
            if self.plane.intersectsLine(pos3d, render.getRelativePoint(camera, nearPoint), render.getRelativePoint(camera, farPoint)):
                pass
            poslst.append(pos3d)
            global count
            count = count + 1
        if count > 9:
            print_message (poslst)
            exit()
        else: return task.again

bcenter = list(map(int, str(sys.argv[1]).split(',')))
campos = list(map(int, str(sys.argv[2]).split(',')))
scrsize = list(map(int, str(sys.argv[3]).lower().split(',')))
pvector = [bcenter[0]-campos[0], bcenter[1]-campos[1], bcenter[2]-campos[2]]
YourClass()
props = WindowProperties( )
props.setSize(scrsize[0], scrsize[1])
base.win.requestProperties(props)
base.taskMgr.run()