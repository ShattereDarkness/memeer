import math
import logging
import pprint
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import loadPrcFileData
import logging

g0 = 9.81
pi = 3.1415

fexpand = []
world = {}

def nextscene (act = []):
	act.append(0)
	while len(act) > 1:
		act[-1] = act[-1]+1
		nxtact = list(filter(lambda x : x['act'] == act, fexpand))
		if len(nxtact) > 0: return act
		act.pop()
	return [act[-1]+1]

def setupscenes (lastscene = []):
	nscene = nextscene (act = lastscene)
	world['scene'] = nscene
	sceneid = world['sceneid'] = '-'.join(map(str, nscene))
	logging.error('Next scene is '+sceneid)
	world['scenery'][sceneid] = []
	scenes = list(filter(lambda x : x['act'] == nscene, fexpand))
	if len(scenes) == 0 and len(nscene) == 1:
		del world['scenery'][sceneid]
	for scene in scenes: 
		pprint.pprint(scene)
		if 'fnmatch' not in scene: continue
		logging.error("Adding new scene...")
		logging.error(pprint.pformat(scene))
		sexpand = globals()[scene['fnmatch']['fname']](nodes = scene['node'], fnmatch = scene['fnmatch'], tags = scene['tag'])
		world['scenery'][sceneid].append(sexpand)

def get_model (defn = 0, actor = {}, isnew = 0):
	def setworldmodel (model):
		if model['macts'] == {}: actor = loader.loadModel(model['modfile'])
		else: actor = Actor(model['modfile'], model['macts'])
		actor.setPos (model['poshpr'][0], model['poshpr'][1], model['poshpr'][2])
		actor.setHpr (model['poshpr'][3], model['poshpr'][4], model['poshpr'][5])
		actor.setScale (model['poshpr'][6], model['poshpr'][7], model['poshpr'][8])
		world['models'].append({'file': model['modfile'], 'actor': actor, 'render': 1, 'vars': model['vagaries'], 'sceneid': {}})
	
	def createNew (actor = {}):
		poshpr = addposhprscl(actor['3dpoint'], actor['gpoint'])
		model = {'modfile': actor['file'], 'poshpr': poshpr, 'modloc': 'self', 'macts': actor['acts']}
		model['vagaries'] = actor['tags']['vagaries']+actor['gtags']['vagaries']
		if 'selfmove' in actor['tags']['vagaries']+actor['gtags']['vagaries']: model['modloc'] = "Hips"
		setworldmodel (model)
		return len(world['models'])-1
	
	if isnew == 0:
		found = {'match': 0, 'id': -1}
		##TODO: the actual vagaries as send by user should come from fexpand, else we chose from available
		for ms, models in enumerate(world['models']):
			if models['file'] != actor['file']: continue
			match = len(list(set(actor['tags']['vagaries']) & set(models['vars'])))
			if match > found['match']:
				found = {'match': match, 'id': ms}
		if found['match'] > 0:
			return found['id']
	nid = createNew (actor = actor)
	return nid

def expandAnimFile (name = '', maxcount = 99999, frames = [], fstart = 0):
	retval = []
	frid = 0
	for fset in frames:
		retval.append({'type': 'posit', 'param': fset[0], 'frid': frid})
		for fid in range(fset[1], fset[2]+1):
			retval.append({'type': 'posin', 'param': {'name': name, 'pseq': fid}, 'frid': frid+fstart})
			frid = frid + 1
			if frid > maxcount: break
	return retval

def expandBlanks (count = 75, fstart = 0):
	retval = []
	frid = 0
	for fid in range(fstart, fstart+count+1):
		retval.append({'type': 'noact', 'frid': fid})
	return retval

def she_standing (nodes = {}, fnmatch = {}, tags = {}):
	retval = {'model': -1, 'animat': []}
	k1obj, k0obj, isnew = nodes['0'], nodes['1'], 0
	if fnmatch['ftag'] == 'wdist': k2obj = nodes['2']
	## Get model details and frame values for action sequencing
	k1objid = get_model (actor = k1obj, isnew = 0)
	retval['model'] = k1objid
	if world['sceneid'] not in world['models'][k1objid]['sceneid']: world['models'][k1objid]['sceneid'][world['sceneid']] = 0 
	retval['animat'] = expandAnimFile (name = k0obj['name'], maxcount = 99999, frames = k0obj['frames'], fstart = world['models'][k1objid]['sceneid'][world['sceneid']])
	world['models'][k1objid]['sceneid'][world['sceneid']] = retval['animat'][len(retval['animat'])-1]['frid']
	if len(tags) > 0:
		## As a general rule, new objects should not be created here
		for tid in tags.keys():
			if tid == '0': world['tagval'][tags[tid]] = k1objid
	return retval

def object_lay (nodes = {}, fnmatch = {}, tags = {}):
	retval = {'model': -1, 'animat': []}
	k1obj, isnew = nodes['0'], 0
	## Get model details and frame values for action sequencing
	k1objid = get_model (actor = k1obj, isnew = 0)
	retval['model'] = k1objid
	if world['sceneid'] not in world['models'][k1objid]['sceneid']: world['models'][k1objid]['sceneid'][world['sceneid']] = 0 
	retval['animat'] = expandBlanks (count = 75, fstart = world['models'][k1objid]['sceneid'][world['sceneid']])
	world['models'][k1objid]['sceneid'][world['sceneid']] = retval['animat'][len(retval['animat'])-1]['frid']
	if len(tags) > 0:
		## As a general rule, new objects should not be created here
		for tid in tags.keys():
			if tid == '0': world['tagval'][tags[tid]] = k1objid
	return retval

def object_thrown (nodes = {}, fnmatch = {}, tags = {}):
	retval = {'model': -1, 'animat': []}
	k1obj, isnew = nodes['0'], 0
	## Get model details and frame values for action sequencing
	k1objid = get_model (actor = k1obj, isnew = 0)
	retval['model'] = k1objid
	if world['sceneid'] not in world['models'][k1objid]['sceneid']: world['models'][k1objid]['sceneid'][world['sceneid']] = 0 
	retval['animat'] = expandBlanks (count = 75, fstart = world['models'][k1objid]['sceneid'][world['sceneid']])
	world['models'][k1objid]['sceneid'][world['sceneid']] = retval['animat'][len(retval['animat'])-1]['frid']
	return retval

def addposhprscl (pos1 = [0, 0, 0, 0, 0, 0, 1, 1, 1], pos2 = [0, 0, 0, 0, 0, 0, 1, 1, 1]):
	retval = []
	retval.extend ([pos1[0]+pos2[0], pos1[1]+pos2[1], pos1[2]+pos2[2]])
	retval.extend ([pos1[3]+pos2[3], pos1[4]+pos2[4], pos1[5]+pos2[5]])
	retval.extend ([pos1[6]*pos2[6], pos1[7]*pos2[7], pos1[8]*pos2[8]])
	return retval

