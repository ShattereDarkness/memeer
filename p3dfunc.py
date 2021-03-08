import math
import pprint
import re
import os
import os.path
import json
import copy

basedir = ''
def deserialize (serialized = [], dsframe = 0, dsline = 0):
	if dsframe == 0: return serialized
	print ("Will check for frames and lines: ", dsframe, dsline)
	openline = list(range(dsline))
	insert0 = []
	modells = []
	for ix in reversed(range(dsframe)):
		scenes = serialized[ix]
		if len(scenes) == 0: continue
		for scene in scenes:
			if dsline <= scene['basic']['lineid']: continue
			if 'disable' in scene['addon']: openline.remove(scene['basic']['lineid'])
			if 'post' in scene['addon'] and scene['basic']['file'] not in modells:
				insert0.append({'basic': scene['basic'], 'addon': {'post': scene['addon']['post']}})
				modells.append(scene['basic']['file'])
			if 'sttmt' in scene['addon'] and scene['basic']['lineid'] in openline:
				insert0.append({'basic': scene['basic'], 'addon': {'sttmt': scene['addon']['sttmt']}})
				openline.remove(scene['basic']['lineid'])
	insert0.reverse()
	retval = [insert0] + serialized[dsframe:]
	return retval

def serialize (universe = {}, animation = [], deserial = 0, portfolio = ''):
	retval=[]
	global basedir
	basedir = portfolio
	for x in range(0, 9999): retval.append([])
	xindex = sindex = 0
	def mergedata (sindex, series, lineid):
		tbasic = {}
		if 'model' in series: tbasic = {'p3dfunc': 'loadmodel', 'file': series['model'], 'lineid': lineid}
		elif 'actor' in series: tbasic = {'p3dfunc': 'loadactor', 'file': series['actor']['mfile'], 'lineid': lineid,
											'acts': series['actor']['acts'], 'action': series['actor']['actf']['action']}
		elif 'camera' in series: tbasic = {'p3dfunc': 'camera', 'lineid': lineid}
		else: return sindex
		findex, lindex = series['frames'][0], series['frames'][1]+1
		for frid in range(series['frames'][0], series['frames'][1]+1):
			modix = frid - series['frames'][0]
			taddon = {}
			if len(series['posts']) > modix and len(series['posts'][modix]) > 0: taddon['post'] = series['posts'][modix]
			if len(series['sttmt']) > modix and len(series['sttmt'][modix]) > 0: taddon['sttmt'] = series['sttmt'][modix]
			if 'poses' in series and len(series['poses']) > modix: taddon['pose'] = series['poses'][modix]
			if taddon == {}: continue
			retval[frid].append({'basic': tbasic, 'addon': taddon})
		retval[frid].append({'basic': tbasic, 'addon': {'disable': lineid}})
		return series['frames'][1]
	print ("animation is:\n", animation)
	dsframe = 0
	for ano, anime in enumerate(animation):
		print ("anime is:\n", anime)
		series = globals()[anime['fname']] (universe = universe, sindex = sindex, tag = anime['ftag'], specs = anime['specs'], model = anime['mmaps'])
		print ("series is:\n", series)
		if deserial > 0 and anime['line'] > deserial and dsframe == 0:
			dsframe = series['frames'][0]
		sindex = mergedata (sindex, series, anime['line'])
		if sindex > xindex: xindex = sindex
	retval[xindex+1].append({'basic': {'p3dfunc': 'exitall'}})
	retval = deserialize (serialized = retval, dsframe = dsframe, dsline = deserial)
	return {'serial': retval, 'frindex': dsframe, 'frlast': xindex, 'frixdel': 9999-len(retval)}

def mergeposition (base = [], addit = []):
	retval = [0, 0, 0, 0, 0, 0, 1, 1, 1]
	for idx in range(0, 6): retval[idx] = base[idx] + addit[idx]
	for idx in range(6, 9): retval[idx] = base[idx] * addit[idx]
	return retval

