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

headers = {'Content-type': 'application/json'}
animurl = 'http://localhost:5000/getanim'

#Make the root widget
root = tkinter.Tk()
root.geometry("950x650")
nb = ttk.Notebook(root)
nb.pack()

def create_entry (framep='', width=0, gridcolumn=0, gridrow=0, columnspan=1, settext='', holder = 0, holderkey = '', withlabel = '', sticky='nw'):
	if withlabel != '':
		ttk.Label(framep, text=withlabel).grid(column=gridcolumn-1, row=gridrow)
	entry_text = tkinter.StringVar()
	entry_text_entry = ttk.Entry(framep, width=width, textvariable=entry_text)
	entry_text_entry.grid(column=gridcolumn, row=gridrow, sticky=sticky, columnspan=columnspan)
	entry_text.set(settext)
	if isinstance(holder, dict):
		holder[holderkey] = entry_text
	return entry_text

# Make user local configuration tab
localconf = {'user_idnt': 'Actually only user', 'secrettxt': 'xxxxxxxxxx', 'portf_dir': r'C:\ProgramData\VirtualBox\common\memeer\userapp\portfolio'}
frame_conf = tkinter.Frame(nb)
nb.add(frame_conf, text="User Local Configuration")
ttk.Label(frame_conf, text="\t\t\t").grid(column=2, row=1)
ttk.Label(frame_conf, text="User Identity").grid(column=1, row=1)
conf_user_idnt = create_entry (framep=frame_conf, width=32, gridcolumn=3, gridrow=1, settext=localconf['user_idnt'])
ttk.Label(frame_conf, text="User Secret Text").grid(column=1, row=2)
conf_secrettxt = create_entry (framep=frame_conf, width=32, gridcolumn=3, gridrow=2, settext=localconf['secrettxt'])
ttk.Label(frame_conf, text="Working Directory").grid(column=1, row=3)
conf_portf_dir = create_entry (framep=frame_conf, width=90, gridcolumn=3, gridrow=3, settext=localconf['portf_dir'])

# Make portfolio detal and review tab
## Start with framing setup
def myfunction(event):
	confcv.configure(scrollregion=confcv.bbox("all"),width=900,height=600)

mframe_port = tkinter.Frame(nb)
mframe_port.pack()
nb.add(mframe_port, text="Portfolio Detail and Review")
confcv=tkinter.Canvas(mframe_port)
frame_port = tkinter.Frame(confcv)
myscrollbar=tkinter.Scrollbar(mframe_port,orient="vertical",command=confcv.yview)
confcv.configure(yscrollcommand=myscrollbar.set)
myscrollbar.pack(side="right",fill="y")
confcv.pack(side="left")
confcv.create_window((0,0),window=frame_port,anchor='nw')
frame_port.bind("<Configure>",myfunction)

## Get the universe data to show
univ = pyback.getUniverseData (conf_user_idnt.get(), conf_portf_dir.get())
rentries = {}
# Add for description
ttk.Label(frame_port, text="Description").grid(column=0, row=0)
port_entry = create_entry (framep=frame_port, width=90, gridcolumn=1, gridrow=0, columnspan=6, settext=univ['description'], holder = rentries, holderkey = 'description')
#print (rentries['description'].get())
rentries['action'] = []
ttk.Label(frame_port, text="Actions").grid(column=1, row=1)
rowcount = 2
for action in univ['action']:
	rentriesact = {}
	if 'func' in action:
		rentriesact['func'] = action['func']
		ttk.Label(frame_port, text="Function Name: "+action['func']).grid(column=1, row=rowcount, sticky='nw')
	elif 'actf' in action:
		rentriesact['actf'] = action['actf']
		ttk.Label(frame_port, text="Action File: "+action['actf']).grid(column=1, row=rowcount, sticky='nw')
	port_entry = create_entry (framep=frame_port, width=40, gridcolumn=1, gridrow=rowcount+1, columnspan=2, 
								settext=', '.join(action['syns']), holder = rentriesact, holderkey = 'syns', withlabel='Synonyms')
	port_entry = create_entry (framep=frame_port, width=40, gridcolumn=4, gridrow=rowcount+1, columnspan=2, 
								settext=', '.join(action['jjrb']), holder = rentriesact, holderkey = 'jjrb', withlabel='Modifiers')
	if 'actf' not in action:
		rentries['action'].append(rentriesact)
		rowcount = rowcount + 2
		continue
	port_entry = create_entry (framep=frame_port, width=10, gridcolumn=1, gridrow=rowcount+2, columnspan=1, 
								settext=', '.join(map(str, action['xyz'])), holder = rentriesact, holderkey = 'xyz', withlabel='Locate')
	port_entry = create_entry (framep=frame_port, width=10, gridcolumn=3, gridrow=rowcount+2, columnspan=1, 
								settext=', '.join(map(str, action['hpr'])), holder = rentriesact, holderkey = 'hpr', withlabel='Orient')
	port_entry = create_entry (framep=frame_port, width=10, gridcolumn=5, gridrow=rowcount+2, columnspan=1, 
								settext=', '.join(map(str, action['lbh'])), holder = rentriesact, holderkey = 'lbh', withlabel='Scaled')
	port_entry = create_entry (framep=frame_port, width=10, gridcolumn=1, gridrow=rowcount+3, columnspan=1, 
								settext=action['speed'], holder = rentriesact, holderkey = 'speed', withlabel='Speed')
	port_entry = create_entry (framep=frame_port, width=10, gridcolumn=3, gridrow=rowcount+3, columnspan=1, 
								settext=action['fstart'], holder = rentriesact, holderkey = 'fstart', withlabel='First Frame')
	port_entry = create_entry (framep=frame_port, width=10, gridcolumn=5, gridrow=rowcount+3, columnspan=1, 
								settext=action['fdone'], holder = rentriesact, holderkey = 'fdone', withlabel='Last Frame')
	rentries['action'].append(rentriesact)
	rowcount = rowcount + 5

