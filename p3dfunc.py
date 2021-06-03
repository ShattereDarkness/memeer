import math
import pprint
import re
import os
import os.path
from pathlib import Path
import json
import copy

def mergeposition (base = [], addit = []):
	if len(addit) < 3: return base
	for idx in range(0, 3): base[idx] = base[idx] + addit[idx]
	if len(addit) < 6: return base
	for idx in range(3, 6): base[idx] = base[idx] + addit[idx]
	if len(addit) < 9: return base
	for idx in range(6, 9): base[idx] = base[idx] * addit[idx]
	return base

def readposfile (filenm, basedir):
	if not re.match(".+\.coord$", filenm): filenm = filenm + '.coord'
	filedat = basedir / 'coords' / filenm
	if not filedat.is_file():
		print ("ERROR: ", str(filedat), " could not be found")
		return [[]]
	with open(filedat) as lujs: allpos = json.load(lujs)
	return allpos['coord']

def fixinitemlist (lfrom = 1, linto = 1):
	retval = [0]
	for ix in range(1, linto):
		fix = round(ix*(lfrom/(linto-1)), 0)
		retval.append(int(fix))
	print ("fixinitemlist", retval)
	return retval

def generatedefposts (fcount = 1, baseloc = [], locrange = '', basedir = '.'):
	retval = []
	if len(baseloc) == 0: baseloc = [0,0,0,0,0,0,1,1,1]
	if 'locfile' in locrange and locrange['locfile'] != '':
		if len(baseloc) == 0: baseloc = [0,0,0]
		coords = readposfile (locrange['locfile'], basedir)
		if coords == [[]]: return [baseloc]
		itemls = fixinitemlist (lfrom = len(coords)-1, linto = fcount)
		lastix = -1
		print("baseloc, itemls, coords", baseloc, itemls, coords)
		for ix, item in enumerate(itemls):
			if lastix == ix:
				retval.append([])
				continue
			modpos = copy.deepcopy(baseloc)
			modpos[0] = modpos[0]+coords[item][0]
			modpos[1] = modpos[1]+coords[item][1]
			modpos[2] = modpos[2]+coords[item][2]
			retval.append(modpos)
	elif 'locfrom' in locrange and 'locupto' in locrange:
		modfpos, modlpos = copy.deepcopy(baseloc), copy.deepcopy(baseloc)
		mergeposition(base = modfpos, addit = locrange['locfrom'])
		mergeposition(base = modlpos, addit = locrange['locupto'])
		itemls = range (1, fcount)
		for ix in itemls:
			modpos = []
			for pix in range(0, 9):
				modpos.append(modfpos[pix] + ((modlpos[pix] - modfpos[pix])*(ix)/fcount))
			retval.append(modpos)
		retval.append(modlpos)
	else: retval.append(baseloc)
	#print ("generatedefposts", retval)
	return retval

def getposlist (bspec = {}, cspec = {}, fcount = 1, basedir = '.'):
	locrange = {}
	locpos = [0, 0, 0, 0, 0, 0, 1, 1, 1]
	if bspec['locfile'] != '': locrange = {'locfile': bspec['locfile']}
	elif cspec['locfile'] != '': locrange = {'locfile': cspec['locfile']}
	elif len(bspec['locfrom']) == 9 and len(bspec['locupto']) == 9: locrange = {'locfrom': bspec['locfrom'], 'locupto': bspec['locupto']}
	elif len(cspec['locfrom']) == 9 and len(cspec['locupto']) == 9: locrange = {'locfrom': cspec['locfrom'], 'locupto': cspec['locupto']}
	if len(bspec['locpos']) > 2: mergeposition (base = locpos, addit = bspec['locpos'])
	if len(cspec['locpos']) > 2: mergeposition (base = locpos, addit = cspec['locpos'])
	print ("bspec, cspec", bspec, cspec)
	retval = generatedefposts (fcount = fcount, baseloc = locpos, locrange = locrange, basedir = basedir)
	#print ("getposlist", retval)
	return retval

