import os
from pathlib import Path
import shutil
from importlib import import_module

parent_wd = Path(os.getcwd()).parent
portf_dir = parent_wd / 'portfolio'
universe = 'universe.py'

def portf_setup ():
	def setup_dirs (dir):
		if not dir.exists():
			dir.mkdir()
		elif not dir.is_dir():
			return {'Error': '"portfolio" exists but not as a directory!'}
		return {'Info': 'Done'}
	# Setup al drectories
	setup_dirs(portf_dir)
	envfile = portf_dir / universe
	if not envfile.is_file():
		with envfile.open('w') as f:
			f.write("description = 'Blank file created'\n")
		f.close()
	setup_dirs(portf_dir / 'actor')
	setup_dirs(portf_dir / 'actor' / 'action')
	setup_dirs(portf_dir / 'media')
	setup_dirs(portf_dir / 'model')
	setup_dirs(portf_dir / 'model' / 'pngs')

def check_media ():
	media_dir = portf_dir / 'media'
	model_dir = portf_dir / 'model'
	for media in media_dir.iterdir():
		if media.suffix not in ['.jpg', '.jpeg', '.png', '.tif', '.mov', '.gif', '.webm']: continue
		model = Path (str(model_dir) + '/' + media.stem + '.egg')
		if model.is_file(): continue
		if media.suffix in ['.jpg', '.jpeg', '.png', '.tif']:
			os.system("cp {}/{} {}/pngs/".format(str(media_dir), media.name, str(model_dir)))
			os.system("cd {}; egg-texture-cards -o {}.egg pngs/{}".format(str(model_dir), media.stem, media.name))
		if media.suffix in ['.mov', '.gif', '.webm']:
			os.system("ffmpeg -i {}/{}{} -vf fps=24 {}/pngs/{}%04d.png".format(str(media_dir), media.stem, media.suffix, str(model_dir), media.stem))
			os.system("cd {}; egg-texture-cards -o {}.egg pngs/{}*.png".format(str(model_dir), media.stem, media.stem))
	return 1

def refresh_media (wildcard):
	media_dir = portf_dir / 'media'
	model_dir = portf_dir / 'model'
	for media in sorted(Path(media_dir).glob(wildcard):
		media_stem = media.stem
		for pngf in sorted(Path(model_dir / 'pngs').glob(media.stem+'*'):
			pngf.unlink()
		for modelf sorted(Path(model_dir).glob(media.stem+'*'):
			modelf.unlink()
	check_media ()
	return 1

def review_universe (memeer, universe):
	univ = import_module(portf_dir+universe)
	univ.description = 'Basic environment for create on host '+memeer['host']+' for user '+memeer['identity']
	
	model_dir = portf_dir / 'model'
	if 'objects' not in universe: universe['objects'] = []
	if len(list(filter(lambda x : x['model'] == 'camera', universe['objects']))) == 0:
		universe['objects'].append ({'syns': ['camera', 'viewer', 'looker', 'onlooker'], 'move': {'look', 'move', 'locate'},
										'xyz': [0, -30, 0], 'models': 'camera'})
	if len(list(filter(lambda x : x['model'] == '__blank__', universe['objects']))) == 0:
		universe['objects'].append ({'syns': ['there', 'it', 'that'], 'models': '__blank__'})
	
	for model in model_dir.iterdir():
		modname = model.stem()
		for object in universe['objects']:
			if len(list(filter(lambda x : x['model'] == modname, object['models']))) == 0:
				universe['objects'].append ({'syns': [modname], 'move': ['look', 'move', 'locat'], 'models': [{'file': 'model/'+modname}], 'xyz': [0, 0, 1]})
	
	if 'actions' not in universe:
		universe['actions'] = []
	if len(list(filter(lambda x : x['actf'] == 'locate', universe['actions']))) == 0:
		universe['actions'].append ({ 'syns': ['look', 'locate'], 'func': 'locate' })
	if len(list(filter(lambda x : x['actf'] == 'move', universe['actions']))) == 0:
		universe['actions'].append ({ 'jjrb': ['slow', 'quick', 'bezier', 'natural'], 'syns': ['move'], 'func': 'move' })
	
	if 'logic_setup' not in universe: universe['logic_setup'] = []
	
	if 'functions' not in universe: universe['functions'] = {}
	if 'camerafocus' not in universe['functions']: universe['functions']['camerafocus'] = {'text': ['camera looks']}
	if 'objectlay' not in universe['functions']: universe['functions']['objectlay'] = {'text': ['tree stand', 'car parked', 'it is road', 'stool lay']}
	if 'objectmov' not in universe['functions']: universe['functions']['objectmov'] = {'text': ['car move'], 'wrate': ['table thrown slowly']}
	
	return universe

def write_universe (universe):
	envfile = portf_dir / universe
	with envfile.open() as f:
		for key in ['description', 'objects', 'actions', 'logic_setup', 'functions']:
			f.write(key+' = '+pprint.pformat(universe[key]))
	f.close()