def setframelen (sindex = 0, specs = {}, conflen = 120):
	fstart, flast = sindex, sindex+conflen
	if len(specs['frames']) == 2:
		if specs['frames'][1] != -1:
			fstart = specs['frames'][0]
			flast = specs['frames'][1]
		else:
			fstart = specs['frames'][0]
			flast = specs['frames'][0] + conflen
	return [fstart, flast]

def setscreentext (specs = {}, fcount=1):
	retval = []
	scount = len(specs['sttmts'])
	if scount == 0: return retval
	ltext = ''
	if fcount < scount:
		retval.append("\n".join(specs['sttmts']))
		return retval
	ratio = fcount//scount
	for sx in range(0, scount):
		frid = sx * ratio
		if len(retval) < frid:
			for fx in range (len(retval), frid): retval.append('')
		retval.append(specs['sttmts'][sx])
		ltext = ltext + specs['sttmts'][sx] + "\n"
	return retval

def setlistedpost (universe, gmodel, specs, fcount, wtfunc):
	basepos = modfpos = modlpos = gmodel['xyz'] + gmodel['hpr'] + gmodel['lbh']
	retval = []
	def readposfile (filenm, frames = fcount):
		if not re.match(".+\.txt$", filenm): filenm = filenm + '.txt'
		print ("filenm", filenm)
		if not os.path.isfile(basedir+'/coords/'+filenm): return retval
		print ("file found")
		with open(basedir+'/coords/'+filenm) as lujs: allpos = json.load(lujs)
		#print("allpos", allpos)
		return allpos['coord']
	coords = readposfile (specs['locfile'], frames = fcount)
	#print ("coords", coords)
	for frid in range(0, fcount+1):
		itemix = math.ceil(len(coords)*frid/fcount) if frid < fcount else len(coords)-1
		#print("frid, itemix", frid, itemix)
		modpos = copy.deepcopy(basepos)
		#print("modpos", modpos)
		#print("coords", coords[itemix])
		if re.match("X_", specs['locfile']):
			modpos[1] = modpos[1]+coords[itemix][0]
			modpos[2] = modpos[2]+coords[itemix][1]
		if re.match("Y_", specs['locfile']):
			modpos[0] = modpos[0]+coords[itemix][0]
			modpos[2] = modpos[2]+coords[itemix][1]
		if re.match("Z_", specs['locfile']):
			modpos[0] = modpos[0]+coords[itemix][0]
			modpos[1] = modpos[1]+coords[itemix][1]
		if re.match("3d__", specs['locfile']):
			modpos[0] = modpos[0]+coords[itemix][0]
			modpos[1] = modpos[1]+coords[itemix][1]
			modpos[2] = modpos[2]+coords[itemix][2]
		#print("updated modpos", modpos)
		retval.append(modpos)
	return retval

def setmodelpost (universe, gmodel, specs, fcount, wtfunc):
	basepos = modfpos = modlpos = gmodel['xyz'] + gmodel['hpr'] + gmodel['lbh']
	if len(specs['locpos']) != 0:
		modfpos = modlpos = mergeposition (base = basepos, addit = specs['locpos'])
	if len(specs['locfrom']) == 0 and len(specs['locupto']) == 0:
		return [modfpos]
	modfpos = mergeposition (base = basepos, addit = specs['locfrom'])
	modlpos = mergeposition (base = basepos, addit = specs['locupto'])
	retval = [modfpos]
	wtlist = range (1, fcount)
	for frid in wtlist:
		modpos = []
		for pix in range(0, 9):
			modpos.append(modfpos[pix] + ((modlpos[pix] - modfpos[pix])*(frid)/(fcount+1)))
		retval.append(modpos)
	retval.append(modlpos)
	return retval

