import math
import pprint

def serialize (universe = {}, animation = []):
	retval=[]
	for x in range(0, 9999): retval.append([])
	sindex = 0
	def mergedata (sindex, series):
		for frid in range(series['frames'][0], series['frames'][1]):
			if (len(series['post']) > frid-series['frames'][0]):
				retval[frid].append({'func': series['func'], 'file': series['file'], 'post': series['post'][frid-series['frames'][0]]})
		return series['frames'][1]
	print("universe:", universe)
	print ("animation:", animation)
	for ano, anime in enumerate(animation):
		print ("anime:", anime)
		series = globals()[anime['fname']] (universe = universe, sindex = sindex, tag = anime['ftag'], specs = anime['specs'], model = anime['mmaps'])
		print (series)
		sindex = mergedata (sindex, series)
	return retval

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
	fcount = frames[1] - frames[0]
	ltext = ''
	if fcount < scount:
		retval.append("\n".join(specs['sttmts']))
		return retval
	ratio = fcount//scount
	for sx in range(0, scount):
		frid = sx * ratio
		if len(retval) < frid:
			for fx in range (len(retval), frid): retval.append('')
		retval.append(ltext + specs['sttmts'][sx])
		ltext = ltext + specs['sttmts'][sx] + "\n"
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
	return ({'model': gmodel['model'][smodel]['file'], 'frames': frames, 'posts': posts, 'sttmt': sttmt})

def getactorfile (universe, gmodel, smodel, action):
	retval = {}
	basef = gmodel['model'][0]['file']
	mfile = gmodel['model'][smodel]['file']
	acts = {}
	actf = {'speed': 1, 'fstart': 0, 'flast': 1}
	for actf in gmodel['acts']:
		actn, actdet = list(actf.items())[0][0], list(actf.items())[0][1]
		acts[actn] = basef + "_" + actn
		if actn != action: continue
		actf = {'action': action,'speed': actdet['speed'], 'fstart': actdet['fstart'], 'flast': actdet['flast']}
	return {'mfile': mfile, 'acts': acts, 'actf': actf}

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
	action = universe['actions'][act[0]['gmodel']]['func']
	actor = getactorfile (universe, gmodel, smodel, action)
	frames = setframelen (sindex = sindex, specs = specs, conflen = actor['actf']['flast']-actor['actf']['fstart'])
	sttmt = setscreentext (specs = specs, fcount = frames[1]-frames[0])
	posts = setmodelpost (universe, gmodel, specs, frames[1]-frames[0], 'default')
	poses = setactorpose (actfnc = actor['actf'], fcount = frames[1]-frames[0])
	return ({'actor': actor, 'frames': frames, 'posts': posts, 'poses': poses})