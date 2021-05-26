import os
from pathlib import Path
import json
import re
import shutil
import p3dfunc
import subprocess

import requests
appfile = 'appsetup.js'

def port_conf_save (appsetup):
	appfile = 'appsetup.js'
	print ("writng", appsetup)
	putUniverseJS (appsetup, appfile)

def saveuniv(which = 'XXX', what = [], where = 'XXX'):
	nuniv = getUniverseJS (where)
	nuniv[which] = what
	putUniverseJS (nuniv, where)

def getappsetup ():
	with open(appfile) as lujs: appsetup = json.load(lujs)
	return appsetup

def putappsetup (appsetup):
	with open(appfile, "w") as lujs: json.dump(lconf, lujs)
	return 1

def getUniverseJS (univfile):
	with open(univfile) as lujs: univ = json.load(lujs)
	return univ

def putUniverseJS (univ, univfile):
	with open(univfile, "w") as lujs: json.dump(univ, lujs, indent=4)
	return 1

def savethedata(lportui):
	print(lportui['desc'].get())
	return 1

def getbasedir(portf_dir):
	portf_dir = Path(portf_dir)
	return portf_dir.stem

def checkProject (folder =  ''):
	portf_dir = Path(folder)
	if not portf_dir.is_dir(): return 0
	return 1

def createProject (folder =  ''):
	portf_dir = Path(folder)
	universe = portf_dir / 'universe.js'
	if not universe.is_file():
		with open(universe, "w") as lujs: json.dump({'initialized': 'from Meemer'}, lujs)
	model_dir = portf_dir / 'model'
	if not model_dir.is_dir(): model_dir.mkdir()
	media_dir = portf_dir / 'media'
	if not media_dir.is_dir(): media_dir.mkdir()
	temp_dir = portf_dir / 'temp'
	if not temp_dir.is_dir(): temp_dir.mkdir()
	actor_dir = portf_dir / 'actor'
	if not actor_dir.is_dir(): actor_dir.mkdir()
	action_dir = portf_dir / 'actor' / 'action'
	if not action_dir.is_dir(): action_dir.mkdir()
	coords_dir = portf_dir / 'coords'
	if not coords_dir.is_dir(): coords_dir.mkdir()
	stories_dir = portf_dir / 'stories'
	if not stories_dir.is_dir(): stories_dir.mkdir()
	rushes_dir = portf_dir / 'rushes'
	if not rushes_dir.is_dir(): rushes_dir.mkdir()
	rushtmp_dir = portf_dir / 'rushes' / 'temp'
	if not rushtmp_dir.is_dir(): rushtmp_dir.mkdir()
	return 1

def check2files (path1=Path('.'), path2=Path('.'), fstem='', suffix1='', suffix2=''):
	if (path1 / (fstem+suffix1)).exists() and (path2 / (fstem+suffix2)).exists(): return 0
	if (path1 / (fstem+suffix1)).exists() and not (path2 / (fstem+suffix2)).exists(): return 1
	if not (path1 / (fstem+suffix1)).exists() and (path2 / (fstem+suffix2)).exists(): return 2
	return 3

