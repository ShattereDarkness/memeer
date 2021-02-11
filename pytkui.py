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
	entry_text_entry = ttk.Entry(framep, width=width)
	entry_text_entry.grid(column=col, row=row, sticky=sticky, columnspan=colspan)
	entry_text_entry.insert(0, text)
	return entry_text_entry

def refresh_universe(lportui, conf_frames, lconf):
	if 'desc' in lportui['conf']:
		print (lportui['conf'])
		lportui['conf']['desc'].destroy()
	for code, frames in conf_frames.items():
		if code == 'conf': continue
		for tkitemls in frames.winfo_children():
			## We delete only items within canvas frame and not canvas frame itself
			tkitemls.destroy()
	univ = pyback.getUniverseData (lconf['user_idnt'], lconf['portf_dir'])
	lconfuisetup (lconf, univ, conf_frames['conf'], lportui['conf'])
	lactsuisetup (univ['actions'], conf_frames['acts'], lportui['acts'])
	lobjsuisetup (univ['objects'], conf_frames['objs'], lportui['objs'])
	llogixuisetup (univ['logicals'], conf_frames['logix'], lportui['logix'])
	lfuncsuisetup (univ['functions'], conf_frames['funcs'], lportui['funcs'])
	return univ

def lconfuisetup (lconf, univ, root, lportui, retry=1):
	ttk.Label(root, text="\t\t\t").grid(column=2, row=1)
	lportui['user'] = newentry (framep=root, width=90, col=3, row=2, text=lconf['user_idnt'], lbltext = 'User Identity')
	lportui['pkey'] = newentry (framep=root, width=90, col=3, row=3, text=lconf['secrettxt'], lbltext = 'Secret Passkey')
	lportui['wdir'] = newentry (framep=root, width=90, col=3, row=4, text=lconf['portf_dir'], lbltext = 'Working Directory')
	if 'namedetail' in univ and retry == 1: lportui['desc'] = newentry (framep=root, width=90, col=3, row=5, text=univ['namedetail'])
	else: ttk.Label(root, text='Name Description').grid(column=2, row=5)

def storyroomsetup (lstory, csize=500):
	def savePosn(event):
		global lastx, lasty
		lastx, lasty = event.x, event.y
		print (lastx, lasty)
	def addLine(event):
		canvas.create_line((lastx, lasty, event.x, event.y))
		savePosn(event)
	def loadCombobox (root = {}, lovalues = (), col=0, row=0, colspan = 1, ):
		countryvar = tkinter.StringVar()
		country = ttk.Combobox(root, textvariable=countryvar)
		country.grid(column=col, row=row, sticky='n', columnspan=colspan)
		country['values'] = lovalues
		country.state(["readonly"])
		return country
	storybox = scrolledtext.ScrolledText(lstory, undo=True, width=30, height=35)
	storybox.grid(column=0, row=0, sticky='n', rowspan=35, columnspan=30)
	storycmb = loadCombobox (root = lstory, lovalues = ('Save Story as ...', 'Show Below Story', 'Show Story Lists'), col=4, row=35, colspan = 25)
	storyent = newentry (framep=lstory, width=30, col=0, row=36, text='', colspan=30)
	canvas = tkinter.Canvas(lstory, width=csize, height=csize, background='gray75')
	canvas.grid(column=31, row=0, sticky='n', columnspan=10)
	canvas.bind("<Button-1>", savePosn)
	canvas.bind("<B1-Motion>", addLine)
	frmatent = newentry (framep=lstory, width=4, col=33, row=35, text='-1')
	froment = newentry (framep=lstory, width=4, col=34, row=34, text='0', lbltext='From')
	tillent = newentry (framep=lstory, width=4, col=36, row=34, text='-1', lbltext='Till')
	ffpsent = newentry (framep=lstory, width=4, col=38, row=34, text='1', lbltext='FPS')
	coordbox = scrolledtext.ScrolledText(lstory, undo=True, width=17, height=30)
	coordbox.grid(column=42, row=0, sticky='n', columnspan=16)
	coordcmb = loadCombobox (root=lstory, lovalues=('Save coords as','Load/Trace Below coords','Show coords Lists','Merge coords with'), col=44, row=34, colspan = 15)
	coordent = newentry (framep=lstory, width=24, col=44, row=35, text='', colspan=18)
	lstoryui = {'storybox': storybox, 'storycmb': storycmb, 'storyent': storyent, 'canvas': canvas,
				'frmatent': frmatent, 'froment': froment, 'tillent': tillent, 'ffpsent': ffpsent, 'coordbox': coordbox, 'coordcmb': coordcmb, 'coordent': coordent}
	return lstoryui

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