def objectmov (universe = {}, sindex = 0, tag = 'text', specs = {}, model = {}):
	defaults = {'length': 120}
	retval = {'func': 'pass', 'file': '', 'post': [], 'sttmts': specs['sttmts']}
	obj = {}
	if tag == 'text': obj = model['0']
	if obj == {}: return retval
	gmodel = universe['objects'][obj[0]['gmodel']]
	smodel = obj[0]['smodel']
	frames = setframelen (sindex = sindex, specs = specs, conflen = defaults['length'])
	sttmt = setscreentext (specs = specs, fcount = frames[1]-frames[0])
	if specs['locfile'] != '':
		posts = setlistedpost (universe, gmodel, specs, frames[1]-frames[0], 'default')
	else:
		posts = setmodelpost (universe, gmodel, specs, frames[1]-frames[0], 'default')
	return ({'model': basedir+'/model/'+gmodel['model'][smodel]['file'], 'frames': frames, 'posts': posts, 'sttmt': sttmt})

def objectlay (universe = {}, sindex = 0, tag = 'text', specs = {}, model = {}):
	defaults = {'length': 120}
	retval = {'func': 'pass', 'file': '', 'post': [], 'sttmts': specs['sttmts']}
	obj = {}
	if tag == 'text': obj = model['2']
	if tag == 'singl': obj = model['0']
	if obj == {}: return retval
	gmodel = universe['objects'][obj[0]['gmodel']]
	smodel = obj[0]['smodel']
	frames = setframelen (sindex = sindex, specs = specs, conflen = defaults['length'])
	sttmt = setscreentext (specs = specs, fcount = frames[1]-frames[0])
	posts = setmodelpost (universe, gmodel, specs, frames[1]-frames[0], 'default')
	return ({'model': basedir+'/model/'+gmodel['model'][smodel]['file'], 'frames': frames, 'posts': posts, 'sttmt': sttmt})

def getactorfile (universe, gmodel, smodel, action):
	retval = {}
	basef = gmodel['model'][0]['file']
	mfile = basedir+'/actor/'+gmodel['model'][smodel]['file']
	acts = {}
	actf = {'speed': 1, 'fstart': 0, 'flast': 1}
	for actf in gmodel['acts']:
		actn, actdet = list(actf.items())[0][0], list(actf.items())[0][1]
		acts[actn] = basedir+'/actor/action/'+basef + "__" + actn
		if actn != action: continue
		pactf = {'action': action,'speed': actdet['speed'], 'fstart': actdet['fstart'], 'flast': actdet['flast']}
	return {'mfile': mfile, 'acts': acts, 'actf': pactf}

def setactorpose (actfnc, fcount):
	retval = []
	ix = 0
	while (ix <= fcount+1):
		fx = actfnc['fstart']
		for fx in range(actfnc['fstart'], actfnc['flast']+1):
			retval.append({'pose': fx})
			ix = ix + 1
			if ix == fcount: return retval
		retval.append({'func': 'poschk'})
		if ix == fcount: return retval
	return retval

def actordoes (universe = {}, sindex = 0, tag = 'text', specs = {}, model = {}):
	retval = {'func': 'pass', 'file': '', 'post': [], 'sttmts': specs['sttmts']}
	obj = {}
	if tag == 'text':
		obj = model['0']
		act = model['1']
	if obj == {}: return retval
	gmodel = universe['objects'][obj[0]['gmodel']]
	smodel = obj[0]['smodel']
	print(model	)
	action = universe['actions'][act[0]['gmodel']]['func']
	print('action', action)
	actor = getactorfile (universe, gmodel, smodel, action)
	print (actor)
	frames = setframelen (sindex = sindex, specs = specs, conflen = actor['actf']['flast']-actor['actf']['fstart'])
	sttmt = setscreentext (specs = specs, fcount = frames[1]-frames[0])
	posts = setmodelpost (universe, gmodel, specs, frames[1]-frames[0], 'default')
	poses = setactorpose (actfnc = actor['actf'], fcount = frames[1]-frames[0])
	return ({'actor': actor, 'frames': frames, 'posts': posts, 'poses': poses, 'sttmt': sttmt})