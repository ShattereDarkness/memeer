#import tkinter and ttk modules
import tkinter
import tkinter.filedialog
from tkinter import ttk
from tksheet import Sheet

import json
import requests
import os

import p3dfunc
import pyback
import pytkui
from PIL import ImageTk, Image

import threading
import time

headers = {'Content-type': 'application/json'}
animurl = 'http://localhost:5000/getanim'
stopauto = 0

#Make the root widget
root = tkinter.Tk()
root.geometry("950x650")
nb = ttk.Notebook(root)
nb.pack()

#univ = pyback.getUniverseData (lconfui['user_idnt'].get(), lconfui['portf_dir'].get())
univ = pyback.getUniverseJS ()
lconf = pyback.getlocaluser()

lportui = {}
frame_conf = pytkui.addstdframe (nb, "User Local Configuration")
pytkui.lconfuisetup (lconf, univ, frame_conf, lportui)

lportui['acts'] = []
frame_acts = pytkui.addcnvframe (nb, "Portfolio Actions")
pytkui.lactsuisetup (univ['actions'], frame_acts, lportui['acts'])

lportui['objs'] = []
frame_objs = pytkui.addcnvframe (nb, "Portfolio Objects")
pytkui.lobjsuisetup (univ['objects'], frame_objs, lportui['objs'])

lportui['logix'] = []
frame_logix = pytkui.addcnvframe (nb, "Logical Functions")
pytkui.llogixuisetup (univ['logicals'], frame_logix, lportui['logix'])

lportui['funcs'] = []
frame_funcs = pytkui.addcnvframe (nb, "Panda3dUI Functions")
pytkui.lfuncsuisetup (univ['functions'], frame_funcs, lportui['funcs'])

def savethedata(*args):
	nuniv = {}
	nuniv['description'] = rentries['description'].get()
	nuniv['action'] = []
	for action in rentries['action']:
		syns = action['syns'].get()
		jjrb = action['jjrb'].get()
		if 'func' in action:
			nuniv['action'].append({'func': action['func'], 'syns': action['syns'].get(), 'jjrb': action['jjrb'].get()})
			continue
		if 'actf' not in action: continue
		nuniv['action'].append({'actf': action['actf'], 'syns': action['syns'].get(), 'jjrb': action['jjrb'].get(),
								'xyz': action['xyz'].get(), 'hpr': action['hpr'].get(), 'lbh': action['lbh'].get(),
								'speed': action['speed'].get(), 'fstart': action['fstart'].get(), 'fdone': action['fdone'].get()})
	nuniv['object'] = []
	for object in rentries['object']:
		nobject = {'syns': object['syns'].get(), 'jjrb': object['jjrb'].get(), 'move': object['lbh'].get(),
					'xyz': object['xyz'].get(), 'hpr': object['hpr'].get(), 'lbh': object['lbh'].get(), 'model': [], 'acts': []}
		for model in object['model']:
			nobject['model'].append({'file': model['file'], 'jjrb': model['jjrb'].get()})
		for acts in object['acts']:
			nobject['acts'].append({'syns': acts['syns'].get(), 'jjrb': acts['jjrb'].get(),
									'xyz': acts['xyz'].get(), 'hpr': acts['hpr'].get(), 'lbh': acts['lbh'].get(),
									'speed': acts['speed'].get(), 'fstart': acts['fstart'].get(), 'fdone': acts['fdone'].get()})
		nuniv['object'].append(nobject)
	nuniv['logic'] = []
	for logic in rentries['logic']:
		nlogic = {'curr': logic['curr'].get(), 'updt': logic['updt'].get()}
		if len(nlogic['updt']) > 0: nuniv['logic'].append(nlogic)
	nuniv['funcs'] = {}
	for fncname, fncdet in rentries['funcs'].items():
		nuniv['funcs'][fncname] = []
		for fnctag, fnctext in fncdet.items():
			nuniv['funcs'][fncname].append({'tag': fnctag, 'texts': fnctext.get()})
	print (nuniv)

def savePosn(event):
	global lastx, lasty
	lastx, lasty = event.x, event.y
	print (lastx, lasty)

def addLine(event):
	canvas.create_line((lastx, lasty, event.x, event.y))
	savePosn(event)

def autoplayfunc(pnglst):
	print("Thread starting")
	canvas.delete("all")
	global stopauto
	for png in pnglst:
		image = Image.open(png)
		image = image.resize((350, 250), Image.ANTIALIAS)
		myimg = ImageTk.PhotoImage(image)
		canvas.create_image(10, 10, image=myimg, anchor='nw')
		if stopauto == 1:
			stopauto = 0
			exit()
		time.sleep(1)

