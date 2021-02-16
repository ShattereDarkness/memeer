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
		series = globals()[anime['funct']['fname']] (universe = universe, sindex = sindex, tag = anime['funct']['ftag'], specs = anime['specs'], model = anime['mmaps'])
		sindex = mergedata (sindex, series)
	return retval

def setframelen (sindex = 0, specs = {}, conflen = 120):
	fstart, flast = 0, 10
	if len(specs['frames']) == 2 and specs['frames'][1] > 0:
		fstart = specs['frames'][0]
		flast = specs['frames'][1]
	elif len(specs['frames']) == 2 and specs['frames'][1] == -1:
		fstart = specs['frames'][0]
		flast = specs['frames'][0] + conflen
	else:
		fstart = sindex
		flast = sindex + conflen
	return [fstart, flast]

def mergeposition (base = [], addit = []):
	retval = [0, 0, 0, 0, 0, 0, 1, 1, 1]
	for idx in range(0, 6): retval[idx] = base[idx] + addit[idx]
	for idx in range(6, 9): retval[idx] = base[idx] * addit[idx]
	return retval

def setmodelpost (modpos = [0, 0, 0, 0, 0, 0, 1, 1, 1], specs = {}, fcount = 10):
	retval = []
	if len(specs['locpos']) != 0:
		modpos = mergeposition (base = modpos, addit = specs['locpos'])
	if len(specs['locfrom']) == 0 or len(specs['locupto']) == 0:
		return [modpos]
	locfrom = mergeposition (base = modpos, addit = specs['locfrom'])
	retval.append(locfrom)
	locupto = mergeposition (base = modpos, addit = specs['locupto'])
	for frid in range (1, fcount):
		modpos = []
		for pix in range(0, 9):
			modpos.append(locfrom[pix] + ((locupto[pix] - locfrom[pix])*(frid)/(fcount-1)))
		retval.append(modpos)
	return retval

def objectlay (universe = {}, sindex = 0, tag = 'text', specs = {}, model = {}):
	defaults = {'length': 120}
	retval = {'func': 'pass', 'file': '', 'post': [], 'sttmts': specs['sttmts']}
	obj = {}
	if tag == 'text': obj = model['2']
	if obj == {}: return retval
	gmodel = universe['objects'][obj[0]['gmodel']]
	smodel = obj[0]['smodel']
	retval['file'] = gmodel['model'][smodel]['file']
	retval['func'] = 'loadmodel'
	retval['frames'] = frames = setframelen (sindex = sindex, specs = specs, conflen = defaults['length'])
	modpos = gmodel['xyz'] + gmodel['hpr'] + gmodel['lbh']
	retval['post'] = setmodelpost (modpos = modpos, specs = specs, fcount = frames[1]-frames[0])
	return retval
