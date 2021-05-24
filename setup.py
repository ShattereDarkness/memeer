import pip
from pathlib import Path
import shutil
import platform
import os
import sys

required_modules = [
	'requests',
	'pillow',
	'opencv-python',
	'matplotlib',
	'numpy',
	'mrcnn',
	'winshell'
]

file_copyadd = [
	{'file': 'appsetup.js'},
	{'file': 'verbforms.js'},
	{'file': 'icon.png'},
	{'file': 'demo', 'folder': 1},
	{'file': 'pyui.py'},
	{'file': 'pytkui.py'},
	{'file': 'pyback.py'},
	{'file': 'imagings.py'},
	{'file': 'p3dfunc.py'},
	{'file': 'p3dpreview.py'},
	{'file': 'p3dcoords.py'},
	{'file': 'mrcnn/model.py', 'module': 'mrcnn'}
]

shortcuts = [{'from': 'pyui.py', 'exec': 'memeer'}]

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])
	return 0

for package in required_modules:
	install(package)

inpath = input("Path for installation of MeMeer: ")
install_path = Path(inpath)
install_path.mkdir(parents=True, exist_ok=True)

for file_item in file_copyadd:
	if 'module' in file_item:
		module = __import__(file_item['module'])
		module_path = Path(module.__file__).parent
		shutil.copy(file_item['file'], str(module_path / file_item['file']))
	else:
		shutil.copy(file_item['file'], str(install_path / file_item['file']))

python_path = sys.executable
for filename in shortcuts:
	if platform.system() == ['Linux', 'Darwin']:	#Set this as binary
		file = install_path / filename['exec']
		file.write_text(python_path + ' ' + filename['from'])
		file.chmod(0o744)
	elif platform.system() == 'Windows':			#Set desktop shortcut
		import winshell
		from win32com.client import Dispatch
		desktop = winshell.desktop()
		path = os.path.join(desktop, "MeMeer.lnk")
		target = python_path + ' ' + install_path + '\\pyui.py'
		wDir = install_path
		icon = install_path + '\\icon.png'
		shell = Dispatch('WScript.Shell')
		shortcut = shell.CreateShortCut(path)
		shortcut.Targetpath = target
		shortcut.WorkingDirectory = wDir
		shortcut.IconLocation = icon
		shortcut.save()	
print ("Installation is completed!")
print ("Please run the test demo scripts to make sure your system is all set to use MeMeer!")