def create_mediamodel (folderstr = "model/", media_dir = Path('.'), model_dir = Path('.')):
	retval = {'add': 0, 'rem': 0}
	os.chdir(folderstr)
	for file in media_dir.iterdir():
		if file.suffix in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
			exist = check2files (path1=media_dir, path2=model_dir, fstem=file.stem, suffix1=file.suffix, suffix2='.egg')
			if exist == 1:
				print ("Creating model for file", file)
				cmdstr = "egg-texture-cards -o " + file.stem + ".egg ../media/" + file.name
				os.system(cmdstr)
				retval['add'] = retval['add'] + 1
			if exist == 2:
				(model_dir / (file.stem+'.egg')).unlink()
				retval['rem'] = retval['rem'] + 1
		elif file.suffix in ['.gif', '.mp4', '.mov', '.avi', '.wmv', '.webm']:
			exist = check2files (path1=media_dir, path2=model_dir, fstem=file.stem, suffix1=file.suffix, suffix2='.egg')
			if exist == 1:
				print ("Creating model for file", file)
				os.mkdir('../media/' + file.stem)
				cmdstr = "ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=avg_frame_rate ../media/" + file.name
				avgfps = (subprocess.run(cmdstr, capture_output=True)).stdout.decode('unicode_escape')[:-2]
				vfps = round(float(avgfps.split('/')[0])/float(avgfps.split('/')[1]))
				vfps = round(vfps)
				cmdstr = "ffmpeg -i ../media/" + file.name + " -vf scale=320:-1 -vsync 0 ../media/" + file.stem + "/series%4d.png"
				os.system(cmdstr)
				cmdstr = "ffmpeg -i ../media/" + file.name + " -vn -acodec copy ../audio/" + file.stem + ".aac"
				os.system(cmdstr)
				shutil.copy(file, Path("../video/"+file.name))
				cmdstr = "egg-texture-cards -o " + file.stem + ".egg -fps "+str(vfps)+" ../media/" + file.stem + "/series*.png"
				os.system(cmdstr)
				retval['add'] = retval['add'] + 1
			elif exist == 2:
				(model_dir / (file.stem+'.egg')).unlink()
				shutil.rmtree('../media/' + file.stem, ignore_errors=True)
				retval['rem'] = retval['rem'] + 1
	os.chdir("../../")
	return retval

def getUniverseData (user = '', folder =  '', appset = {}):
	retval = {'media': {'add': 0, 'rem': 0}, 'model': {'add': 0, 'rem': 0}, 'anims': 0}
	portf_dir = Path(folder)
	#Here we expect that the folder have been created as per createProject function
	universe = portf_dir / 'universe.js'
	with universe.open('r') as univjs: univ = json.load(univjs)
	if 'namedetail' not in univ or univ['namedetail'] == '':
		univ['namedetail'] = 'Basic environment for create at '+appset['project']['folder']+' self initialized'
	model_dir = portf_dir / 'model'
	action_dir = model_dir / 'action'
	media_dir = portf_dir / 'media'
	# Start checking for models and actions
	if 'actions' not in univ: univ['actions'] = []
	if 'objects' not in univ: univ['objects'] = []
	## Conver media files into models
	fps = appset['project']['fps']
	ffmopt = "-pix_fmt pal8" if appset['project']['preview'] == 1 else "-pix_fmt pal8"
	retval['media'] = create_mediamodel (folderstr = folder+"/model", media_dir = media_dir, model_dir = model_dir)
	# Check for each model now
	for muniv in univ['objects']:
		if (model_dir / (muniv['file']+".egg")).exists(): continue
		muniv['saved'] = 0
		retval['model']['rem'] = retval['model']['rem'] + 1
	for mfile in model_dir.glob('*.egg'):
		if len(list(filter(lambda x : x['file'] == mfile.stem, univ['objects']))) > 0: continue
		univ['objects'].append({'syns': [mfile.stem], 'move': ['move', 'locate', 'l'], 'jjrb': [], 'acts': {}, 'joint': '', \
							'file': mfile.stem, 'jjrb': []})
		retval['model']['add'] = retval['model']['add'] + 1
	univ['objects'] = list(filter(lambda x : 'saved' not in x or x['saved'] == 1, univ['objects']))
	uactions = []
	for afile in action_dir.glob('*.egg'):
		actor, anime = afile.stem.split ('__', 1)
		uactions.append(anime)
		if len(list(filter(lambda x : x['file'] == actor, univ['objects']))) == 0: continue
		if len(list(filter(lambda x : x['func'] == anime, univ['actions']))) == 0:
			univ['actions'].append({'jjrb': [], 'syns': [anime], 'func': anime, 'show': 1})
			retval['actions']['add'] = retval['actions']['add'] + 1
		mobject = list(filter(lambda x : x['file'] == actor, univ['objects']))[0]
		if anime not in mobject['acts']:
			mobject['acts'][anime] = {"fstart": 1, "flast": -1}
	if 'logicals' not in univ: univ['logicals'] = []
	if 'functions' not in univ: univ['functions'] = {}
	# update the values in universe
	if retval['media']['add']+retval['media']['rem']+retval['model']['add']+retval['model']['rem']+retval['anims'] ==  0:
		return univ
	with universe.open('w') as univjs: json.dump(univ, univjs, indent=4)
	return univ

