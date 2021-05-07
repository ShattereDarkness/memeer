import math
import pprint
import re
import os
import os.path
import json
import copy
import coordinates

def mergeposition (base = [], addit = []):
	retval = [0, 0, 0, 0, 0, 0, 1, 1, 1]
	if len(addit) < 3: return base
	for idx in range(0, 3): retval[idx] = base[idx] + addit[idx]
	if len(addit) < 9: return retval
	for idx in range(3, 6): retval[idx] = base[idx] + addit[idx]
	for idx in range(6, 9): retval[idx] = base[idx] * addit[idx]
	return retval

def readposfile (filenm, basedir):
	print("filenm, basedir", filenm, basedir)
	if not re.match(".+\.txt$", filenm): filenm = filenm + '.txt'
	if not os.path.isfile(basedir+'/coords/'+filenm): return []
	print (filenm, "file found")
	with open(basedir+'/coords/'+filenm) as lujs: allpos = json.load(lujs)
	return allpos['coord']

def fixinitemlist (lfrom = 1, linto = 1):
	retval = [0]
	for ix in range(1, linto):
		fix = round(ix*(lfrom/(linto-1)), 0)
		retval.append(int(fix))
	return retval

def generatedefposts (fcount = 1, baseloc = [], locrange = '', basedir = '.'):
	retval = []
	if len(baseloc) == 0: baseloc = [0,0,0,0,0,0,1,1,1]
	if 'locfile' in locrange and locrange['locfile'] != '':
		coords = readposfile (locrange['locfile'], basedir)
		itemls = fixinitemlist (lfrom = len(coords)-1, linto = fcount)
		lastix = -1
		print("itemls, coords",  itemls, coords)
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
		modfpos = mergeposition(base = baseloc, addit = locrange['locfrom'])
		modlpos = mergeposition(base = baseloc, addit = locrange['locupto'])
		itemls = range (1, fcount)
		for ix in itemls:
			modpos = []
			for pix in range(0, 9):
				modpos.append(modfpos[pix] + ((modlpos[pix] - modfpos[pix])*(ix)/fcount))
			retval.append(modpos)
		retval.append(modlpos)
	else: retval.append(baseloc)
	return retval

def getposlist (bspec = {}, cspec = {}, fcount = 1, basedir = '.'):
	locrange = {}
	locpos = [0, 0, 0, 0, 0, 0, 1, 1, 1]
	if bspec['locfile'] != '': locrange = {'locfile': bspec['locfile']}
	elif cspec['locfile'] != '': locrange = {'locfile': cspec['locfile']}
	elif len(bspec['locfrom']) == 9 and len(bspec['locupto']) == 9: locrange = {'locfrom': bspec['locfrom'], 'locupto': bspec['locupto']}
	elif len(cspec['locfrom']) == 9 and len(cspec['locupto']) == 9: locrange = {'locfrom': cspec['locfrom'], 'locupto': cspec['locupto']}
	if len(bspec['locpos']) == 9: mergeposition (base = locpos, addit = bspec['locpos'])
	if len(cspec['locpos']) == 9: mergeposition (base = locpos, addit = cspec['locpos'])
	retval = generatedefposts (fcount = fcount, baseloc = locpos, locrange = locrange, basedir = basedir)
	return retval

def serialized (cmdlets, rushobjlst, universe = {}, appsetup = {'project': {'folder': '.'}}, fframe = 1):
	basedir = appsetup['project']['folder']
	ispreview = appsetup['project']['preview']
	winsize = appsetup['project']['winsize']
	fps = appsetup['project']['fps']
	frameset = {}
	lastindx = 1
	def mergeanimation (series = {}, frames = [], frameset = {}, lastindx = 1):
		print ("series", series)
		for frid in range(frames[0], frames[1]+1):
			if str(frid) not in frameset: frameset[str(frid)] = []
			frameset[str(frid)].append(series[str(frid)])
		if lastindx > frames[1]: return lastindx
		return frames[1]
	for cmdlet in cmdlets:
		if cmdlet['func'] == 'NOMATCH' or cmdlet['params'] == {}: continue
		#cmdlet['bspec'], cmdlet['cspec']
		fcount = cmdlet['frames'][1]-cmdlet['frames'][0]+1
		posdet = getposlist (bspec = cmdlet['bspec'], cspec = cmdlet['cspec'], fcount = fcount, basedir = basedir)
		series = globals()[cmdlet['func']] (universe = universe, params = cmdlet['params'], posdet = posdet, frames = cmdlet['frames'], rushobjlst = rushobjlst)
		lastindx = mergeanimation (series = series, frames = cmdlet['frames'], frameset = frameset, lastindx = lastindx)
		print ("frameset", frameset)
	animes = {}
	for frid in range(1, fframe+2): animes['1'].extend(frameset[str(frid)])
	for frid in range(fframe+1, lastindx+1): animes[str(frid - fframe + 1)].extend(frameset[str(frid)])
	
	retval = {'animes': animes, 'fframe': fframe, 'rushobjlst': rushobjlst, 'lastindx': lastindx,
				'basedir': basedir, 'winsize': winsize, 'fps': fps, 'preview': preview}
	with open("temp_rushframes.js", "w") as lujs: json.dump(frameset, lujs)
	return frameset

def createretval (frames = []):
	retval = {}
	for frid in range (frames[0], frames[1]+1):
		retval[str(frid)] = []
	return retval

def object_exists (universe = {},  params = {}, posdet = [], frames = [], rushobjlst = []):
	retval = createretval (frames = frames)
	p3dmodel = rushobjlst[params['modid']]
	if params['isnew'] == 1: retval[str(frames[0])].append({'what': 'loadobj', 'model': params['modid']})
	for frid in range(frames[0], frames[1]+1):
		if len(posdet) <= frid: break
		if len(posdet[frid-1]) == 0: continue
		retval[str(frid)].append({'what': 'moveobj', 'model': params['modid'], 'pos': posdet[frid-1]})
	return retval

def object_does (universe = {},  params = {}, posdet = [], frames = [], rushobjlst = []):
	retval = createretval (frames = frames)
	print ("params, posdet, fcount", params, posdet, fcount)
	p3dmodel = rushobjlst[params['modid']]
	if params['isnew'] == 1: retval[str(frames[0])].append({'what': 'loadobj', 'model': params['modid']})
	if p3dmodel['file'] == 'line':
		for frid in range(frames[0], frames[1]+1):
			if len(posdet) <= frid: break
			if len(posdet[frid-1]) == 0: continue
			retval[str(frid)].append({'what': 'lineseg', 'model': params['modid'], 'from': posdet[frid-1], 'upto': posdet[frid]})
	else:
		for frid in range(frames[0], frames[1]+1):
			if len(posdet) <= frid: break
			if len(posdet[frid-1]) == 0: continue
			retval[str(frid)].append({'what': 'moveobj', 'model': params['modid'], 'pos': posdet[frid-1]})
	if params['type'] == 'move': return retval
	if params['type'] == 'acts':
		fstart, flast = p3dmodel['acts'][params['func']]['fstart'], p3dmodel['acts'][params['func']]['flast']
		retval[str(frames[0])][0]['stats'] = {'fstart': fstart, 'flast': flast, 'redux': 0}
		for frid in range(frames[0], frames[1]+1):
			retval[str(frid)].append({'what': 'poseobj', 'model': params['modid'], 'action': params['func'], 'poseid': frid})
	return retval

def storyparse (story):
	retval = []
	def getspecifics (text):
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
