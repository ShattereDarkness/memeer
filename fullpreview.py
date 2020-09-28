import os.path
from os import path
import sys

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from direct.gui.OnscreenText import OnscreenText

def defaultTask(task):
    gframe = task.frame
    ftext = "GFrame: " + str(task.frame) + "\n"
    inplay = 0
    for anim in tstat:
        if gframe > anim['start'] and gframe < anim['end']:
            if 'fname' in anim and anim['act']['inuse'] == 1:
                if anim['act']['current'] == 0: anim['object'].reparentTo(render)
                ftext = ftext + "Animation: " + anim['fname'] + "\n"
                anim['object'].pose('anim', anim['act']['start']+anim['act']['current'])
                inplay = 1
                anim['act']['current'] = anim['act']['current'] + anim['act']['delta']
                ftext = ftext + "LFrame: " + str(anim['act']['current']) + "/" + str(anim['act']['end'])
                textObject.text = ftext
                if anim['act']['current'] > anim['act']['end']:
                    print ("Warning: current frame > end frame")
                    anim['act']['current'] = anim['act']['end']
        if gframe > anim['end']:
            if anim['finally'] == 'destroy':
                anim['object'].cleanup ()
    if inplay == 0 and gframe > 4: sys.exit()
    return Task.cont

tstat = []
gframe = 0
for sid in range (0, 2):
    for nid in range (0, 2):
        fname = "A20GFLC-A20g%02d_%02d" %(sid, nid)
        if not path.isfile(fname+".egg"): continue
        print ("Working for file: ", fname+".egg")
        actor = Actor('A20GFLC', {'anim': fname})
        ac = actor.getAnimControl('anim')
        animlen = ac.getNumFrames()
        animdat = {'object': actor, 'fname': fname, 'start': gframe, 'end': gframe+animlen, 'finally': 'destroy',
                       'pos': {'inuse': 0, 'start': [], 'end': [], 'current': [], 'delta': [], 'frames': 0},
                       'hpr': {'inuse': 0, 'start': [], 'end': [], 'current': [], 'delta': [], 'frames': 0},
                       'act': {'inuse': 1, 'start': 0, 'end': animlen, 'current': 0, 'delta': 1, 'frames': animlen}
                  }
        gframe = gframe + animlen
        tstat.append (animdat)

ShowBase()
scene = loader.loadModel("BeachTerrain")
scene.reparentTo(render)
base.disableMouse()
camera.setPos(0, -120, 10)
camera.setHpr(0, 0, 0)
textObject = OnscreenText(text="0123454667\nABCDEFGHIJKLmNOPQR", pos=(-1.2, 0.9), scale=0.07, align=0)
taskMgr.add(defaultTask, "defaultTask")
base.movie(namePrefix='fullreview/fr', duration=10000, fps=6, format='png')
base.run()