def entdefaultparams (ix, params, projvars):
	if params[ix] == 'FPS': return projvars['fps']
	if params[ix] == 'Screen Size (Wide x Height)': return projvars['winsize']
	if params[ix] == 'Canvas Size (Wide x Height)': return projvars['canvas']
	if params[ix] == 'Play from frame#': return '1'
	if params[ix] == 'From frame#': return '1'
	if params[ix] == 'Upto frame#': return '-1'
	if params[ix] == 'Draft (Yes/No)': return projvars['preview']
	if params[ix] == 'Frames range': return '1, -1'
	if params[ix] == '*NAME LIKE*': return '*'
	if params[ix] == 'Camera Location (3D)': return '0, -120, 0'
	if params[ix] == 'Camera Looks at/\nWhiteboard Center': return '0, 0, 0'
	return ""

def splittext (text = '', rtyp = str, sep = ','):
	retval = []
	for nstr in text.split(sep):
		if nstr == '': continue
		retval.append(rtyp(nstr.strip()))
	return retval

def loadsynos (uwords, verbjs, expand):
	retval = []
	for uword in uwords:
		if ((expand == 0 and not re.match(".+\+$", uword)) or (expand == 1 and re.match(".+-$", uword))):
			retval.append(uword)
			continue
		if re.match(".+\+$", uword): uword = uword[:-1]
		for fwords in verbjs:
			if not uword in fwords: continue
			retval.extend(fwords)
		retval.append(uword)
	retval=list(set(retval))
	return retval

def updateuniverseforsend (universe = {}, appsetup = {}):
	def removeextraverb (actions):
		for action in actions:
			nsyns = []
			for syns in action['syns']:
				verbs = syns.split(",")
				for verb in verbs:
					nverb = verb.strip()
					if re.match(".+-$", nverb):
						nverb = nverb[:-1]
					nsyns.append(nverb)
			action['syns'] = nsyns
		return 1
	def updatejoints (objects, joints = {}):
		for model in objects:
			if model['joint'] == '' or model['joint'] not in joints: continue
			model['joint'] = joints[model['joint']]
	def additionalobj (objects):
		objects.insert(0, {'file': 'camera', 'acts': {}, 'syns': ['camera'], 'jjrb': [], 'move': ['move', 'locate', 'looks'], 'joint': ''})
		objects.insert(1, {'file': 'line', 'acts': {}, 'syns': ['line'], 'jjrb': [], 'move': ['draw'], 'joint': ''})
		objects.insert(2, {'file': 'subtext', 'acts': {}, 'syns': ['subtitle', 'text'], 'jjrb': [], 'move': ['draw'], 'joint': ''})
	removeextraverb (universe['actions'])
	updatejoints (universe['objects'], joints = appsetup['joint'])
	additionalobj (universe['objects'])
	return 1

def getscreensize (text, w, h):
	try:
		winsize = text.replace('X', 'x')
		scrwide = list(map(int, winsize.split('x')))[0]
		scrhigh = list(map(int, winsize.split('x')))[1]
		if scrwide * scrhigh < 20: return w, h
		else: return scrwide, scrhigh
	except: return w, h
	return 500, 500

def forceint(text):
	try: return int(text)
	except: return -1

