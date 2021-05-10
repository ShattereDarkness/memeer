import os
from pathlib import Path
import json
import re
import shutil
import p3dfunc

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
		if file.suffix in ['.gif', '.mp4', '.mov', '.avi', '.wmv', '.webm']:
			exist = check2files (path1=media_dir, path2=model_dir, fstem=file.stem, suffix1=file.suffix, suffix2='.egg')
			if exist == 1:
				#try:
				os.mkdir('../media/' + file.stem)
				vfps = os.system("ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=r_frame_rate media/" + file.name)
				print ("vfps1", vfps)
				vfps = round(vfps)
				print ("vfps2", vfps)
				cmdstr = "ffmpeg -i ../media/" + file.name + " -vf scale=320:-1 -vsync 0 ../media/" + file.stem + "/series%4d.png"
				print ("cmdstr", cmdstr)
				os.system(cmdstr)
				#except: print ("Video "+file.stem+" is already parsed and will be reused")
				cmdstr = "egg-texture-cards -o " + file.stem + ".egg -fps "+str(vfps)+" ../media/" + file.stem + "/series*.png"
				os.system(cmdstr)
				retval['add'] = retval['add'] + 1
			if exist == 2:
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
	return {'code': 0, 'data': 'temp_rushframes'}

def exec_save_story (fname, projvars = {}):
	retval = {'code': 0, 'data': ''}
	portf_dir = Path(portf_dir_str) / 'stories'
	if fname == '': {'code': 1, 'data': ''}
	saveas = portf_dir / 'stories' / fname
	saveas.write_text(storytxt)
	return {'code': 1, 'data': ''}

def exec_open_story (fname, projvars = {}):
	if fname == '': return {'code': 1, 'data': ''}
	fromf = Path(portf_dir_str) / 'stories' / fname
	return {'code': 0, 'data': fromf.read_text()}

def exec_list_story (flike, projvars = {}):
	retval = {'code': 0, 'data': ''}
	portf_dir = Path(portf_dir_str) / 'stories'
	if flike == '': flike = '*'
	for file in list(portf_dir.glob(flike)):
		retval['data'].append(file.name)
	return retval

def exec_expo_story (fname, projvars = {}):
	if 'lastexec' not in projvars: return {'code': 101, 'data': ''}
	if fname == '': {'code': 1, 'data': ''}
	return {'code': 0, 'data': ''}

def exec_save_coords (fname, projvars = {}):
	retval = {'code': 0, 'data': ''}
	portf_dir = Path(portf_dir_str) / 'coords'
	if fname == '': {'code': 1, 'data': ''}
	saveas = portf_dir / 'coords' / fname
	saveas.write_text(storytxt)
	return {'code': 1, 'data': ''}

def exec_open_story (fname, projvars = {}):
	if fname == '': return {'code': 1, 'data': ''}
	fromf = Path(portf_dir_str) / 'coords' / fname
	return {'code': 0, 'data': fromf.read_text()}

def exec_list_story (flike, projvars = {}):
	retval = {'code': 0, 'data': ''}
	portf_dir = Path(portf_dir_str) / 'coords'
	if flike == '': flike = '*'
	for file in list(portf_dir.glob(flike)):
		retval['data'].append(file.name)
	return retval

def exec_expo_story (fname, projvars = {}):
	if 'lastexec' not in projvars: return {'code': 101, 'data': ''}
	if fname == '': {'code': 1, 'data': ''}
	return {'code': 0, 'data': ''}

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

def logit (logtext, input):
	if isinstance(input, str):
		logtext.insert('end', "Application logging------------------------------------\n")

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
		