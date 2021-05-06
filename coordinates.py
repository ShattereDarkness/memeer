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
			modpos = copy.deepcopy(blocfrom)
			modpos[0] = modpos[0]+coords[item][0]
			modpos[1] = modpos[1]+coords[item][1]
			modpos[2] = modpos[2]+coords[item][2]
			retval.append(modpos)
	elif 'locfrom' in locrange and 'locupto' in locrange:
		modfpos = mergeposition(base = blocfrom, addit = locrange['locfrom'])
		modlpos = mergeposition(base = blocfrom, addit = locrange['locupto'])
		retval = [modfpos]
		itemls = range (1, fcount)
		for ix in itemls:
			modpos = []
			for pix in range(0, 9):
				modpos.append(modfpos[pix] + ((modlpos[pix] - modfpos[pix])*(ix)/fcount))
			retval.append(modpos)
		retval.append(modlpos)
	else: return baseloc
	return retval
