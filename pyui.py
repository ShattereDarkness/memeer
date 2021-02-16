mystory = """
it is narrator @(0,0,0,0,0,0,1,1,1)

narrator says "hello youong frinds" #36

narrator says "welcome to this animmation on far flung cltures of India" @(0,0,0,0,0,0,1,1,1)-@(0,0,0,0,0,0,4,4,4)

narrator says "My name is Ahmad Balti and today, I will tell you about my Balti people" #72-#144

lady walks "and that is true" #72-#144

"""

import tkinter
import tkinter.filedialog
from tkinter import ttk
from tkinter import BOTH, END, LEFT

import json
import requests
import os
import re

import p3dfunc
import pyback
import pytkui
from PIL import ImageTk, Image

import threading
import time

headers = {'Content-type': 'application/json'}
animurl = 'http://localhost:5000/getanim'
stopauto = 0

laststory = ''

#Make the root widget
root = tkinter.Tk()
root.geometry("950x650")
root.iconphoto(False, tkinter.PhotoImage(file='icon.png'))
root.title("Meme'er")

nb = ttk.Notebook(root)
nb.pack()

lconf = pyback.getlocaluser()
lportui = {'conf': {}, 'acts': [], 'objs': [], 'logix': [], 'funcs': []}
lstoryui = {}

frame_conf = pytkui.addstdframe (nb, "User Local Configuration")
pytkui.lconfuisetup (lconf, {}, frame_conf, lportui['conf'])

frame_acts = pytkui.addcnvframe (nb, "Portfolio Actions")
frame_objs = pytkui.addcnvframe (nb, "Portfolio Objects")
frame_logix = pytkui.addcnvframe (nb, "Logical Functions")
frame_funcs = pytkui.addcnvframe (nb, "Panda3dUI Functions")
conf_frames = {'conf': frame_conf, 'acts': frame_acts, 'objs': frame_objs, 'logix': frame_logix, 'funcs': frame_funcs}
frame_story = pytkui.addstdframe (nb, "User Stories and play")
lstoryui = pytkui.storyroomsetup (frame_story)
lstoryui['storybox'].insert(1.0, mystory)

def frame_acts_save ():
	cacts = pytkui.lactsuiread(lportui['acts'])
	pyback.saveuniv('actions', cacts)

def frame_objs_save ():
	cobjs = pytkui.lobjsuiread(lportui['objs'])
	print (cobjs)
	pyback.saveuniv('objects', cobjs)

def frame_logix_save ():
	print(lportui['funcs'])
	clogix = pytkui.llogixuiread(lportui['logix'])
	pyback.saveuniv('logicals', clogix)

def refresh_frame_buttons ():
	frame_size = frame_acts.grid_size()
	btn_acts_save = ttk.Button(frame_acts, text="\tSave Action configuration\t", command=frame_acts_save).grid(column=4, row=frame_size[1])
	frame_size = frame_objs.grid_size()
	btn_objs_save = ttk.Button(frame_objs, text="\tSave Object configuration\t", command=frame_objs_save).grid(column=4, row=frame_size[1])
	frame_size = frame_logix.grid_size()
	btn_logix_save = ttk.Button(frame_logix, text="\tSave Logical configuration\t", command=frame_logix_save).grid(column=1, row=frame_size[1])

univ = pytkui.refresh_universe(lportui, conf_frames, lconf)
refresh_frame_buttons ()

def frame_conf_save():
	pyback.port_conf_save (lportui['conf'], lconf, univ)

def refresh_full_universe():
	pytkui.refresh_universe(lportui, conf_frames, lconf)
	refresh_frame_buttons ()

btn_conf_save = ttk.Button(frame_conf, text="\tSave the configuration\t", command=frame_conf_save).grid(column=1, row=6, columnspan=3)
btn_conf_open = ttk.Button(frame_conf, text="Open Workdir", command=refresh_full_universe).grid(column=4, row=4)

def frame_story_story():
	selection = lstoryui['storycmb'].get()
	if len (selection) < 2: print ("No execution")
	elif selection == 'Save Story as ...':
		fname = lstoryui['storyent'].get()
		storytxt = lstoryui['storybox'].get("1.0",END)
		pyback.savestoryas (fname, storytxt, lconf['portf_dir'])
	elif selection == 'Show Story Lists':
		filelist = pyback.showstories (lconf['portf_dir'])
		print (filelist)
		lstoryui['storybox'].delete('1.0', END)
		lstoryui['storybox'].insert(1.0, filelist)
		laststory = ''
	elif selection == 'Show Below Story':
		fname = re.sub("\n", "", lstoryui['storyent'].get())
		storytext = pyback.showastory (fname, lconf['portf_dir'])
		lstoryui['storybox'].delete('1.0', END)
		lstoryui['storybox'].insert(1.0, storytext)
		laststory = ''
	return 1

def frame_story_edit():
	return 1
def frame_play_full():
	storytext = lstoryui['storybox'].get("1.0",END)
	cacts = pytkui.lactsuiread(lportui['acts'])
	cobjs = pytkui.lobjsuiread(lportui['objs'])
	clogix = pytkui.llogixuiread(lportui['logix'])
	cfuncs = pytkui.lfuncsuiread(lportui['funcs'])
	cuniv = {'actions': cacts, 'objects': cobjs, 'logicals': clogix, 'functions': cfuncs}
	animation = pyback.response_textplay (animurl, headers, cuniv, storytext)
	serialized = p3dfunc.serialize (universe = cuniv, animation = animation)

def frame_play_edit():
	return 1

btn_story_story = ttk.Button(frame_story, text="Exec", command=frame_story_story).grid(column=0, row=35)
btn_story_edit = ttk.Button(frame_story, text="Exec", command=frame_story_edit).grid(column=46, row=36)
btn_play_full = ttk.Button(frame_story, text="Play from start", command=frame_play_full).grid(column=32, row=33)
btn_play_edit = ttk.Button(frame_story, text="Play from edit", command=frame_play_edit).grid(column=35, row=33)
btn_frame_play = ttk.Button(frame_story, text="Play frames", command=frame_play_edit).grid(column=32, row=34)
btn_frame_stop = ttk.Button(frame_story, text="Stop/ at frame", command=frame_play_edit).grid(column=32, row=35)
btn_frame_save = ttk.Button(frame_story, text="Save movie", command=frame_play_edit).grid(column=35, row=35)

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

nb.enable_traversal()
root.mainloop()