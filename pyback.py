import os
from pathlib import Path
import json
import re
import shutil

import requests
appfile = 'appsetup.js'

def port_conf_save (uielems, lconf, univ):
	lconf['user_idnt'] = uielems['user'].get()
	lconf['secrettxt'] = uielems['pkey'].get()
	lconf['portf_dir'] = uielems['wdir'].get()
	univfile = lconf['portf_dir'] + 'universe.js'
	putlocaluser (lconf)
	univ['namedetail'] = uielems['desc'].get()
	putUniverseJS (univ, univfile)

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
			exist = check2files (path1=Path('.'), path2=model_dir, fstem=file.stem, suffix1=file.suffix, suffix2='.egg')
			if exist == 1: ##create egg
				cmdstr = "egg-texture-cards -o " + file.stem + ".egg ../media/" + file.name
				os.system(cmdstr)
				retval['add'] = retval['add'] + 1
			if exist == 2:
				(model_dir / (file.stem+'.egg')).unlink()
				retval['rem'] = retval['rem'] + 1
		if file.suffix in ['.gif', '.mp4', '.mov', '.avi', '.wmv', '.webm']:
			exist = check2files (path1=Path('.'), path2=model_dir, fstem=file.stem, suffix1=file.suffix, suffix2='.egg')
			if exist == 1:
				os.mkdir('../media/' + file.stem)
				cmdstr = "ffmpeg -i ../media/" + file.name + " -vf fps="+str(fps)+" "+ ffmopt +" ../media/" + file.stem + "/series%4d.png"
				os.system(cmdstr)
				cmdstr = "egg-texture-cards -o " + file.stem + ".egg -fps 24 ../media/" + file.stem + "/series*.png"
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
		univ['objects'].append({'syns': [mfile.stem], 'move': ['move', 'locate', 'vanish'], 'jjrb': [], 'acts': {}, 'joint': '', \
							'file': mfile.stem, 'jjrb': []})
		retval['model']['add'] = retval['model']['add'] + 1
	univ['objects'] = list(filter(lambda x : 'saved' not in x or x['saved'] == 1, univ['objects']))
	print("univ['objects']", univ['objects'])
	uactions = []
	for afile in action_dir.glob('*.egg'):
		actor, anime = afile.stem.split ('__', 1)
		uactions.append(anime)
		print("actor, anime", actor, anime)
		if len(list(filter(lambda x : x['file'] == actor, univ['objects']))) == 0: continue
		if len(list(filter(lambda x : x['func'] == anime, univ['actions']))) == 0:
			univ['actions'].append({'jjrb': [], 'syns': [anime], 'func': anime, 'show': 1})
			retval['actions']['add'] = retval['actions']['add'] + 1
		mobject = list(filter(lambda x : x['file'] == actor, univ['objects']))[0]
		print("mobject", mobject)
		if anime not in mobject['acts']:
			mobject['acts'][anime] = {"fstart": 1, "flast": -1}
	if 'logicals' not in univ: univ['logicals'] = []
	if 'functions' not in univ: univ['functions'] = {}
	# update the values in universe
	print(retval)
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
			print("uword", uword)
			retval.append(uword)
			continue
		uword = uword[:-1]
		for fwords in verbjs:
			if not uword in fwords: continue
			retval.extend(fwords)
		retval.append(uword)
	retval=list(set(retval))
	return retval

def storyparse (story, gall = 0):
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
		if gall == 0 and sline == '': continue
		specs = getspecifics (sline)
		retval.append(specs)
	return retval

def exec_play_story (entparams = [], appsetup = {}, universe = {}, story = ''):
	if len(entparams) < 1: animfps = appsetup['winsize']
	if len(entparams) < 3:
		winsize = winsize.replace('X', 'x')
		scrwide = list(map(int, winsize.split('x')))[0]
		scrhigh = list(map(int, winsize.split('x')))[1]
	serialized = response_textplay (appsetup['meemerurl'], {'Content-type': 'application/json'}, universe, storyparse(story, gall = 1))
	cline = pyback.getchanged (gappvars['laststory'], storytext, change)
	os.system('ppython p3dpreview.py')
	appsetup['laststory'] = storytext
	appsetup['lastanime'] = pyback.framedesc (serialized)
	return {'code': 0, 'data': ''}

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

def response_textplay (animurl, headers, cuniverse, story):
	#return [{'line': 0, 'mmaps': {'0': [{'wt': 1, 'gmodel': 1, 'smodel': 0}], '2': [{'wt': 1, 'gmodel': 10, 'smodel': 0}]}, 'specs': {'locupto': [], 'locfrom': [], 'locpos': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'sttmts': [], 'frames': []}, 'fname': 'objectlay', 'ftag': 'text'}, {'line': 1, 'mmaps': {'0': [{'wt': 1, 'gmodel': 10, 'smodel': 0}], '1': [{'wt': 1, 'gmodel': 2, 'smodel': 0}]}, 'specs': {'locupto': [], 'locfrom': [], 'locpos': [], 'sttmts': ['"hello youong frinds"'], 'frames': [36, -1]}, 'fname': 'objectlay', 'ftag': 'singl'}, {'line': 2, 'mmaps': {'0': [{'wt': 1, 'gmodel': 10, 'smodel': 0}], '1': [{'wt': 1, 'gmodel': 2, 'smodel': 0}]}, 'specs': {'locupto': [0, 0, 0, 0, 0, 0, 4, 4, 4], 'locfrom': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'locpos': [], 'sttmts': ['"welcome to this animmation on far flung cltures of India"'], 'frames': []}, 'fname': 'objectlay', 'ftag': 'singl'}, {'line': 3, 'mmaps': {'0': [{'wt': 1, 'gmodel': 10, 'smodel': 0}], '1': [{'wt': 1, 'gmodel': 2, 'smodel': 0}]}, 'specs': {'locupto': [], 'locfrom': [], 'locpos': [], 'sttmts': ['"My name is Ahmad Balti and today, I will tell you about my Balti people"'], 'frames': [72, 144]}, 'fname': 'objectlay', 'ftag': 'singl'}, {'line': 4, 'mmaps': {'0': [{'wt': 1, 'gmodel': 18, 'smodel': 0}], '1': [{'wt': 1, 'gmodel': 5, 'smodel': 0}]}, 'specs': {'locupto': [], 'locfrom': [], 'locpos': [], 'sttmts': ['"and that is true"'], 'frames': [72, 144]}, 'fname': 'actordoes', 'ftag': 'text'}]
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
		