rentries['object'] = []
ttk.Label(frame_port, text="Objects").grid(column=1, row=rowcount)
rowcount = rowcount + 1
for object in univ['object']:
	rentriesobj = {}
	objname = 'ObjectName: '+', '.join(map(lambda x: x['file'], object['model']))
	ttk.Label(frame_port, text=objname).grid(column=1, row=rowcount, columnspan=2, sticky='nw')
	port_entry = create_entry (framep=frame_port, width=40, gridcolumn=1, gridrow=rowcount+1, columnspan=2, 
								settext=', '.join(object['syns']), holder = rentriesobj, holderkey = 'syns', withlabel='Synonyms')
	port_entry = create_entry (framep=frame_port, width=40, gridcolumn=4, gridrow=rowcount+1, columnspan=2, 
								settext=', '.join(object['jjrb']), holder = rentriesobj, holderkey = 'jjrb', withlabel='Modifiers')
	port_entry = create_entry (framep=frame_port, width=10, gridcolumn=1, gridrow=rowcount+2, columnspan=1, 
								settext=', '.join(map(str, object['xyz'])), holder = rentriesobj, holderkey = 'xyz', withlabel='Locate')
	port_entry = create_entry (framep=frame_port, width=10, gridcolumn=3, gridrow=rowcount+2, columnspan=1, 
								settext=', '.join(map(str, object['hpr'])), holder = rentriesobj, holderkey = 'hpr', withlabel='Orient')
	port_entry = create_entry (framep=frame_port, width=10, gridcolumn=5, gridrow=rowcount+2, columnspan=1, 
								settext=', '.join(map(str, object['lbh'])), holder = rentriesobj, holderkey = 'lbh', withlabel='Scaled')
	port_entry = create_entry (framep=frame_port, width=40, gridcolumn=1, gridrow=rowcount+3, columnspan=2, 
								settext=', '.join(object['move']), holder = rentriesobj, holderkey = 'move', withlabel='Movement')
	ttk.Label(frame_port, text='Actfiles: '+', '.join(list(map(lambda x: list(x)[0], object['acts'])))).grid(column=4, row=rowcount+3, columnspan=2)
	rowcount = rowcount + 4
	rentriesobj['model'] = []
	for model in object['model']:
		rentriesobjmod = {'file': model['file']}
		ttk.Label(frame_port, text='Model list: '+model['file']).grid(column=1, row=rowcount, columnspan=2, sticky='nw')
		port_entry = create_entry (framep=frame_port, width=40, gridcolumn=3, gridrow=rowcount, columnspan=3, 
									settext=', '.join(model['jjrb']), holder = rentriesobjmod, holderkey = 'jjrb', withlabel='Modifiers')
		rentriesobj['model'].append(rentriesobjmod)
		rowcount = rowcount + 1
	rentriesobj['acts'] = []
	for actdet in object['acts']:
		rentriesobjact = {}
		actf, action = list(actdet.keys())[0], list(actdet.values())[0]
		ttk.Label(frame_port, text=objname+', Action file: '+actf).grid(column=0, row=rowcount, columnspan=2)
		port_entry = create_entry (framep=frame_port, width=40, gridcolumn=1, gridrow=rowcount+1, columnspan=2, 
									settext=', '.join(action['syns']), holder = rentriesobjact, holderkey = 'syns', withlabel='Synonyms')
		port_entry = create_entry (framep=frame_port, width=40, gridcolumn=4, gridrow=rowcount+1, columnspan=2, 
									settext=', '.join(action['jjrb']), holder = rentriesobjact, holderkey = 'jjrb', withlabel='Modifiers')
		port_entry = create_entry (framep=frame_port, width=10, gridcolumn=1, gridrow=rowcount+2, columnspan=1, 
									settext=', '.join(map(str, action['xyz'])), holder = rentriesobjact, holderkey = 'xyz', withlabel='Locate')
		port_entry = create_entry (framep=frame_port, width=10, gridcolumn=3, gridrow=rowcount+2, columnspan=1, 
									settext=', '.join(map(str, action['hpr'])), holder = rentriesobjact, holderkey = 'hpr', withlabel='Orient')
		port_entry = create_entry (framep=frame_port, width=10, gridcolumn=5, gridrow=rowcount+2, columnspan=1, 
									settext=', '.join(map(str, action['lbh'])), holder = rentriesobjact, holderkey = 'lbh', withlabel='Scaled')
		port_entry = create_entry (framep=frame_port, width=10, gridcolumn=1, gridrow=rowcount+3, columnspan=1, 
									settext=action['speed'], holder = rentriesobjact, holderkey = 'speed', withlabel='Speed')
		port_entry = create_entry (framep=frame_port, width=10, gridcolumn=3, gridrow=rowcount+3, columnspan=1, 
									settext=action['fstart'], holder = rentriesobjact, holderkey = 'fstart', withlabel='First Frame')
		port_entry = create_entry (framep=frame_port, width=10, gridcolumn=5, gridrow=rowcount+3, columnspan=1, 
									settext=action['fdone'], holder = rentriesobjact, holderkey = 'fdone', withlabel='Last Frame')
		rentriesobj['acts'].append(rentriesobjact)
		rowcount = rowcount + 4
	rentries['object'].append(rentriesobj)
