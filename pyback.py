import os
from pathlib import Path
import json
import re

import requests
univfile = 'portfolio/universe.js'
conffile = 'localuser.js'

def port_conf_save (uielems, lconf, univ):
	lconf['user_idnt'] = uielems['user'].get()
	lconf['secrettxt'] = uielems['pkey'].get()
	lconf['portf_dir'] = uielems['wdir'].get()
	putlocaluser (lconf)
	univ['namedetail'] = uielems['desc'].get()
	putUniverseJS (univ)

def saveuniv(what, citemls):
	nuniv = getUniverseJS ()
	nuniv[what] = citemls
	putUniverseJS (nuniv)

def getlocaluser ():
	global conffile
	with open(conffile) as lujs: luser = json.load(lujs)
	return luser

def putlocaluser (lconf):
	global conffile
	with open(conffile, "w") as lujs: json.dump(lconf, lujs)
	return 1

def getUniverseJS ():
	global univfile
	with open(univfile) as lujs: univ = json.load(lujs)
	return univ

def putUniverseJS (univ):
	global univfile
	with open(univfile, "w") as lujs: json.dump(univ, lujs)
	return 1

def savethedata(lportui):
	print(lportui['desc'].get())
	return 1

def getUniverseData (user, portf_dir_str):
	portf_dir = Path(portf_dir_str)
	universe = portf_dir / 'universe.js'
	# Start reading basic setup at directory
	with universe.open('r') as univjs: univ = json.load(univjs)
	if 'namedetail' not in univ or univ['namedetail'] == '':
		univ['namedetail'] = 'Basic environment for create at '+portf_dir_str+' for user '+user
	model_dir = portf_dir / 'model'
	actor_dir = portf_dir / 'actor'
	# Start checking for models and actions
	if 'actions' not in univ: univ['actions'] = []
	if 'objects' not in univ: univ['objects'] = []
	## First setup the actions
	for func in ['move', 'locate', 'say']:
		if len(list(filter(lambda x : 'func' in x and x['func'] == func, univ['actions']))) == 0:
			univ['actions'].append({'jjrb': ['slow', 'quick'], 'syns': [func], 'func': func})
	## Check for camera and pronouns
	def setup_object (objname):
		for object in univ['objects']:
			if len(list(filter(lambda x : x['file'] == objname, object['model']))) > 0: return 1
		newobj = {}
		if objname == 'camera':
			newobj = {'syns': ['camera', 'viewer', 'looker', 'onlooker'], 'move': ['look', 'move', 'locate'], 'acts': [],
				'jjrb': [], 'xyz': [0, -30, 0], 'hpr': [0, 0, 0], 'lbh': [1, 1, 1], 'acts': [], 'model': [{'file': 'camera', 'jjrb': []}]}
		elif objname == '__blank__':
			newobj = {'syns': ['there', 'it', 'that'], 'move': [], 'jjrb': [], 'acts': [],
				'xyz': [0, 0, 0], 'hpr': [0, 0, 0], 'lbh': [1, 1, 1], 'acts': [], 'model': [{'file': '__blank__', 'jjrb': []}]}
		else:
			newobj = {'syns': [objname], 'move': ['look', 'move', 'locat', 'say'], 'jjrb': [], 'acts': [],
							'xyz': [0, 0, 0], 'hpr': [0, 0, 0], 'lbh': [1, 1, 1], 'model': [{'file': objname, 'jjrb': []}]}
			for action in actor_dir.glob('action/'+objname+'__*.egg'):
				basefile = action.stem
				actname = re.sub(objname+'__', '', basefile)
				if actname == basefile: continue
				newobj['acts'].append({actname: {'jjrb': [], 'speed': 1, 'fstart': 0, 'flast': 1}})
				if len(list(filter(lambda x : 'actf' in x and x['actf'] == actname, univ['actions']))) > 0: continue
				univ['actions'].append({'jjrb': ['slow', 'quick'], 'syns': [], 'func': actname})
		univ['objects'].append(newobj)
	# Check for each model now
	setup_object ('camera')
	setup_object ('__blank__')
	for model in model_dir.glob('*.egg'): setup_object (model.stem)
	for actor in actor_dir.glob('*.egg'): setup_object (actor.stem)
	# Additional components
	if 'logicals' not in univ: univ['logicals'] = []
	if 'functions' not in univ: univ['functions'] = {}
	if 'camerafocus' not in univ['functions']: univ['functions']['camerafocus'] = [{'tag': 'text', 'texts': ['camera looks']}]
	if 'objectlay' not in univ['functions']: univ['functions']['objectlay'] = [{'tag': 'text', "texts": ["it is pic"]}, {'tag': "singl", "texts": ["tree stand", "car parked", "pic say", "stool lay"]}]
	if 'actordoes' not in univ['functions']: univ['functions']['actordoes'] = [{"tag": "text","texts": ["lady walk"]}]
	if 'objectmov' not in univ['functions']: univ['functions']['objectmov'] = [{'tag': 'text', 'texts': ['car move']}, {'tag': 'wrate', 'texts': ['table thrown slowly']}]
	# update the values in universe
	with universe.open('w') as univjs: json.dump(univ, univjs)
	return univ