def serialized (cmdlets, rushobjlst, universe = {}, appsetup = {}, fframe = 1, fps = 1, winsize = [10, 10]):
	print ("cmdlets, rushobjlst, universe, appsetup, fframe", cmdlets, rushobjlst, universe , appsetup, fframe)
	basedir = Path(appsetup['project']['name'])
	preview = appsetup['project']['preview']
	frameset = {}
	lastindx = 1
	def mergeanimation (series = {}, frames = [], frameset = {}, lastindx = 1):
		for frid in range(frames[0], frames[1]+1):
			if str(frid) not in frameset: frameset[str(frid)] = []
			frameset[str(frid)].extend(series[str(frid)])
		if lastindx > frames[1]: return lastindx
		return frames[1]
	for ix, cmdlet in enumerate(cmdlets):
		if cmdlet['func'] == 'NOMATCH' or cmdlet['params'] == {}: continue
		print ("cmdlets["+str(ix)+"] =", cmdlet)
		fcount = cmdlet['frames'][1]-cmdlet['frames'][0]+1
		posdet = getposlist (bspec = cmdlet['bspec'], cspec = cmdlet['cspec'], fcount = fcount, basedir = basedir)
		print ("series input (params and posdet)", cmdlet['params'], posdet)
		series = globals()[cmdlet['func']] (universe = universe, params = cmdlet['params'], posdet = posdet, frames = cmdlet['frames'], rushobjlst = rushobjlst, basedir = basedir)
		lastindx = mergeanimation (series = series, frames = cmdlet['frames'], frameset = frameset, lastindx = lastindx)
	animes = {}
	for frid in range(1, fframe+1):
		if str(frid) in frameset: animes.setdefault('1', []).extend(frameset[str(frid)])
	for frid in range(fframe+1, lastindx+1):
		if str(frid) in frameset: animes.setdefault(str(frid - fframe + 1), []).extend(frameset[str(frid)])
	retval = {'animes': animes, 'fframe': fframe, 'rushobjlst': rushobjlst, 'lastindx': lastindx - fframe + 1,
				'basedir': str(basedir.stem), 'winsize': winsize, 'fps': fps, 'preview': preview}
	with open(basedir/"temp/temp_rushframes.js", "w") as lujs: json.dump(retval, lujs, indent=4)
	return {'code': 0, 'data': basedir/"temp/temp_rushframes.js"}

def createretval (frames = []):
	retval = {}
	for frid in range (frames[0], frames[1]+1):
		retval[str(frid)] = []
	return retval

def appendmovements (frames = [1,2], retval = {}, posdet = [], append = {}):
	for ix in range(frames[0], frames[1]+1):
		frid = ix - frames[0]
		if len(posdet)-1 < frid: break
		if len(posdet[frid]) < 3: continue
		append['pos'] = posdet[frid]
		if 'posnow' not in append: append['posnow'] = 0
		retval[str(ix)].append(copy.deepcopy(append))
	return 1

def loadobjectflet (params = {}, rushobjlst = [], retval = {}, basedir = Path('.'), frames = []):
	p3dmodel = rushobjlst[params['modid']]
	if params['isnew'] == 1 and p3dmodel['file'] not in ['line']:
		retval[str(frames[0])].append({'what': 'loadobj', 'model': params['modid']})
	p3dmodel['filenm'] = basedir.stem + '/model/' + p3dmodel['file']
	if 'type' not in params or params['type'] != 'acts': return p3dmodel
	p3dmodel['action'] = {}
	for acts in p3dmodel['acts'].keys():
		p3dmodel['action'][acts] = basedir.stem + '/model/action/' + p3dmodel['file']+ '__' + acts
	return p3dmodel

def object_exists (universe = {},  params = {}, posdet = [], frames = [], rushobjlst = [], basedir = Path('.')):
	retval = createretval (frames = frames)
	p3dmodel = loadobjectflet (params = params, retval = retval, rushobjlst = rushobjlst, basedir = basedir, frames = frames)
	appendmovements (frames = frames, retval = retval, posdet = posdet, append = {'what': 'moveobj', 'model': params['modid'], 'pos': []})
	return retval

def appendnewobjects (frames = [1,2], retval = {}, posdet = [], append = {}):
	for ix in range(frames[0], frames[1]+1):
		frid = ix - frames[0]
		if len(posdet)-1 < frid: break
		if len(posdet[frid]) < 3: continue
		append['pos'] = posdet[frid]
		retval[str(ix)].append(copy.deepcopy(append))
	return 1