def splittext (text = '', asnum = 0, sep = ','):
	retval = []
	for nstr in text.split(sep):
		if nstr == '': continue
		if asnum == 1: retval.append(float(nstr))
		else: retval.append(nstr.strip())
	return retval

def lactsuiread (lactsui):
	retval = []
	for act in lactsui:
		lact = {}
		if 'func' in act: lact['func'] = act['func']
		else: lact['acts'] = act['acts']
		lact['syns'] = splittext (text = act['syns'].get())
		lact['jjrb'] = splittext (text = act['jjrb'].get())
		retval.append(lact)
	return retval

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

def lobjsuiread (lobjsui):
	retval = []
	for obj in lobjsui:
		lobj = {'model': [], 'acts': []}
		lobj['syns'] = splittext (text = obj['syns'].get())
		lobj['jjrb'] = splittext (text = obj['jjrb'].get())
		lobj['move'] = splittext (text = obj['move'].get())
		lobj['xyz'] = splittext (text = obj['xyz'].get(), asnum = 1)
		lobj['hpr'] = splittext (text = obj['hpr'].get(), asnum = 1)
		lobj['lbh'] = splittext (text = obj['lbh'].get(), asnum = 1)
		for mfile in obj['mfile']:
			mfdetjjrb = splittext (text = mfile['jjrb'].get())
			mfdet = {'file': mfile['file'].get(), 'jjrb': mfdetjjrb}
			lobj['jjrb'].extend(mfdetjjrb)
			lobj['model'].append(mfdet)
		for macts in obj['action']:
			mfdet = {'speed': int(macts['speed'].get()), 'fstart': int(macts['fstart'].get()), 'flast': int(macts['flast'].get())}
			mfdet['jjrb'] = splittext (text = macts['jjrb'].get())
			lobj['acts'].append({macts['afid']: mfdet})
		retval.append(lobj)
	return retval

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
			ttk.Label(root, text=objname+', Action file: '+afile).grid(column=0, row=rownum)
			rownum = _get_syns_jjrb (attrs = ['jjrb', 'speed', 'fstart', 'flast'], holder = lobjfui, rownum=rownum, framep = root, source = actdet)
			lobjui['action'].append(lobjfui)
			rownum = rownum + 5
		lobjsui.append(lobjui)

def llogixuiread (llogixui):
	retval = []
	for llist in llogixui:
		logic = {}
		logic['basic'] = llist['basic'].get()
		if logic['basic'] == '': continue
		logic['addon'] = splittext (text = llist['addon'].get('1.0', tkinter.END), sep = "\n")
		retval.append(logic)
	return retval

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
		llogcui['addon'] = indexbox
		rownum=rownum+3
		llogxui.append(llogcui)

def lfuncsuiread (lfuncsui):
	retval = {}
	for llist in lfuncsui:
		retval[llist['fname']] = []
		for tags in llist['tags']:
			retval[llist['fname']].append({'tag': tags['tagn'], 'texts': splittext (text = tags['ttext'].get())})
	print(retval)
	return retval

def lfuncsuisetup (funcs, root, lfuncsui):
	rownum = 0
	for fname, funcdet in funcs.items():
		ttk.Label(root, text='-'*100).grid(column=0, row=rownum, columnspan=2, sticky='nw')
		lfuncui = {'fname': fname}
		ttk.Label(root, text='Function Name: '+fname).grid(column=0, row=rownum+1, columnspan=2, sticky='nw')
		lfuncui['tags'] = []
		rownum=rownum+2
		for ftid, ftext in enumerate(funcdet):
			lfunctui = newentry (framep=root, width=90, col=1, row=rownum, colspan=6, text=', '.join(ftext['texts']), lbltext=ftext['tag'])
			lfuncui['tags'].append({'tagn':ftext['tag'], 'ttext': lfunctui})
			rownum=rownum+1
		lfuncsui.append(lfuncui)
		rownum=rownum+1