def savestoryas (fname, storytxt, portf_dir_str):
	portf_dir = Path(portf_dir_str)
	if fname == '': return 1
	fname = fname+'.txt'
	saveas = portf_dir / 'stories' / fname
	saveas.write_text(storytxt)
	return 1

def showstories (portf_dir_str):
	retval = ''
	portf_dir = Path(portf_dir_str) / 'stories'
	for file in portf_dir.iterdir():
		if file.suffix != '.txt': continue
		retval = retval + file.name + "\n"
	return retval

def showastory (fname, portf_dir_str):
	print(fname)
	fromf = Path(portf_dir_str) / 'stories' / fname
	return fromf.read_text()


def response_textplay (animurl, headers, cuniverse, mystory):
	animation = [{'line': 0, 'mmaps': {'0': [{'wt': 1, 'gmodel': 1, 'smodel': 0}], '2': [{'wt': 1, 'gmodel': 10, 'smodel': 0}]}, 'specs': {'locupto': [], 'locfrom': [], 'locpos': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'sttmts': [], 'frames': []}, 'fname': 'objectlay', 'ftag': 'text'}, {'line': 1, 'mmaps': {'0': [{'wt': 1, 'gmodel': 10, 'smodel': 0}], '1': [{'wt': 1, 'gmodel': 2, 'smodel': 0}]}, 'specs': {'locupto': [], 'locfrom': [], 'locpos': [], 'sttmts': ['"hello youong frinds"'], 'frames': [36, -1]}, 'fname': 'objectlay', 'ftag': 'singl'}, {'line': 2, 'mmaps': {'0': [{'wt': 1, 'gmodel': 10, 'smodel': 0}], '1': [{'wt': 1, 'gmodel': 2, 'smodel': 0}]}, 'specs': {'locupto': [0, 0, 0, 0, 0, 0, 4, 4, 4], 'locfrom': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'locpos': [], 'sttmts': ['"welcome to this animmation on far flung cltures of India"'], 'frames': []}, 'fname': 'objectlay', 'ftag': 'singl'}, {'line': 3, 'mmaps': {'0': [{'wt': 1, 'gmodel': 10, 'smodel': 0}], '1': [{'wt': 1, 'gmodel': 2, 'smodel': 0}]}, 'specs': {'locupto': [], 'locfrom': [], 'locpos': [], 'sttmts': ['"My name is Ahmad Balti and today, I will tell you about my Balti people"'], 'frames': [72, 144]}, 'fname': 'objectlay', 'ftag': 'singl'}, {'line': 4, 'mmaps': {'0': [{'wt': 1, 'gmodel': 18, 'smodel': 0}], '1': [{'wt': 1, 'gmodel': 5, 'smodel': 0}]}, 'specs': {'locupto': [], 'locfrom': [], 'locpos': [], 'sttmts': ['"and that is true"'], 'frames': [72, 144]}, 'fname': 'actordoes', 'ftag': 'text'}]
	return animation
	mydata=json.dumps({'mystory': mystory, 'universe': cuniverse})
	response = requests.post(animurl, headers=headers, data=mydata)
	animation = json.loads(response.text)
	return animation