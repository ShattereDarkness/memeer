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

from panda3d.core import loadPrcFileData
loadPrcFileData("", "win-size 800 450")

def defaultTask(task):
    global lastplay
    gframe = task.frame
    ftext = "GFrame: " + str(task.frame) + "\n"
    for anim in tstat:
        if gframe > anim['start'] and gframe < anim['end']:
            if 'fname' in anim and anim['act']['inuse'] == 1:
                if anim['act']['current'] == 0: anim['object'].reparentTo(render)
                ftext = ftext + "Animation: " + anim['fname'] + "\n"
                anim['object'].pose('anim', anim['act']['start']+anim['act']['current'])
                lastplay = gframe
                anim['act']['current'] = anim['act']['current'] + anim['act']['delta']
                ftext = ftext + "LFrame: " + str(anim['act']['current']) + "/" + str(anim['act']['end'])
                textObject.text = ftext
                if anim['act']['current'] > anim['act']['end']:
                    print ("Warning: current frame > end frame")
                    anim['act']['current'] = anim['act']['end']
        if gframe > anim['end']:
            if anim['finally'] == 'destroy':
                anim['object'].cleanup ()
    if gframe - lastplay > 20: sys.exit()
    return Task.cont

tstat = []
gframe = 0
lastplay = 0
sid=13
for nid in range (26, 29):
    fname = "basemodel/actions/A20GFLC-A20g%02d_%02d" %(sid, nid)
    print ("fname", fname)
    if not path.isfile(fname+".egg"): continue
    print ("Working for file: ", fname+".egg")
    actor = Actor('humans/bam files/lady_mini_01.bam', {'anim': fname})
    ac = actor.getAnimControl('anim')
    animlen = ac.getNumFrames()
    animdat = {'object': actor, 'modegg': 'A05GFEA', 'fname': fname, 'start': gframe, 'end': gframe+animlen, 'finally': 'destroy',
                   'pos': {'inuse': 0, 'start': [], 'end': [], 'current': [], 'delta': [], 'frames': 0},
                   'hpr': {'inuse': 0, 'start': [], 'end': [], 'current': [], 'delta': [], 'frames': 0},
                   'act': {'inuse': 1, 'start': 0, 'end': animlen, 'current': 0, 'delta': 1, 'frames': animlen}
              }
    gframe = gframe + animlen
    tstat.append (animdat)
    print ("tstat", tstat)

ShowBase()
base.disableMouse()
camera.setPos(0, -120, 10)
camera.setHpr(0, 0, 0)
textObject = OnscreenText(text=" ", pos=(-1.2, 0.9), scale=0.07, align=0)
taskMgr.add(defaultTask, "defaultTask")
# namePrefix = "fullreview/fr_sid%03d" %(sid)
# base.movie(namePrefix=namePrefix, duration=100000, fps=24, format='png')
base.run()