def exec_play_story (entparams = [], appsetup = {}, universe = {}, story = ''):
	print ("appsetup:", appsetup)
	print ("entparams:", entparams)
	fps = appsetup['project']['fps'] if forceint(entparams[0]) == -1 else forceint(entparams[0])
	scrwide, scrhigh = getscreensize (entparams[1], 0, 0) 
	if scrwide * scrhigh < 2: scrwide, scrhigh = getscreensize (appsetup['project']['winsize'], 500, 500) 
	fframe = 1 if forceint(entparams[2]) == -1 else forceint(entparams[2])
	print ("fps, scrwide, scrhigh, frame", fps, scrwide, scrhigh, fframe)
	updateuniverseforsend (universe = universe, appsetup = appsetup)
	nlu = response_textplay (appsetup['meemerurl'], {'Content-type': 'application/json'}, universe, p3dfunc.storyparse(story), appsetup['democheck'])
	serialized = p3dfunc.serialized (nlu['cmdlets'], nlu['rushobjlst'], universe = universe, appsetup = appsetup, fframe = fframe, fps = fps, winsize = [scrwide, scrhigh])
	os.system('ppython p3dpreview.py')
	pngoverwrites (fframe = fframe, imgdest = appsetup['project']['folder']+'/rushes/')
	return {'code': 0, 'data': 'temp_rushframes'}

def pngoverwrites (fframe = 1, imgdest = Path('.')):
	for frid in range(2, 9999):
		oldimg = "rush__"+"%04d"%(frid)+".png"
		newimg = "rush__"+"%04d"%(frid+fframe-2)+".png"
		try: os.remove(imgdest+newimg)
		except: pass
		if not os.path.isfile(imgdest+'temp/'+oldimg): break
		try: os.rename(imgdest+'temp/'+oldimg, imgdest+newimg)
		except: pass
	return 1

def exec_save_story (entparams = [], appsetup = {}, story = ''):
	if entparams[0] == '': return 0
	filename = Path(appsetup['project']['name']) / 'stories' / entparams[0]
	if filename.suffix != '.story': filename = Path(appsetup['project']['name']) / 'stories' / (entparams[0]+'.story')
	filename.write_text(story)
	return 1

def exec_open_story (entparams = [], appsetup = {}):
	if entparams[0] == '': return 0
	filename = Path(appsetup['project']['name']) / 'stories' / entparams[0]
	if filename.suffix != '.story': filename = Path(appsetup['project']['name']) / 'stories' / (entparams[0]+'.story')
	if not filename.is_file(): return {'code': 1, 'data': ''}
	return {'code': 0, 'data': filename.read_text()}

def exec_list_filesets (entparams = [], appsetup = {}, folder = '___', suffix = '.tmp'):
	retval = {'code': 0, 'data': []}
	dirpath = Path(appsetup['project']['name']) / folder
	entparams[0] = '*' + entparams[0] + '*'
	entparams[0] = re.sub("\*+", "*", entparams[0])
	for file in list(dirpath.glob(entparams[0])):
		if isinstance(suffix, str) and file.suffix != suffix: continue
		if isinstance(suffix, list) and file.suffix not in suffix: continue
		if file.suffix == '.coord':
			with open(file) as lpts: coordls = json.load(lpts)
			retval['data'].append('File name: ' + file.name + ', Frames: ' + str(len(coordls['pixel'])))
		else:
			retval['data'].append(file.name)
	return retval

def exec_save_coords (entparams = [], appsetup = {}, coord = [], revert = 0):
	if entparams[0] == '': entparams[0] = '0, -120, 0'
	if entparams[1] == '': entparams[1] = '0, 0, 0'
	if entparams[2] == '': return 1
	filename = Path(appsetup['project']['name']) / 'coords' / entparams[2]
	if filename.suffix != '.coord': filename = Path(appsetup['project']['name']) / 'coords' / (entparams[2]+'.coord')
	jsondat = {'campos': entparams[0], 'bcenter': entparams[1], 'pixel': json.loads(coord), 'coord': []}
	if revert == 0: jsondat['pixel'].append (jsondat['pixel'][len(jsondat['pixel'])-1])
	with open(filename, "w") as lpts: json.dump(jsondat, lpts)
	os.system('ppython p3dcoords.py ' + str(filename))
	if revert == 0: return 1
	with open(filename) as lpts: coordls = json.load(lpts)
	return list(map(str, coordls['coord']))

