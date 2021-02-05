import json
import tkinter
import tkinter.filedialog
from tkinter import ttk
from tksheet import Sheet
import pyback
import tkinter.scrolledtext as scrolledtext

def addstdframe (root, framedesc, row=0, col=0):
	nframe = tkinter.Frame(root)
	root.add(nframe, text=framedesc)
	#nframe.pack()
	return nframe

def addcnvframe (root, framedesc):
	def myfunction(event):
		mcanvas.configure(scrollregion=mcanvas.bbox("all"), width=900, height=600)

	mframe = addstdframe(root, framedesc)
	mcanvas=tkinter.Canvas(mframe)
	nframe = tkinter.Frame(mcanvas)
	myscrollbar=tkinter.Scrollbar(mframe, orient="vertical", command=mcanvas.yview)
	mcanvas.configure(yscrollcommand=myscrollbar.set)
	myscrollbar.pack(side="right", fill="y")
	mcanvas.pack (side="left")
	mcanvas.create_window ((0,0), window=nframe, anchor='nw')
	nframe.bind("<Configure>",myfunction)
	return nframe

def newentry (framep='', width=0, col=0, row=0, colspan=1, text='', lbltext = '', sticky='nw'):
	if lbltext != '':
		ttk.Label(framep, text=lbltext).grid(column=col-1, row=row)
	entry_text = tkinter.StringVar()
	entry_text_entry = ttk.Entry(framep, width=width, textvariable=entry_text)
	entry_text_entry.grid(column=col, row=row, sticky=sticky, columnspan=colspan)
	entry_text.set(text)
	return entry_text

def lconfuisetup (lconf, univ, root, lportui):
	ttk.Label(root, text="\t\t\t").grid(column=2, row=1)
	lportui['user'] = newentry (framep=root, width=90, col=3, row=2, text=lconf['user_idnt'], lbltext = 'User Identity')
	lportui['pkey'] = newentry (framep=root, width=90, col=3, row=3, text=lconf['secrettxt'], lbltext = 'Secret Passkey')
	lportui['wdir'] = newentry (framep=root, width=90, col=3, row=4, text=lconf['portf_dir'], lbltext = 'Working Directory')
	lportui['desc'] = newentry (framep=root, width=90, col=3, row=5, text=univ['namedetail'], lbltext = 'Name Description')

def _get_syns_jjrb (attrs = [], holder = {}, rownum=1, framep = {}, source = {}):
	if 'syns' in attrs or 'jjrb' in attrs:
		if 'syns' in source: holder['syns'] = newentry (framep=framep, width=40, col=1, row=rownum, colspan=2, text=', '.join(source['syns']), lbltext='Synonyms')
		if 'jjrb' in source: holder['jjrb'] = newentry (framep=framep, width=40, col=4, row=rownum, colspan=2, text=', '.join(source['jjrb']), lbltext='Modifier')
		rownum = rownum + 1
	if 'xyz' in attrs and 'hpr' in attrs and 'lbh' in attrs:
		holder['xyz'] = newentry (framep=framep, width=10, col=1, row=rownum, text=', '.join(map(str, source['xyz'])), lbltext='Coordinates')
		holder['hpr'] = newentry (framep=framep, width=10, col=3, row=rownum, text=', '.join(map(str, source['hpr'])), lbltext='Orientation')
		holder['lbh'] = newentry (framep=framep, width=10, col=5, row=rownum, text=', '.join(map(str, source['lbh'])), lbltext='Base Sizing')
		rownum = rownum + 1
	if 'speed' in attrs and 'fstart' in attrs and 'flast' in attrs:
		holder['speed'] = newentry (framep=framep, width=10, col=1, row=rownum, text=source['speed'], lbltext='Action FPS')
		holder['fstart'] = newentry (framep=framep, width=10, col=3, row=rownum, text=source['fstart'], lbltext='First Frame')
		holder['flast'] = newentry (framep=framep, width=10, col=5, row=rownum, text=source['flast'], lbltext='Last Frame')
		rownum = rownum + 1
	return rownum

