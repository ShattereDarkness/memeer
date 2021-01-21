import os
from pathlib import Path
import json

def getUniverseData (user, portf_dir_str):
	portf_dir = Path(portf_dir_str)
	universe = portf_dir / 'universe.js'
	# Start reading basic setup at directory
	with universe.open('r') as univjs: univ = json.load(univjs)
	univ['description'] = 'Basic environment for create at '+portf_dir_str+' for user '+user
	model_dir = portf_dir / 'model'
	actor_dir = portf_dir / 'actor'
	# Start checking for models and actions
	if 'action' not in univ: univ['action'] = []
	if 'object' not in univ: univ['object'] = []
	## First setup the actions
	for func in ['move', 'locate']:
		if len(list(filter(lambda x : 'func' in x and x['func'] == func, univ['action']))) == 0:
			univ['action'].append({'jjrb': ['slow', 'quick'], 'syns': [func], 'func': func})
	## Check for camera and pronouns
	def setup_object (objname):
		for object in univ['object']:
			if len(list(filter(lambda x : x['file'] == objname, object['model']))) > 0: return 1
		newobj = {}
		if objname == 'camera':
			newobj = {'syns': ['camera', 'viewer', 'looker', 'onlooker'], 'move': ['look', 'move', 'locate'], 'acts': [],
				'jjrb': [], 'xyz': [0, -30, 0], 'hpr': [0, 0, 0], 'lbh': [1, 1, 1], 'acts': [], 'model': [{'file': 'camera', 'jjrb': []}]}
		elif objname == '__blank__':
			newobj = {'syns': ['there', 'it', 'that'], 'move': [], 'jjrb': [], 'acts': [],
				'xyz': [0, 0, 0], 'hpr': [0, 0, 0], 'lbh': [1, 1, 1], 'acts': [], 'model': [{'file': '__blank__', 'jjrb': []}]}
		else:
			newobj = {'syns': [], 'move': ['look', 'move', 'locat'], 'jjrb': [], 'acts': [],
							'xyz': [0, 0, 0], 'hpr': [0, 0, 0], 'lbh': [1, 1, 1], 'model': [{'file': objname, 'jjrb': []}]}
			for action in actor_dir.glob('action/'+objname+'__*.egg'):
				basefile = action.stem
				actname = re.sub(objname+'__', '', basefile)
				if actname == basefile: continue
				newobj['acts'].append({actname: {'jjrb': [], 'speed': 1, 'syns': [], 'fstart': 0, 'fdone': 1,
										'xyz': [0, 0, 0], 'hpr': [0, 0, 0], 'lbh': [1, 1, 1]}})
				if len(list(filter(lambda x : 'actf' in x and x['actf'] == actname, univ['action']))) > 0: continue
				univ['action'].append({'jjrb': ['slow', 'quick'], 'syns': [], 'actf': actname, 'speed': 1,
										'xyz': [0, 0, 0], 'hpr': [0, 0, 0], 'lbh': [1, 1, 1], 'fstart': 0, 'fdone': 1})
		univ['object'].append(newobj)
	# Check for each model now
	setup_object ('camera')
	setup_object ('__blank__')
	for model in model_dir.glob('*.egg'): setup_object (model.stem)
	for actor in actor_dir.glob('*.egg'): setup_object (actor.stem)
	# Additional components
	if 'logic_setup' not in univ: univ['logic_setup'] = []
	if 'functions' not in univ: univ['functions'] = {}
	if 'camerafocus' not in univ['functions']: univ['functions']['camerafocus'] = {'text': ['camera looks']}
	if 'objectlay' not in univ['functions']: univ['functions']['objectlay'] = {'text': ['tree stand', 'car parked', 'it is road', 'stool lay']}
	if 'objectmov' not in univ['functions']: univ['functions']['objectmov'] = {'text': ['car move'], 'wrate': ['table thrown slowly']}
	# update the values in universe
	with universe.open('w') as univjs: json.dump(univ, univjs)
	return univ