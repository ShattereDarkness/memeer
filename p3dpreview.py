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

loadlist = []
screentx = []
execoutp = []

def checkformodel (modfile):
	for mno, model in enumerate(loadlist):
		if model['file'] == modfile: return mno
	return -1

def setactorpose (modid, action, poseid):
	loadlist[modid]['model'].pose (action, poseid)
	return 1

def disablemodel (lineid, statements):
	global screentx
	screentx = list(filter(lambda x : x['lineid'] != lineid, screentx))
	setscrtext (statements, '', -1)

def setscrtext (statements, text, lineid):
	if lineid > -1:
		screentx.append({'text': text, 'lineid': lineid})
	txtstr = ''
	for scrtx in screentx: txtstr = txtstr + scrtx['text'] + "\n"
	txtstr.strip()
	statements.text = txtstr
	return 1

def setmodelpost (modid, poshpr):
	loadlist[modid]['model'].setPos(float(poshpr[0]), float(poshpr[1]), float(poshpr[2]))
	loadlist[modid]['model'].setHpr(float(poshpr[3]), float(poshpr[4]), float(poshpr[5]))
	if modid > 0:
		loadlist[modid]['model'].setScale(float(poshpr[6]), float(poshpr[7]), float(poshpr[8]))
	return 1

def newmodel (scene):
	if scene['basic']['p3dfunc'] not in ['loadmodel', 'loadactor', 'camerapos']: return -1
	modid = checkformodel (scene['basic']['file'])
	if modid == -1:
		if scene['basic']['p3dfunc'] == 'loadactor': model = Actor(scene['basic']['file'], scene['basic']['acts'])
		else: model = loader.loadModel(scene['basic']['file'])
		model.reparentTo(render)
		loadlist.append({'file': scene['basic']['file'], 'model': model, 'post': [0,0,0,0,0,0,1,1,1], 'sttmt': []})
		modid = len(loadlist)-1
	return modid

with open('portfolio/rushes/serial.js') as lujs: serealized = json.load(lujs)
serial, frindex, inprod, imgdest = serealized['serial'], serealized['frindex'], serealized['inprod'], serealized['imgdest']
props = WindowProperties( )
props.setTitle("For Preview")
ShowBase()
base.disableMouse()
camera.setPos(0, -120, 0)
camera.setHpr(0, 0, 0)
statements = OnscreenText(text=" ", pos=(-1.2, 0.9), scale=0.08, align=0, wordwrap=30)
textbasics = OnscreenText(text=" ", pos=(-1.2, -0.95), scale=0.08, align=0, wordwrap=30)

def defaultTask(task):
	#print('Current frame: '+str(task.frame))
	textbasics.text = 'Frame#: '+str(frindex+task.frame)
	scenes = serial[task.frame]
	#print (scenes)
	for scene in  scenes:
		if scene['basic']['p3dfunc'] == 'exitall':
			return exit(1)
		modid = newmodel (scene)
		if 'post' in scene['addon']: setmodelpost (modid, scene['addon']['post'])
		if 'sttmt' in scene['addon']: setscrtext (statements, scene['addon']['sttmt'], scene['basic']['lineid'])
		if 'pose' in scene['addon'] and 'pose' in scene['addon']['pose']:
			setactorpose (modid, scene['basic']['action'], scene['addon']['pose']['pose'])
		if 'disable' in scene['addon']: disablemodel (scene['basic']['lineid'], statements)
	return Task.cont

loadlist.append({'file': 'camera', 'model': base.camera, 'post': [0, -120, 10,0, 0, 0, 1, 1, 1]})
taskMgr.add(defaultTask, "defaultTask")
namePrefix = serealized['imgdest']
base.win.requestProperties( props )
base.movie(namePrefix=namePrefix, duration=1000, fps=24, format='png')
base.run()