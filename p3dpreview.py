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
from pandac.PandaModules import ClockObject
from panda3d.core import LineSegs
from panda3d.core import NodePath

import time
import json

loadlist = []
screentx = []
execoutp = []

def newmodel (scene):
	if scene['basic']['p3dfunc'] not in ['loadmodel', 'loadactor', 'camera']: return -1
	modid = checkformodel (scene['basic']['file'])
	if modid == -1:
		if scene['basic']['p3dfunc'] == 'loadactor':
			model = Actor(scene['basic']['file'], scene['basic']['acts'])
			model.makeSubpart("legs", ["LHipJoint", "RHipJoint"])
			model.makeSubpart("hand", ["LeftShoulder", "RightShoulder"])
			model.makeSubpart("head", ["Neck"], ["LHipJoint", "RHipJoint"])
		else: model = loader.loadModel(scene['basic']['file'])
		model.reparentTo(render)
		loadlist.append({'file': scene['basic']['file'], 'model': model, 'post': [0,0,0,0,0,0,1,1,1], 'sttmt': []})
		modid = len(loadlist)-1
	return modid

def loadObject (modid = 0):
	modfile = rushobjlst[modid]
	if 'acts' in modfile:
		model = Actor(modfile['file'], modfile['acts'])
		for jname, jparts in modfile['joint'].items():
			model.makeSubpart(jname, jparts['include'], jparts['exclude'])
	elif modfile['file'] == 'line':
		line = LineSegs()
	else:
		model = loader.loadModel(modfile['file'])
	model.reparentTo(render)
	rushobjlst['p3dmod'] = model
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
	lines.moveTo(pfrom)
	lines.drawTo(pupto)
	lines.setThickness(1)
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

with open('temp_rushframes.js') as lujs: animes = json.load(lujs)
animes, fframe, rushobjlst, lastindx = animes['animes'], animes['fframe'], animes['rushobjlst'], animes['lastindx']
basedir, winsize, fps, preview = animes['basedir'], animes['winsize'], animes['fps'], animes['preview']
props = WindowProperties( )
props.setTitle("For Preview (Starting from frame " + str(fframe) + ")")
winw, winh = winsize[0], winsize[1] 
props = WindowProperties() 
props.setSize(winw, winh) 

ShowBase()
base.disableMouse()
camera.setPos(0, -120, 0)
camera.setHpr(0, 0, 0)
statements = OnscreenText(text=" ", pos=(-1.2, 0.9), scale=0.08, align=0, wordwrap=30)
if preview == 1: textbasics = OnscreenText(text=" ", pos=(-1.2, -0.95), scale=0.08, align=0, wordwrap=30)

def defaultTask(task):
	if preview == 1: textbasics.text = 'Frame#: '+str(frindex+task.frame)
	if lastindx <= task.frame:
		return exit(1)
	if str(task.frame) not in animes: return Task.cont
	anims = animes[str(task.frame)]
	print (anims)
	for anim in  anims:
		print("anims", anims)
		if anim['what'] = 'loadobj': loadObject (modid = anim['model'])
		if anim['what'] = 'moveobj': moveObject (modid = anim['model'], pos = anim['pos'])
		if anim['what'] = 'poseobj': poseObject (modid = anim['model'], action = anim['action'], poseid = anim['poseid'])
		if anim['what'] = 'lineseg': linesegObj (modid = anim['model'], pfrom = anim['from'], pupto = anim['upto'])
	return Task.cont


base.win.requestProperties(props) 
loadlist.append({'file': 'camera', 'model': base.camera, 'post': [0, -120, 0, 0, 0, 0, 1, 1, 1]})
taskMgr.add(defaultTask, "defaultTask")
namePrefix = basedir + "/demo/rushes/temp"
print("namePrefix", namePrefix)
base.movie(namePrefix=namePrefix, duration=6000, fps=fps, format='png')
base.run()