rentries['logic'] = []
ttk.Label(frame_port, text="Logical setup").grid(column=1, row=rowcount)
rowcount = rowcount + 1
for refer in univ['logic_setup']+[{'before': [], 'current': [], 'after': []}]:
	rentriesref = {}
	lbltext="Existing one" if len(refer['before'])+len(refer['before'])+len(refer['before']) > 0 else "New one"
	ttk.Label(frame_port, text=lbltext).grid(column=1, row=rowcount)
	port_entry = create_entry (framep=frame_port, width=80, gridcolumn=1, gridrow=rowcount+1, columnspan=5, 
								settext=', '.join(refer['before']), holder = rentriesref, holderkey = 'before', withlabel='Before condition')
	port_entry = create_entry (framep=frame_port, width=80, gridcolumn=1, gridrow=rowcount+2, columnspan=5, 
								settext=', '.join(refer['current']), holder = rentriesref, holderkey = 'current', withlabel='Current condition')
	port_entry = create_entry (framep=frame_port, width=80, gridcolumn=1, gridrow=rowcount+3, columnspan=5, 
								settext=', '.join(refer['after']), holder = rentriesref, holderkey = 'after', withlabel='After condition')
	rentries['logic'].append(rentriesref)
	rowcount = rowcount + 4
rentries['funclet'] = {}
ttk.Label(frame_port, text="Functions").grid(column=1, row=rowcount)
rowcount = rowcount + 1
# No need to allow new functions defined here - user setting up new function can update json itself
for fkey, fvalue in univ['functions'].items():
	rentriesfnc = {}
	ttk.Label(frame_port, text="Name: "+fkey).grid(column=0, row=rowcount, columnspan=2, sticky='nw')
	for ffkey, ffvalue in fvalue.items():
		port_entry = create_entry (framep=frame_port, width=80, gridcolumn=2, gridrow=rowcount, columnspan=5, 
									settext=', '.join(ffvalue), holder = rentriesfnc, holderkey=ffkey, withlabel=ffkey)
		rowcount = rowcount + 1
	rentries['funclet'][fkey] = rentriesfnc

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
		nlogic = {'before': logic['before'].get(), 'current': logic['current'].get(), 'after': logic['after'].get()}
		if len(nlogic['before'])+len(nlogic['before'])+len(nlogic['before']) > 0: nuniv['logic'].append(nlogic)
	nuniv['funclet'] = {}
	for fncname, fncdet in rentries['funclet'].items():
		nuniv['funclet'][fncname] = {}
		for fnctag, fnctext in fncdet.items():
			nuniv['funclet'][fncname][fnctag] = fnctext.get()
	print (nuniv)

