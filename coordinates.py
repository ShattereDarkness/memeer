import math
import pprint
import re
import os
import os.path
import json
import copy

def mergeposition (base = [], addit = []):
	retval = [0, 0, 0, 0, 0, 0, 1, 1, 1]
	if len(addit) < 3: return base
	for idx in range(0, 3): retval[idx] = base[idx] + addit[idx]
	if len(addit) < 6: return retval
	for idx in range(3, 6): retval[idx] = base[idx] + addit[idx]
	if len(addit) < 9: return retval
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

def generatedefposts (fcount, blocfrom, locrange, basedir):
	retval = []
	if len(blocfrom) == 0: blocfrom = [0,0,0,0,0,0,1,1,1]
	if 'locfile' in locrange:
		coords = readposfile (locrange['locfile'], basedir)
		itemls = fixinitemlist (lfrom = len(coords)-1, linto = fcount)
		lastix = -1
		print("itemls, coords",  itemls, coords)
		for ix, item in enumerate(itemls):
			if lastix == ix:
				retval.append([])
				continue
			modpos = copy.deepcopy(blocfrom)
			modpos[0] = modpos[0]+coords[item][0]
			modpos[1] = modpos[1]+coords[item][1]
			modpos[2] = modpos[2]+coords[item][1]
			retval.append(modpos)
	else:
		modfpos = locrange['locfrom']
		modlpos = locrange['locupto']
		retval = [modfpos]
		itemls = range (1, fcount)
		for ix in itemls:
			modpos = []
			for pix in range(0, 9):
				modpos.append(modfpos[pix] + ((modlpos[pix] - modfpos[pix])*(ix)/fcount))
			retval.append(modpos)
		retval.append(modlpos)
	return retval

def _oldfunctions ():
	def setlistedpost (universe, gmodel, specs, fcount, wtfunc, bspecs):
		basepos = modfpos = modlpos = gmodel['xyz']
		retval = []
		def readposfile (filenm, frames = fcount):
			if not re.match(".+\.txt$", filenm): filenm = filenm + '.txt'
			if not os.path.isfile(basedir+'/coords/'+filenm): return retval
			print (filenm, "file found")
			with open(basedir+'/coords/'+filenm) as lujs: allpos = json.load(lujs)
			return allpos['coord']
		coords = readposfile (specs['locfile'], frames = fcount)
		for frid in range(0, fcount+1):
			itemix = math.ceil(len(coords)*frid/fcount) if frid < fcount else len(coords)-1
			modpos = copy.deepcopy(basepos)
			modpos[0] = modpos[0]+coords[itemix][0]
			modpos[1] = modpos[1]+coords[itemix][1]
			modpos[2] = modpos[2]+coords[itemix][2]
			retval.append(modpos)
		return retval

	def setmodelpost1 (universe, gmodel, specs, fcount, wtfunc, bspecs):
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