def playall ():
	mystory={"mystory": 'it is Outsideview "Primordial thing in here: beauty, lots of it" #8 @(0,0,0,0,0,0,1,1,1)'}
	#mystory={"mystory": storybox.get("1.0", "end")}
	print (mystory)
	mystory=json.dumps(mystory)
	response = requests.post(animurl, headers=headers, data=mystory)
	animation = json.loads(response.text)
	serealize = p3dfunc.serealize(animation)
	p3dinput = {'title': 'Preview mode', 'serealize': serealize}
	with open("C:\ProgramData\Memeer\data.py", "w") as outfile: json.dump(p3dinput, outfile)
	os.system('ppython production.py')
	with open('C:\ProgramData\Memeer\data.py') as infile: p3dinput = json.load(infile)
	pnglst = p3dinput['pnglst']
	x = threading.Thread(target=autoplayfunc, args=(pnglst,)).start()
	return 1

def playatedit (*args):
	return 1

def playbetween (*args):
	return 1

def prvframe (*args):
	global stopauto
	stopauto = 1

def playpending (*args):
	return 1

# mframe_main = tkinter.Frame(nb)
# nb.add(mframe_main, text="Welcome to Meme'er")
# storybox = tkinter.Text(mframe_main, width=50, height=25)
# storybox.grid(column=0, row=0, columnspan=3)
# canvas = tkinter.Canvas(mframe_main, width=400, height=400, background='gray75')
# canvas.grid(column=3, row=0, columnspan=3)
# canvas.bind("<Button-1>", savePosn)
# canvas.bind("<B1-Motion>", addLine)
# image = Image.open('C:\ProgramData\Memeer\curstory\story_0007.png')
# image = image.resize((350, 250), Image.ANTIALIAS)
# myimg = ImageTk.PhotoImage(image)
# canvas.create_image(10, 10, image=myimg, anchor='nw')
# indexbox = tkinter.Text(mframe_main, width=11, height=25).grid(column=6, row=0, columnspan=2)
# ttk.Label(mframe_main, text=".    .    .    .    .    .    .    .").grid(column=1, row=1, columnspan=7)
# ttk.Label(mframe_main, text="C    O    N    T    R    O    L    S").grid(column=1, row=2, columnspan=7)
# ttk.Label(mframe_main, text="    .    .    .    .    .    .    .    ").grid(column=1, row=3, columnspan=7)

# ttk.Button(mframe_main, text="Start Full Play", command=playall).grid(column=1, row=4)
# ttk.Button(mframe_main, text="Start Play from Edit", command=playatedit).grid(column=1, row=5)
# mainplayfro = create_entry (framep=mframe_main, width=6, gridcolumn=0, gridrow=6, sticky='ne')
# ttk.Button(mframe_main, text="Show Between Frames", command=playbetween).grid(column=1, row=6)
# mainplaytil = create_entry (framep=mframe_main, width=6, gridcolumn=2, gridrow=6)

# ttk.Button(mframe_main, text="Previous Frame", command=prvframe).grid(column=3, row=4, sticky='ne')
# ttk.Button(mframe_main, text="Next Frame", command=prvframe).grid(column=4, row=4, sticky='ne')
# ttk.Button(mframe_main, text="Play at Speed", command=playpending).grid(column=3, row=5, sticky='ne')
# mainframspd = create_entry (framep=mframe_main, width=3, gridcolumn=4, gridrow=5, sticky='ne')
# ttk.Button(mframe_main, text="Between Frames", command=playbetween).grid(column=3, row=6, sticky='ne')
# mainframfro = create_entry (framep=mframe_main, width=3, gridcolumn=4, gridrow=6, sticky='ne')
# mainframtil = create_entry (framep=mframe_main, width=3, gridcolumn=5, gridrow=6, sticky='nw')

# mainindxnam = create_entry (framep=mframe_main, width=5, gridcolumn=6, gridrow=4)
# ttk.Button(mframe_main, text="Save Indexes", command=playbetween).grid(column=7, row=4)
# mainindxmrg = create_entry (framep=mframe_main, width=3, gridcolumn=6, gridrow=5)
# ttk.Button(mframe_main, text="Orthogonal merge", command=playbetween).grid(column=7, row=5)
# ttk.Button(mframe_main, text="Start/Stop IDX", command=playbetween).grid(column=6, row=6,  columnspan=2)

# nb.select(mframe_main)
nb.enable_traversal()
root.mainloop()