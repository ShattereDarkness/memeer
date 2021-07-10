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
sid = int(input ("Enter Subject ID (INTEGER): "))
print ("Enter Range of action files to preview (ex. 20, 28). Leave blank for 1, 1000")
nrange = str(input ("Enter Range: "))
if nrange == '': nrange = '1,200'
if ',' in nrange: nidf, nidl = int(nrange.split(',')[0].strip()), int(nrange.split(',')[1].strip())
else: nidf, nidl = int(nrange), int(nrange)+1
actdir = str(input ("Enter action directory (default is 'actions'): "))
if actdir == '': actdir = 'actions'
for nid in range (nidf, nidl):
    fname = "basemodels/"+actdir+"/A20GFLC-A20g%02d_%02d.egg" %(sid, nid)
    print ("fname", fname)
    if not path.isfile(fname): continue
    print ("Working for file: ", fname)
#    actor = Actor('lady_mannequin.bam', {'anim': fname})
    actor = Actor('basemodels/egg files/basewoman.bam', {'anim': fname})
    ac = actor.getAnimControl('anim')
    animlen = ac.getNumFrames()
    animdat = {'object': actor, 'modegg': 'A05GFEA', 'fname': fname, 'start': gframe, 'end': gframe+animlen, 'finally': 'destroy',
                   'pos': {'inuse': 0, 'start': [], 'end': [], 'current': [], 'delta': [], 'frames': 0},
                   'hpr': {'inuse': 0, 'start': [], 'end': [], 'current': [], 'delta': [], 'frames': 0},
                   'act': {'inuse': 1, 'start': 0, 'end': animlen, 'current': 0, 'delta': 1, 'frames': animlen}
              }
    gframe = gframe + animlen
    tstat.append (animdat)

ShowBase()
scene = loader.loadModel("openmodels/BeachTerrain")
scene.reparentTo(render)
base.disableMouse()
camera.setPos(0, -60, 12)
camera.setHpr(0, 0, 0)
textObject = OnscreenText(text=" ", pos=(-1.2, 0.9), scale=0.07, align=0)
taskMgr.add(defaultTask, "defaultTask")
base.run()