def object_multiple (universe = {},  params = {}, posdet = [], frames = [], rushobjlst = [], basedir = Path('.')):
	retval = createretval (frames = frames)
	rushobjlst[params['modid']]['filenm'] = basedir.stem + '/model/' + rushobjlst[params['modid']]['file']
	appendmovements (frames = frames, retval = retval, posdet = posdet, append = {'what': 'loadobj', 'model': params['modid'], 'posnow': 1, 'pos': []})
	return retval

def object_named (universe = {},  params = {}, posdet = [], frames = [], rushobjlst = [], basedir = Path('.')):
	retval = createretval (frames = frames)
	p3dmodel = loadobjectflet (params = params, retval = retval, rushobjlst = rushobjlst, basedir = basedir, frames = frames)
	appendmovements (frames = frames, retval = retval, posdet = posdet, append = {'what': 'moveobj', 'model': params['modid'], 'pos': []})
	return retval

def object_does (universe = {},  params = {}, posdet = [], frames = [], rushobjlst = [], basedir = Path('.')):
	retval = createretval (frames = frames)
	p3dmodel = loadobjectflet (params = params, retval = retval, rushobjlst = rushobjlst, basedir = basedir, frames = frames)
	if p3dmodel['file'] == 'line':
		for ix in range(frames[0], frames[1]):
			frid = ix - frames[0]
			if len(posdet)-1 <= frid: break
			if len(posdet[frid-1]) == 0: continue
			retval[str(ix)].append({'what': 'lineseg', 'model': params['modid'], 'from': posdet[frid][:3], 'upto': posdet[frid+1][:3]})
	else:
		appendmovements (frames = frames, retval = retval, posdet = posdet, append = {'what': 'moveobj', 'model': params['modid'], 'pos': []})
	if params['func'] in ['move', 'locate', 'draw']: return retval
	if params['type'] == 'acts':
		fstart, flast = p3dmodel['acts'][params['func']]['fstart'], p3dmodel['acts'][params['func']]['flast']
		for frid in range(frames[0], frames[1]+1):
			if params['repeat'] == 0 and flast != -1 and (frid - frames[0]) > flast: break
			retval[str(frid)].append({'what': 'poseobj', 'model': params['modid'], 'action': params['func'], 'poseid': frid, 'repeat': params['repeat']})
	return retval

def storyparse (story):
	retval = []
	def getspecifics (text):
		print ("Working for text:", text)
		retval = [text, {'locupto': [], 'locfrom': [], 'locpos': [], 'locfile': '', 'sttmts': [], 'frames': []}]
		tofrom=re.match(".+\@\((.+?)\)\-\@\((.+?)\)", retval[0])
		if tofrom and len(tofrom.groups()) == 2:
			retval[1]['locfrom'] = list(map(float, tofrom.groups()[0].split(",")))
			retval[1]['locupto'] = list(map(float, tofrom.groups()[1].split(",")))
			retval[0] = re.sub("\@\((.+?)\)\-\@\((.+?)\)", "", retval[0])
		atloc = re.match(".+\@\((.+?)\)", retval[0])
		if atloc:
			retval[1]['locpos'] = list(map(float, atloc.groups()[0].split(",")))
			retval[0] = re.sub("\@\((.+?)\)", "", retval[0])
		posfile = re.match(".+\@f\((.+?)\)", retval[0])
		if posfile:
			retval[1]['locfile'] = posfile.groups()[0]
			retval[0] = re.sub("\@f\((.+?)\)", "", retval[0])
		sttmts = re.findall('(".+?")', retval[0])
		if sttmts:
			retval[1]['sttmts'] = sttmts
			if len(sttmts) == 1: retval[0] = re.sub('(".+?")', "", retval[0])
			else: retval[0] = re.sub('(".+?")', ' statement ', retval[0])
		frames = re.findall('#(\d+)\-#(\d+)', retval[0])
		if frames:
			retval[1]['frames'] = list(map(int, frames[0]))
			retval[0] = re.sub('#(\d+)\-#(\d+)', '', retval[0])
		frames = re.findall('#(\d+)', retval[0])
		if frames and len(retval[1]['frames']) == 0:
			retval[1]['frames'] = [int(frames[0]), -1]
			retval[0] = re.sub('#(\d+)', '', retval[0])
		retval[0] = re.sub(" +", " ", retval[0])
		retval[0] = retval[0].strip()
		return retval
	for sline in story.split("\n"):
		specs = getspecifics (sline)
		retval.append(specs)
	return retval