def exec_open_coords (entparams = [], appsetup = {}, jskey = 'pixel'):
	if entparams[0] == '': return 1
	filename = Path(appsetup['project']['name']) / 'coords' / entparams[0]
	if filename.suffix != '.coord': filename = Path(appsetup['project']['name']) / 'coords' / (entparams[0]+'.coord')
	with open(filename) as lpts: coordls = json.load(lpts)
	print (coordls)
	if jskey == 'all': return coordls
	return coordls[jskey]

def exec_merge_coords (entparams = [], appsetup = {}):
	fdata = [None, None, None]
	def fixinitemlist (lfrom = 1, linto = 1):
		retval = [0]
		for ix in range(1, linto):
			fix = round(ix*(lfrom/(linto-1)), 0)
			retval.append(int(fix))
		return retval
	for ix in range(0,3):
		if entparams[ix] == '': return 2
		fdata[ix] = exec_open_coords (entparams = [entparams[ix], '', ''], appsetup = appsetup, jskey = 'coord')
		fdata[ix].pop()
	datalen = min(len(fdata[0]), len(fdata[1]), len(fdata[2]))
	itemls = [None, None, None]
	for ix in range(0,3):
		itemls[ix] = fixinitemlist (lfrom = len(fdata[ix])-1, linto = datalen)
	coordjs = {'X_coord': entparams[0], 'Y_coord': entparams[1], 'Z_coord': entparams[2], 'coord': []}
	for ix in range(0, datalen):
		X_coord = fdata[0][itemls[0][ix]][0]
		Y_coord = fdata[1][itemls[1][ix]][1]
		Z_coord = fdata[2][itemls[2][ix]][2]
		coordjs['coord'].append([X_coord, Y_coord, Z_coord])
	filename = Path(appsetup['project']['name']) / 'coords' / ("+".join(entparams)+'.coord')
	with open(filename, "w") as lpts: json.dump(coordjs, lpts)
	return 1

def exec_transform_coords (entparams = [], appsetup = {}):
	if entparams[0] == '': return 1
	if entparams[1] == '': entparams[1] = appsetup['project']['canvas']
	if entparams[2] == '': entparams[2] = appsetup['project']['winsize']
	framerunparams (entparams = entparams, appsetup = appsetup)
	canw, canh = getscreensize (entparams[1], 500, 500)
	winw, winh = getscreensize (entparams[2], 500, 500)
	nratio = max(winw, winh)/min(winw, winh)
	pixels = exec_open_coords (entparams = entparams, appsetup = appsetup, jskey = 'pixel')
	npixels = []
	for pixel in pixels:
		rwpix, rhpix = 250+int((pixel[0]-250)*nratio), 250+int((pixel[1]-250)*nratio)
		print ("from pixel to rwpix, rhpix", pixel, rwpix, rhpix)
		npixels.append([rwpix, rhpix])
	nfile = 'T_' + entparams[0]
	exec_save_coords (entparams = ['', '', nfile], appsetup = appsetup, coord = str(npixels), revert = 0)

def exec_save_merge (entparams = [], appsetup = {}):
	for ix in range(0,3):
		if entparams[ix] == '': return 2
	audio = Path(appsetup['project']['name']) / 'audio' / entparams[0]
	video = Path(appsetup['project']['name']) / 'video' / entparams[1]
	merge = Path(appsetup['project']['name']) / 'video' / entparams[2]
	if merge.suffix == '': merge = Path(appsetup['project']['name']) / 'video' / (entparams[2]+video.suffix)
	cmdstr = "ffmpeg -i " + video.name + " -i " + aidio.name + " -c:v copy -map 0:v:0 -map 1:a:0 " + merge.name
	os.system(cmdstr)
	return 1