def lactsuisetup (actions, root, lactsui):
	rownum = 0
	for actid, action in enumerate(actions):
		ttk.Label(root, text='-'*100).grid(column=0, row=rownum, columnspan=2, sticky='nw')
		lactui = {'actid': actid}
		if 'func' not in action: continue
		lactui['func'] = action['func']
		ttk.Label(root, text="Function Name: "+action['func']).grid(column=0, row=rownum, sticky='nw')
		rownum = _get_syns_jjrb (attrs = ['syns', 'jjrb'], holder = lactui, rownum=rownum+2, framep = root, source = action)
		lactsui.append(lactui)

def lobjsuisetup (objects, root, lobjsui):
	rownum = 0
	for modid, model in enumerate(objects):
		ttk.Label(root, text='-'*100).grid(column=0, row=rownum, columnspan=2, sticky='nw')
		objname = ', '.join(map(lambda x: x['file'], model['model']))
		lobjui = {'file': objname, 'modid': modid}
		ttk.Label(root, text='Model list: '+objname).grid(column=0, row=rownum, columnspan=2, sticky='nw')
		lobjui['move'] = newentry (framep=root, width=40, col=1, row=rownum+1, colspan=2, text=', '.join(model['move']), lbltext='Movement')
		rownum = rownum+2
		rownum = _get_syns_jjrb (attrs = ['syns', 'jjrb', 'xyz', 'hpr', 'lbh'], holder = lobjui, rownum=rownum, framep = root, source = model)
		lobjui['mfile'] = []
		for mfid, mfile in enumerate(model['model']):
			lobjfui = {'mfid': mfid}
			lobjfui['file'] = newentry (framep=root, width=40, col=1, row=rownum, colspan=2, text=mfile['file'], lbltext='Model File')
			lobjfui['jjrb'] = newentry (framep=root, width=40, col=4, row=rownum, colspan=2, text=', '.join(mfile['jjrb']), lbltext='Modifier')
			lobjui['mfile'].append(lobjfui)
			rownum = rownum+2
		lobjui['action'] = []
		for afildet in model['acts']:
			afile, actdet = list(afildet.items())[0]
			lobjfui = {'afid': afile}
			ttk.Label(root, text=objname+', Action file: '+afile).grid(column=0, row=rownum, columnspan=4)
			rownum = rownum+1
			rownum = _get_syns_jjrb (attrs = ['syns', 'jjrb', 'xyz', 'hpr', 'lbh', 'speed', 'ffrst', 'flast'], holder = lobjfui, rownum=rownum, framep = root, source = actdet)
			lobjui['action'].append(lobjfui)
			rownum = rownum + 4
		lobjsui.append(lobjui)

def llogixuisetup (logix, root, llogxui):
	rownum = 0
	for logid, logic in enumerate(logix+[{'basic': '', 'addon': []}]):
		ttk.Label(root, text='-'*100).grid(column=0, row=rownum, columnspan=2, sticky='nw')
		llogcui = {'logid': logid}
		llogcui['basic'] = newentry (framep=root, width=60, col=1, row=rownum+1, colspan=8, text=logic['basic'], lbltext='Current condition')
		ttk.Label(root, text='Extra steps').grid(column=0, row=rownum+2, sticky='nw')
		indexbox = scrolledtext.ScrolledText(root, undo=True, width=60, height=5)
		indexbox.grid(column=1, row=rownum+2, columnspan=5)
		indexbox.insert(1.0, "\n".join(logic['addon']))
		rownum=rownum+3
		llogxui.append(llogcui)

def lfuncsuisetup (funcs, root, lfuncsui):
	rownum = 0
	for fname, funcdet in funcs.items():
		ttk.Label(root, text='-'*100).grid(column=0, row=rownum, columnspan=2, sticky='nw')
		lfuncui = {'fname': fname}
		ttk.Label(root, text='Function Name: '+fname).grid(column=0, row=rownum+1, columnspan=2, sticky='nw')
		lfuncui['tags'] = []
		rownum=rownum+2
		for ftid, ftext in enumerate(funcdet):
			print (rownum)
			lfunctui = newentry (framep=root, width=90, col=1, row=rownum, colspan=6, text=', '.join(ftext['texts']), lbltext=ftext['tag'])
			lfuncui['tags'].append(lfunctui)
			rownum=rownum+1
		lfuncsui.append(lfuncui)
		rownum=rownum+1