ttk.Button(frame_port, text="Save", command=savethedata).grid(column=1, row=rowcount, sticky='nw', columnspan=5)

def savePosn(event):
	global lastx, lasty
	lastx, lasty = event.x, event.y
	print (lastx, lasty)

def addLine(event):
	canvas.create_line((lastx, lasty, event.x, event.y))
	savePosn(event)

def playall ():
	mystory={"mystory": storybox.get("1.0", "end")}
	mystory=json.dumps(mystory)
	response = requests.post(animurl, headers=headers, data=mystory)
	animation = json.loads(response.text)
	serealize = p3dfunc.serealize(animation)
	with open("C:\ProgramData\Memeer\data.py", "w") as outfile: json.dump(serealize, outfile) 
	#execfile('production.py')
	os.system('ppython production.py')
	return 1

def playatedit (*args):
	return 1

def playbetween (*args):
	return 1

def prvframe (*args):
	return 1

def playpending (*args):
	return 1

mframe_main = tkinter.Frame(nb)
nb.add(mframe_main, text="Welcome to Meme'er")
storybox = tkinter.Text(mframe_main, width=50, height=25)
storybox.grid(column=0, row=0, columnspan=3)
canvas = tkinter.Canvas(mframe_main, width=400, height=400, background='gray75')
canvas.grid(column=3, row=0, columnspan=3)
canvas.bind("<Button-1>", savePosn)
canvas.bind("<B1-Motion>", addLine)
myimg = tkinter.PhotoImage(file='models/2dpics/basemedia/indiamap.png')
canvas.create_image(10, 10, image=myimg, anchor='nw')
indexbox = tkinter.Text(mframe_main, width=11, height=25).grid(column=6, row=0, columnspan=2)
ttk.Label(mframe_main, text=".    .    .    .    .    .    .    .").grid(column=1, row=1, columnspan=7)
ttk.Label(mframe_main, text="C    O    N    T    R    O    L    S").grid(column=1, row=2, columnspan=7)
ttk.Label(mframe_main, text="    .    .    .    .    .    .    .    ").grid(column=1, row=3, columnspan=7)

ttk.Button(mframe_main, text="Start Full Play", command=playall).grid(column=1, row=4)
ttk.Button(mframe_main, text="Start Play from Edit", command=playatedit).grid(column=1, row=5)
mainplayfro = create_entry (framep=mframe_main, width=6, gridcolumn=0, gridrow=6, sticky='ne')
ttk.Button(mframe_main, text="Show Between Frames", command=playbetween).grid(column=1, row=6)
mainplaytil = create_entry (framep=mframe_main, width=6, gridcolumn=2, gridrow=6)

ttk.Button(mframe_main, text="Previous Frame", command=prvframe).grid(column=3, row=4, sticky='ne')
ttk.Button(mframe_main, text="Next Frame", command=prvframe).grid(column=4, row=4, sticky='ne')
ttk.Button(mframe_main, text="Play at Speed", command=playpending).grid(column=3, row=5, sticky='ne')
mainframspd = create_entry (framep=mframe_main, width=3, gridcolumn=4, gridrow=5, sticky='ne')
ttk.Button(mframe_main, text="Between Frames", command=playbetween).grid(column=3, row=6, sticky='ne')
mainframfro = create_entry (framep=mframe_main, width=3, gridcolumn=4, gridrow=6, sticky='ne')
mainframtil = create_entry (framep=mframe_main, width=3, gridcolumn=5, gridrow=6, sticky='nw')

mainindxnam = create_entry (framep=mframe_main, width=5, gridcolumn=6, gridrow=4)
ttk.Button(mframe_main, text="Save Indexes", command=playbetween).grid(column=7, row=4)
mainindxmrg = create_entry (framep=mframe_main, width=3, gridcolumn=6, gridrow=5)
ttk.Button(mframe_main, text="Orthogonal merge", command=playbetween).grid(column=7, row=5)
ttk.Button(mframe_main, text="Start/Stop IDX", command=playbetween).grid(column=6, row=6,  columnspan=2)

nb.select(mframe_main)
nb.enable_traversal()
root.mainloop()