def exec_fork_project (entparams = [], appsetup = {}):
	if entparams[0] == '': return 2
	shutil.copytree(Path(appsetup['project']['name']), entparams[0])
	shutil.rmtree(entparams[0]+'video')
	shutil.rmtree(entparams[0]+'audio')
	shutil.rmtree(entparams[0]+'rushes')
	os.mkdir(entparams[0]+'video')
	os.mkdir(entparams[0]+'audio')
	os.mkdir(entparams[0]+'rushes')
	os.mkdir(entparams[0]+'rushes/temp')
	return 1
	
def showstories (portf_dir_str):
	retval = ''
	for file in portf_dir.iterdir():
		if file.suffix != '.txt': continue
		retval = retval + file.name + "\n"
	return retval

def response_textplay (animurl, headers, cuniverse, story, democheck):
	if democheck == 1:
		return {'cmdlets': [{'bspec': {'locupto': [], 'locfrom': [], 'locpos': [0.0, 2.0, 7.0, 0.0, 0.0, 0.0, 75.0, 50.0, 50.0], 'locfile': '', 'sttmts': [], 'frames': [1, 120], 'oid': 303}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_named', 'params': {'modid': 1, 'weight': 1, 'isnew': 1}, 'frames': [1, 120]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [], 'locfile': 'somelist1', 'sttmts': [], 'frames': [61, 120], 'oid': 304}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_exists', 'params': {'modid': 2, 'weight': 1, 'isnew': 1}, 'frames': [61, 120]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [], 'locfile': '', 'sttmts': [], 'frames': [121, 150], 'oid': 310}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_exists', 'params': {'modid': 1, 'weight': 4, 'isnew': 0}, 'frames': [121, 150]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [], 'locfile': '', 'sttmts': [], 'frames': [], 'oid': 306}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_named', 'params': {'modid': 3, 'weight': 1, 'isnew': 1}, 'frames': [151, 271]}, {'bspec': {'locupto': [21.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0], 'locfrom': [-21.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0], 'locpos': [], 'locfile': '', 'sttmts': [], 'frames': [61, 120], 'oid': 307}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_does', 'params': {'modid': 3, 'weight': 6, 'isnew': 0, 'type': 'acts', 'func': 'run', 'repeat': 0}, 'frames': [61, 120]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [], 'locfile': 'Y_driveaway', 'sttmts': [], 'frames': [1, 60], 'oid': 308}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_does', 'params': {'modid': 4, 'weight': 4, 'isnew': 1, 'type': 'move', 'func': 'move', 'repeat': 0}, 'frames': [1, 60]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [-21.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0], 'locfile': '', 'sttmts': [], 'frames': [], 'oid': 309}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_exists', 'params': {'modid': 5, 'weight': 2, 'isnew': 1}, 'frames': [272, 392]}], 'rushobjlst': [{'file': 'camera', 'acts': {}, 'syns': ['camera'], 'jjrb': [], 'move': ['move', 'locate', 'looks'], 'joint': '', 'type': 'move'}, {'file': 'earth', 'acts': {}, 'syns': ['earth'], 'jjrb': [], 'move': ['move', 'locate', 'l'], 'joint': '', 'rname': 'Mypicture'}, {'file': 'line', 'acts': {}, 'syns': ['line'], 'jjrb': [], 'move': ['draw'], 'joint': ''}, {'file': 'lady', 'acts': {'run': {'fstart': 1, 'flast': -1}}, 'syns': ['lady'], 'jjrb': [], 'move': ['move', 'moving', 'moved', 'locate', 'located', 'locating', 'vanish', 'vanished', 'vanishing'], 'joint': {'legs': {'include': ['LHipJoint', 'RHipJoint'], 'exclude': []}, 'hand': {'include': ['LeftShoulder', 'RightShoulder'], 'exclude': []}, 'head': {'include': ['Neck'], 'exclude': ['LHipJoint', 'RHipJoint']}}, 'rname': 'Ruchika'}, {'file': 'SUVfront', 'acts': {}, 'syns': ['SUV'], 'jjrb': ['front', 'front facing'], 'move': ['move', 'locate', 'l'], 'joint': ''}, {'file': 'SUVfront', 'acts': {}, 'syns': ['SUV'], 'jjrb': ['front', 'front facing'], 'move': ['move', 'locate', 'l'], 'joint': ''}]}
	mydata=json.dumps({'story': story, 'universe': cuniverse})
	response = requests.post(animurl, headers=headers, data=mydata)
	animation = json.loads(response.text)
	return animation

def framerunparams (entparams = [], appsetup = {}):
	retval = {'fromfr': 1, 'tillfr': -1, 'fps': 1, 'width': 500, 'height': 500}
	retval['fromfr'] = 1 if forceint(entparams[0]) == -1 else forceint(entparams[0])
	retval['tillfr'] = 9999 if forceint(entparams[1]) == -1 else forceint(entparams[1])
	retval['fps'] = appsetup['project']['fps'] if forceint(entparams[2]) == -1 else forceint(entparams[2])
	retval['scrwide'], retval['scrhigh'] = getscreensize (appsetup['project']['winsize'], 500, 500)
	maxscr = max(retval['scrwide'], retval['scrhigh'])
	if maxscr <= 500: return retval
	retval['scrwide'], retval['scrhigh'] = int(retval['scrwide']*500/maxscr), int(retval['scrhigh']*500/maxscr)
	return retval

def exec_pic_export (entparams = [], appsetup = {}):
	if entparams[0] == '': return 1
	filenm = Path(appsetup['project']['name']) / 'video' / entparams[0]
	if filenm.suffix == '': filenm = Path(appsetup['project']['name']) / 'video' / (entparams[0] + '.gif')
	fps = appsetup['project']['fps'] if forceint(entparams[1]) == -1 else forceint(entparams[1])
	rushes = Path(appsetup['project']['name']) / "rushes"
	frange = entparams[2].split(",")
	fstart = int(frange[0].strip())
	flast = -1 if len(frange) == 1 else int(frange[1].strip())
	cmdstr = "ffmpeg -framerate " + str(fps) + " -start_number " + str(fstart) + " "
	if flast != -1:
		vlen = (flast+1 - fstart)/fps
		cmdstr = cmdstr + " -t " + str(vlen) + " "
	cmdstr = cmdstr + " -i " + str(rushes) + "/rush__%04d.png "
	print ("filenm", filenm, filenm.suffix, filenm.stem)
	if filenm.suffix in ['.mp4', '.mov']: cmdstr = cmdstr + " -pix_fmt yuv420p "
	cmdstr = cmdstr + str(filenm) + " -y"
	print ("cmdstr", cmdstr)
	os.system(cmdstr)
	return 1

def exec_pic_delete (entparams = [], appsetup = {}):
	rushes = Path(appsetup['project']['name']) / "rushes"
	for files in rushes.glob('*.png'):
		files.unlink()
	tempr = Path(appsetup['project']['name']) / "rushes" / "temp"
	for files in tempr.glob('*.png'):
		files.unlink()
	return 1

def getchanged (laststory, currstory, change):
	if change == 0: return 0
	lastarr = laststory.split("\n")
	currarr = currstory.split("\n")
	for ix, lasttx in enumerate(lastarr):
		if currarr[ix].strip() != lasttx.strip(): return ix
	return ix

def overwrites (imgdest, frindex, frlast, frixdel):
	for ix in range(1, frlast-frixdel+1):
		oimg = "pngs_"+"%04d"%(ix)+".png"
		nimg = "pngs_"+"%04d"%(ix+frixdel)+".png"
		os.remove(imgdest+nimg)
		os.rename(imgdest+'/temp/'+oimg, imgdest+nimg)

def savecoordas (fname, coordstxt, portf_dir_str):
	portf_dir = Path(portf_dir_str)
	if fname == '': return 1
	if not fname.startswith('Y_'):
		fname = 'Y_' + fname
	if not fname.endswith('.txt'): fname = fname+'.txt'
	saveas = portf_dir / 'coords' / fname
	filejs = {'pixel': json.loads(coordstxt), 'coord': []}
	filejs['pixel'].append (filejs['pixel'][len(filejs['pixel'])-1])
	with open(saveas, "w") as lpts: json.dump(filejs, lpts)
	os.system('ppython p3dcoords.py ' + str(saveas))
	return 1

def readcoordof (fname, portf_dir_str):
	fromf = Path(portf_dir_str) / 'coords' / fname
	with open(fromf) as lpts: filestr = json.load(lpts)
	return filestr['pixel']

def showscoords (portf_dir_str):
	retval = ''
	portf_dir = Path(portf_dir_str) / 'coords'
	for file in portf_dir.iterdir():
		if not file.name.startswith('X_') and not file.name.startswith('Y_') and not file.name.startswith('Z_'): continue
		if file.suffix != '.txt': continue
		retval = retval + file.name + "\n"
	return retval

def save3dcoord (fname, portf_dir_str):
	files = fname.split(',')
	sourcef, addingf = 'portfolio/coords/'+files[0].strip(), 'portfolio/coords/'+files[1].strip()
	srcnm, addnm = files[0].strip()[:2], files[1].strip()[:2]
	print(sourcef, addingf, srcnm, addnm)
	if srcnm not in ['X_', 'Y_', 'Z_'] or addnm not in ['X_', 'Y_', 'Z_']: return 2
	with open(sourcef) as lpts: srcdata = json.load(lpts)
	with open(addingf) as lpts: adddata = json.load(lpts)
	print("AAA", srcdata, adddata)
	if srcnm == addnm:
		srcdata['pixel'].extend(adddata['pixel'])
		srcdata['coord'].extend(adddata['coord'])
		with open(sourcef, "w") as lpts: json.dump(srcdata, lpts)
		return 1
	f3dlist = []
	for sx, pt3d in enumerate(srcdata['coord']):
		if sx < len(adddata['coord']):
			if srcnm == 'X_': f3dlist.append([adddata['coord'][sx][0], srcdata['coord'][sx][0], srcdata['coord'][sx][1]])
			if srcnm == 'Y_': f3dlist.append([srcdata['coord'][sx][0], adddata['coord'][sx][0], srcdata['coord'][sx][1]])
			if srcnm == 'Z_': f3dlist.append([srcdata['coord'][sx][0], srcdata['coord'][sx][0], adddata['coord'][sx][0]])
		else:
			if srcnm == 'X_': f3dlist.append([0, srcdata['coord'][sx][0], srcdata['coord'][sx][1]])
			if srcnm == 'Y_': f3dlist.append([srcdata['coord'][sx][0], 0, srcdata['coord'][sx][1]])
			if srcnm == 'Z_': f3dlist.append([srcdata['coord'][sx][0], srcdata['coord'][sx][0], 0])
	f3dfile = 'portfolio/coords/3d__' + files[0].strip()[2:][:4] + "__" + files[1].strip()[2:][:4] + '.txt'
	print(f3dfile)
	with open(f3dfile, "w") as lpts: json.dump(f3dlist, lpts)
	return 1

def logit (logtext, inputlog):
	if isinstance(inputlog, str):
		logtext.insert('end', inputlog)

def getlvllists (level = 1, boarditems = {}, sel = 0):
	retval = []
	print('se', sel)
	def getlvllists_1 (boarditems = boarditems):
		retval = []
		for items in enumerate(boarditems.keys()):
			retval.append(items)
			return retval
	if level == 1: return getlvllists_1 (boarditems = boarditems)
	return retval
		