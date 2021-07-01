import pip
from pathlib import Path
import shutil
import platform
import os
import subprocess
import sys

required_modules = [
    'requests',
    'pillow',
    'opencv-python',
    'matplotlib',
    'numpy',
    'winshell'
]

file_copyadd = [
    {'file': 'appsetup.js'},
    {'file': 'verbforms.js'},
    {'file': 'imgs', 'folder': 1},
    {'file': 'basicproject', 'folder': 1},
    {'file': 'ibrt', 'folder': 1},
    {'file': 'pyui.py'},
    {'file': 'pytkui.py'},
    {'file': 'pyback.py'},
    {'file': 'imagings.py'},
    {'file': 'p3dfunc.py'},
    {'file': 'p3dpreview.py'},
    {'file': 'p3dcoords.py'}
]

shortcuts = [{'from': 'pyui.py', 'exec': 'Memeer.lnk'}]

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    return 0

for package in required_modules:
    install(package)

try:
    inpath = input("Path for installation of MeMeer: ")
    install_path = Path(inpath) / 'memeer'
    print (f"install_path is {install_path}")
    install_path.mkdir(parents=True, exist_ok=True)
except:
    print ("Meme'er cannot be installed at the location")
    exit (1)

for file_item in file_copyadd:
    if 'folder' in file_item and file_item['folder'] == 1:
        dstdir = install_path / file_item['file']
        if dstdir.is_dir(): shutil.rmtree(install_path / file_item['file'])
        shutil.copytree(file_item['file'], str(install_path / file_item['file']))
    else:
        shutil.copy(file_item['file'], str(install_path / file_item['file']))

print ("Installation is completed!")
python_path = sys.executable
for filename in shortcuts:
    if platform.system() == ['Linux', 'Darwin']:    #Set this as binary
        file = install_path / filename['exec']
        file.write_text(python_path + ' ' + filename['from'])
        file.chmod(0o777)
    elif platform.system() == 'Windows':            #Set desktop shortcut
        import winshell
        import pythoncom
        from win32com.client import Dispatch
        desktop = winshell.desktop()
        path = os.path.join(desktop, filename['exec'])
        target = python_path
        args = ' ' + str(install_path / filename['from'])
        wDir = str(install_path)
        icon = str(install_path / 'imgs/logo.ico')
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.Arguments = args
        shortcut.IconLocation = icon
        shortcut.save()    
print ("Setting of softlinks/ shortcuts completed!")
print ("Please run the test demo scripts to make sure your system is all set to use Meme\'er!")
