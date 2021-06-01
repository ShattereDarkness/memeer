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
from direct.interval.ActorInterval import ActorInterval
from panda3d.core import LineSegs
from panda3d.core import NodePath
from panda3d.core import OrthographicLens
from panda3d.core import LColor

import time
import json

loadlist = []
screentx = []
execoutp = []

def loadObject (modid = 0, fullanim = {}):
    modfile = rushobjlst[modid]
    print ("modfile", modfile)
    if modfile['acts'] != {}:
        model = Actor(modfile['filenm'], modfile['action'])
        for jname, jparts in modfile['joint'].items():
            model.makeSubpart(jname, jparts['include'], jparts['exclude'])
    elif modfile['file'] not in ['line']:
        model = loader.loadModel(modfile['filenm'])
        ##model.find('**/+SequenceNode').node().play() - enable for like "play bird loading once"?
    else: return 1
    model.reparentTo(render)
    if 'posnow' in fullanim and 'pos' in fullanim and fullanim['posnow'] == 1:
        if len(fullanim['pos']) > 2: model.setPos(float(fullanim['pos'][0]), float(fullanim['pos'][1]), float(fullanim['pos'][2]))
        if len(fullanim['pos']) > 5: model.setHpr(float(fullanim['pos'][3]), float(fullanim['pos'][4]), float(fullanim['pos'][5]))
        if len(fullanim['pos']) > 8: model.setScale(float(fullanim['pos'][6]), float(fullanim['pos'][7]), float(fullanim['pos'][8]))
    rushobjlst[modid]['p3dmod'] = model
    return 1

def moveObject (modid = 0, pos = [0, 0, 0, 0, 0, 0, 1, 1, 1]):
    model = rushobjlst[modid]['p3dmod']
    model.setPos(float(pos[0]), float(pos[1]), float(pos[2]))
    if len(pos) < 4: return 1
    model.setHpr(float(pos[3]), float(pos[4]), float(pos[5]))
    if modid == 0 or len(pos) < 7: return 1
    model.setScale(float(pos[6]), float(pos[7]), float(pos[8]))
    return 1

def poseObject (modid = 0, action = '', poseid = 1):
    model = rushobjlst[modid]['p3dmod']
    if 'bpart' not in rushobjlst[modid]: model.pose (action, poseid)
    else: model.pose (action, poseid, partName = rushobjlst[modid]['bpart'])
    return 1

def linesegObj (modid = 0, pfrom = [0, 0, 0], pupto = [0, 0, 0]):
    lines.moveTo(pfrom[0], pfrom[1], pfrom[2])
    lines.drawTo(pupto[0], pupto[1], pupto[2])
    node = lines.create()
    np = NodePath(node)
    np.reparentTo(render)
    return 1

def subtitling (modid = 0, text = ''):
    return 1

def setscrtext (statements, text, lineid):
    if lineid > -1:
        screentx.append({'text': text, 'lineid': lineid})
    txtstr = ''
    for scrtx in screentx: txtstr = txtstr + scrtx['text'] + "\n"
    txtstr.strip()
    statements.text = txtstr
    return 1

with open('temp_rushframes.js') as lujs: animdat = json.load(lujs)
animes, fframe, rushobjlst, lastindx = animdat['animes'], animdat['fframe'], animdat['rushobjlst'], animdat['lastindx']
basedir, winsize, fps, preview = animdat['basedir'], animdat['winsize'], animdat['fps'], animdat['preview']
props = WindowProperties( )
props.setTitle("For Preview (Starting from frame " + str(fframe) + ")")
winw, winh = winsize[0], winsize[1] 
props.setSize(winw, winh) 

ShowBase()
base.disableMouse()
camera.setPos(0, -120, 0)
camera.setHpr(0, 0, 0)
statements = OnscreenText(text=" ", pos=(-1.0, 0.9), scale=0.08, align=0, wordwrap=30)
if preview == 1: textbasics = OnscreenText(text=" ", pos=(-1.0, -0.95), scale=0.08, align=0, wordwrap=30)
def defaultTask(task):
    if preview == 1: textbasics.text = 'Frame#: '+str(fframe+task.frame-1)
    if lastindx <= task.frame:
        return exit(1)
    if str(task.frame) not in animes: return Task.cont
    anims = animes[str(task.frame)]
    print ("anims", anims)
    for anim in  anims:
        if anim['what'] == 'loadobj': loadObject (modid = anim['model'], fullanim = anim)
        if anim['what'] == 'moveobj': moveObject (modid = anim['model'], pos = anim['pos'])
        if anim['what'] == 'poseobj': poseObject (modid = anim['model'], action = anim['action'], poseid = anim['poseid'])
        if anim['what'] == 'lineseg': linesegObj (modid = anim['model'], pfrom = anim['from'], pupto = anim['upto'])
    return Task.cont

lines = LineSegs()
lines.setColor(0,0,0,1)
lines.setThickness(1)
base.win.requestProperties(props) 
loadlist.append({'file': 'camera', 'model': base.camera, 'post': [0, -120, 0, 0, 0, 0, 1, 1, 1]})
taskMgr.add(defaultTask, "defaultTask")
namePrefix = "demo/rushes/temp/rush_"
print("namePrefix", namePrefix)
base.movie(namePrefix=namePrefix, duration=100, fps=fps, format='png')
base.run()