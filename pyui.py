mystory = """
it is apartment @(0,1,0,0,0,0,60,6,90) #1-#240
camera looks #1
lady is running #1
"""

import tkinter
import tkinter.filedialog
from tkinter import ttk
from tkinter import BOTH, END, LEFT

import json
import requests
import os
import re
import pprint

import p3dfunc
import pyback
import pytkui
from PIL import ImageTk, Image
from tkinter import messagebox 
from tkinter.messagebox import showinfo
import tkinter.scrolledtext as scrolledtext

import threading
import time

gappvars = {}
gappvars['headers'] = {'Content-type': 'application/json'}
gappvars['animurl'] = 'http://localhost:5000/getanim'
gappvars['imgdest'] = ''
gappvars['laststory'] = ''
gappvars['rushes'] = {}
gappvars['linepos'] = []
gappvars['logtext'] = []
linux_ffmpeg = 'ffmpeg -pattern_type glob -i "*.png" -c:v libx264 -y -filter:v "setpts=2*PTS"  -pix_fmt yuv420p out.mp4'
#gappvars['animurl'] = 'http://35.229.114.180:8001/getanim'

#Make the root widget
root = tkinter.Tk()
root.geometry("950x650")
root.iconphoto(False, tkinter.PhotoImage(file='icon.png'))
root.title("Meme'er")

nb = ttk.Notebook(root)
nb.pack()

lconf = pyback.getlocaluser()
gappvars['imgdest'] = pyback.getbasedir(lconf['portf_dir'])+'/rushes/'
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
lstoryui = pytkui.storyroomsetup (frame_story, csize = 500, gappvars = gappvars)
lstoryui['storybox'].insert(1.0, mystory)

def frame_acts_save ():
	cacts = pytkui.lactsuiread(lportui['acts'])
	pyback.saveuniv('actions', cacts, lconf['portf_dir']+'/universe.js')

def frame_objs_save ():
	cobjs = pytkui.lobjsuiread(lportui['objs'])
	pyback.saveuniv('objects', cobjs, lconf['portf_dir']+'/universe.js')

def frame_logix_save ():
	clogix = pytkui.llogixuiread(lportui['logix'])
	pyback.saveuniv('logicals', clogix, lconf['portf_dir']+'/universe.js')

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
	global gappvars
	gappvars['imgdest'] = pyback.getbasedir(lconf['portf_dir'])+'/rushes/'
	refresh_frame_buttons ()

btn_conf_save = ttk.Button(frame_conf, text="\tSave the configuration\t", command=frame_conf_save).grid(column=1, row=6, columnspan=3)
btn_conf_open = ttk.Button(frame_conf, text="Open Workdir", command=refresh_full_universe).grid(column=4, row=4)
gappvars['logtext'] = scrolledtext.ScrolledText(frame_conf, undo=True, width=115, height=29, bg="grey")
gappvars['logtext'].bind('<1>', lambda event: gappvars['logtext'].focus_set())
gappvars['logtext'].grid(column=1, row=8, sticky='n', columnspan=6)
pyback.logit (gappvars['logtext'], "Application logging------------------------------------\n")

def frame_story_story():
	def settext (text):
		lstoryui['storybox'].delete('1.0', END)
		lstoryui['storybox'].insert(1.0, text)
	selection = lstoryui['storycmb'].get()
	global gappvars
	if len (selection) < 2: print ("No execution")
	elif selection == 'Save Story as ...':
		fname = lstoryui['storyent'].get()
		storytxt = lstoryui['storybox'].get("1.0",END)
		pyback.savestoryas (fname, storytxt, lconf['portf_dir'])
	elif selection == 'Show Story Lists':
		filelist = pyback.showstories (lconf['portf_dir'])
		print (filelist)
		settext(filelist)
		gappvars['laststory'] = ''
	elif selection == 'Show Below Story':
		fname = re.sub("\n", "", lstoryui['storyent'].get())
		storytext = pyback.showastory (fname, lconf['portf_dir'])
		settext(storytext)
		gappvars['laststory'] = ''
	return 1

def frame_story_edit():
	return 1

def getstoryanim (change = 0, dest = '', inprod = 0):
	global gappvars
	storytext = lstoryui['storybox'].get("1.0",END)
	from pathlib import Path
	portf_dir = Path(lconf['portf_dir'])
	cacts = pytkui.lactsuiread(lportui['acts'])
	cobjs = pytkui.lobjsuiread(lportui['objs'])
	clogix = pytkui.llogixuiread(lportui['logix'])
	cfuncs = pytkui.lfuncsuiread(lportui['funcs'])
	cuniv = {'actions': cacts, 'objects': cobjs, 'logicals': clogix, 'functions': cfuncs}
	animation = pyback.response_textplay (gappvars['animurl'], gappvars['headers'], cuniv, storytext)
	cline = pyback.getchanged (gappvars['laststory'], storytext, change)
	serialized = p3dfunc.serialize (universe = cuniv, animation = animation, deserial = cline, portfolio = portf_dir.stem)
	serialized['inprod'] = str(inprod)
	if inprod == 1:	serialized['imgdest'] = gappvars['imgdest'] + 'pngs' + lstoryui['mprefix'].get()
	else: serialized['imgdest'] = gappvars['imgdest'] + dest + 'pngs'
	with open('serial.js', "w") as lujs: json.dump(serialized, lujs)
	gappvars['laststory'] = storytext
	return serialized

