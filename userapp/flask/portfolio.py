import os
from pathlib import Path
import shutil
from importlib import import_module

parent_wd = Path(os.getcwd()).parent)
portf_dir = parent_wd / 'portfolio'
universe = 'universe.py'

def portf_setup ():
	def setup_dirs (dir):
		if not dir.exists():
			dir.mkdir()
		elif not dir.is_dir():
			return {'Error': '"portfolio" exists but not as a directory!'}
		return {'Info': 'Done'}
	
	setup_dirs(portf_dir)
	envfile = portf_dir / universe
	if not envfile.is_file():
		with envfile.open() as f:
			f.write('description = "Blank file created"')
	setup_dirs(portf_dir / 'actor')
	setup_dirs(portf_dir / 'actor' / 'action')
	setup_dirs(portf_dir / 'media')
	setup_dirs(portf_dir / 'model')
	setup_dirs(portf_dir / 'model' / 'pngs')

def check_media ():
	media_dir = portf_dir / 'media'
	model_dir = portf_dir / 'model'
	for media in media_dir.iterdir():
		suffx = PurePosixPath(media).suffix
		if suffx in ['.jpg', '.jpeg', '.png', '.tif', '.mov', '.gif', '.webm']:
			model = Path ('model/' + PurePosixPath(media).stem + '.egg')
			if not model.is_file():
				shutil.copy2 (media, model)
				if suffx in ['.jpg', '.jpeg', '.png', '.tif']:
					os.system("egg-texture-cards -o model/{}.egg model/{}{}".format(PurePosixPath(media).stem, suffx))
				if suffx in ['.mov', '.gif', '.webm']:
					os.system("ffmpeg -i model/{}.{} -vf fps=1 model/pngs/{}%04d.png".format(PurePosixPath(media).stem, suffx, PurePosixPath(media).stem))
					os.system("egg-texture-cards -o model/{}.egg model/pngs/{}*.png".format(PurePosixPath(media).stem, PurePosixPath(media).stem))
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

def universe (memeer):
	univ = import_module(portf_dir+universe)
	univ.description = 'Basic environment for create on host '+memeer['host']+' for user '+memeer['identity']
	