def frame_play_prod ():
	storyanim = getstoryanim (change = 0, dest = '', inprod = 1)
	os.system('ppython p3dpreview.py')
	global gappvars
	for keys in ['frindex', 'frlast', 'frixdel']: gappvars['rushes'][keys] = storyanim[keys]
	print ("Panda3d Execution completed")

def frame_play_full():
	storyanim = getstoryanim (change = 0, dest = '')
	os.system('ppython p3dpreview.py')
	global gappvars
	for keys in ['frindex', 'frlast', 'frixdel']: gappvars['rushes'][keys] = storyanim[keys]
	print ("Panda3d Execution completed")

def frame_play_edit():
	storyanim = getstoryanim (change = 1, dest = 'temp/')
	os.system('ppython p3dpreview.py')
	print ("Panda3d Execution completed")
	global gappvars
	for keys in ['frindex', 'frlast', 'frixdel']: gappvars['rushes'][keys] = storyanim[keys]
	pyback.overwrites (gappvars['imgdest'], storyanim['frindex'], storyanim['frlast'], storyanim['frixdel'])

def frame_play_pngs():
	fromfr = int(lstoryui['froment'].get())
	tillfr = int(lstoryui['tillent'].get())
	ffpsfr = int(lstoryui['ffpsent'].get())
	global gappvars
	print(gappvars['rushes'])
	if 'frindex' not in gappvars['rushes'] or 'frlast' not in gappvars['rushes'] or 'frixdel' not in gappvars['rushes']: return 1
	if fromfr < 1 or fromfr > gappvars['rushes']['frlast']: return 1
	if tillfr < 1 or tillfr > gappvars['rushes']['frlast']:
		lstoryui['tillent'].insert(0, str(gappvars['rushes']['frlast']))
		tillfr = gappvars['rushes']['frlast']
	lstoryui['canvas'].delete("all")
	for px in range(fromfr, tillfr):
		imgpng = gappvars['imgdest']+'pngs_'+"%04d"%(px)+".png"
		print(imgpng)
		image = Image.open(imgpng)
		image = image.resize((640, 480), Image.ANTIALIAS)
		root.myimg = myimg = ImageTk.PhotoImage(image)
		lstoryui['canvas'].create_image((0,0), image=myimg, anchor='nw')
		lstoryui['canvas'].update()
		time.sleep(1/ffpsfr)

def frame_stop_pngs():
	# showinfo("Window", "Hello World!")
	# xx=messagebox.askquestion("askquestion", "Are you sure?")
	# print (xx)
	frameat = int(lstoryui['frmatent'].get())
	global gappvars
	if 'frindex' not in gappvars['rushes'] or 'frlast' not in gappvars['rushes'] or 'frixdel' not in gappvars['rushes']: return 1
	if frameat < 1 or frameat > gappvars['rushes']['frlast']: return 1
	lstoryui['canvas'].delete("all")
	imgpng = gappvars['imgdest']+'pngs_'+"%04d"%(int(frameat))+".png"
	image = Image.open(imgpng)
	image = image.resize((500, 500), Image.ANTIALIAS)
	root.myimg = myimg = ImageTk.PhotoImage(image)
	lstoryui['canvas'].create_image((0,0), image=myimg, anchor='nw')
	lstoryui['canvas'].update()

def frame_point_exec():
	def settext (text):
		lstoryui['coordbox'].delete('1.0', END)
		lstoryui['coordbox'].insert(1.0, text)
	selection = lstoryui['coordcmb'].get()
	if selection == 'Save coords as':
		fname = lstoryui['coordent'].get()
		coordstxt = lstoryui['coordbox'].get("1.0",END)
		pyback.savecoordas (fname, coordstxt, lconf['portf_dir'])
		gappvars['linepos'] = []
		lstoryui['coordbox'].delete('1.0', END)
	elif selection == 'Load/Trace Below coords':
		fname = lstoryui['coordent'].get()
		coords = pyback.readcoordof (fname, lconf['portf_dir'])
		for ix in range(0, len(coords)-1):
			lstoryui['canvas'].create_line((coords[ix][0], coords[ix][1], coords[ix+1][0], coords[ix+1][1]))
			settext(pprint.pformat(coords, indent=2))
	elif selection == 'Show coords Lists':
		filelist = pyback.showscoords (lconf['portf_dir'])
		settext(filelist)
	elif selection == 'Merge coords with':
		xcoords = lstoryui['coordbox'].get("1.0",END)
		fname = lstoryui['coordent'].get()
		pyback.save3dcoord (fname, lconf['portf_dir'])
	print(gappvars['linepos'])

btn_story_story = ttk.Button(frame_story, text="Exec", command=frame_story_story).grid(column=0, row=35)
btn_story_edit = ttk.Button(frame_story, text="Exec", command=frame_point_exec).grid(column=46, row=36)
btn_play_full = ttk.Button(frame_story, text="Play from start", command=frame_play_full).grid(column=32, row=33)
btn_play_edit = ttk.Button(frame_story, text="Play from edit", command=frame_play_edit).grid(column=35, row=33)
btn_frame_play = ttk.Button(frame_story, text="Play frames", command=frame_play_pngs).grid(column=32, row=34)
btn_frame_stop = ttk.Button(frame_story, text="Stop/ at frame", command=frame_stop_pngs).grid(column=32, row=35)
btn_frame_save = ttk.Button(frame_story, text="Save movie (Suffix)", command=frame_play_prod).grid(column=35, row=35)

nb.enable_traversal()
root.mainloop()