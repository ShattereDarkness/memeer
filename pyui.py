mystory = """earth is named Mypicture @(0,2,7,0,0,0,75,50,50) #1-#120
line is drawn @(-21,0,0,0,0,0,1,1,1)-@(21,0,0,0,0,0,1,1,1) #61-#120
Ruchika is a lady #61
Ruchika ran @(-21,0,0,0,0,0,1,1,1)-@(21,0,0,0,0,0,1,1,1) #61-#120
front SUV moved away @f(Y_driveaway) #1-#60
line is drawn @(0,0,22,0,0,0,1,1,1)-@(0,0,-22,0,0,0,1,1,1) #121-#180
another front SUV @(-21,0,0,0,0,0,1,1,1)


line is drawn @f(0000horse1)
line is drawn @f(0001horse1)
line is drawn @f(0002horse1)
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
import imagings
import pytkui
from PIL import ImageTk, Image
from tkinter import messagebox 
from tkinter.messagebox import showinfo
import tkinter.scrolledtext as scrolledtext

import threading
import time

gappvars = {}
#gappvars['animurl'] = 'http://localhost:5000/getanim'
gappvars['imgdest'] = ''
gappvars['laststory'] = ''
gappvars['rushes'] = {}
gappvars['linepos'] = []
gappvars['logtext'] = []
projvars = {}
projvars['animurl'] = 'http://localhost:5000/getanim'
session = {'coords': [], 'stopact': 0}
#linux_ffmpeg = 'ffmpeg -pattern_type glob -i "*.png" -c:v libx264 -y -filter:v "setpts=2*PTS"  -pix_fmt yuv420p out.mp4'
#gappvars['animurl'] = 'http://35.229.114.180:8001/getanim'

#Make the root widget
root = tkinter.Tk()
root.geometry("950x650")
root.resizable(0,0)
root.iconphoto(False, tkinter.PhotoImage(file='imgs/icon.png'))
root.title("Meme'er")

boarditems = [
    {"Current rush": [{"Play story": ["FPS", "Screen Size (Wide x Height)", "Play from frame#"]}, {"Replay frames": ["From frame#", "Upto frame#", "FPS"]}, {"Export video": ["Name of video", "FPS", "Frames range"]}, {"Delete rush frames": []}]},
    {"Story": [{"Save story": ["Name"]}, {"Open story": ["Name"]}, {"List stories": ["*NAME LIKE*"]}]},
    {"Co-ord": [{"Save coords": ["Camera Location (3D)", "Camera Looks at/\nWhiteboard Center", "Name"]}, 
        {"Quick coords": ["Camera Location (3D)", "Camera Looks at/\nWhiteboard Center"]}, {"Open coords": ["Name"]}, 
        {"List coords": ["*NAME LIKE*"]}, {"Merge coords": ["X list file", "Y list file", "Z list file"]}, 
        {"Transform coords": ["Name", "Canvas Size (Wide x Height)", "Screen Size (Wide x Height)"]}, 
        {"Translate coords": ["Name", "Movement to right", "Movement to bottom"]}]},
    {"Audio/ Video": [{"List Audios": ["*NAME LIKE*"]}, {"List Videos": ["*NAME LIKE*"]}, {"Merge Audio+Video": ["Audio file", "Video file", "Output file"]}]},
    {"Project": [{"Fork project": ["Name"]}, {"Go Supernova!": []}]}
]

procsitems = [
       { "fname": "AddAudio", "text": "Add audio upon existing video file", "descimage": "earth.png",
        "params": ["Video file (with/ without existing audio)", "Name of the audio file to be appended", "Starting time for the audio to be included", "Length of the audio file to addup", "Output file (blank for same video file)"]
    }, {
        "fname": "GetContours", "text": "Get image coordinates for doodling", "descimage": "earth.png" ,
        "params": ["Input image file", "Output file name (image & coordinates", "Camera Location (3D)", "Camera Looks at/ Whiteboard Center"]
    }, {"fname": "Manipulation", "text": "Basic image manipulation functions", "descimage": "earth.png" ,
        "params": ["Input image file", "New name for image", "Resize (Percentage)", "param3"]
    }, {"fname": "Manipulation", "text": "Advanced image manipulation - Remove background", "descimage": "earth.png" ,
        "params": ["Input file (image or gif)", "Output file name", "Color to remove", "Additional parameters"]
    }, {"fname": "MovieCreate", "text": "Make a movie from existing rush frames", "descimage": "earth.png" ,
        "params": ["First frame", "Last Frame", "Output movie name"]
    }, {"fname": "MovieCreate", "text": "Make a transparent gif from existing rush frames", "descimage": "earth.png" ,
        "params": ["Final image frame", "Start frame", "Last Frame", "Output movie name"]
    }, {"fname": "MovieCreate", "text": "Remove blue/ green screen from existing rushes", "descimage": "earth.png" ,
        "params": ["Start frame", "Last Frame", "Output movie name", "Color to remove\n(Red/Green/Blue/Yellow)"]
    }, {"fname": "ImageCreate", "text": "Make text image", "descimage": "earth.png" ,
        "params": ["File name", "Text", "Font name", "Font size"]
    }
]

nb = ttk.Notebook(root)
nb.pack()

frame_conf = pytkui.addstdframe (nb, "Application Setup")
appsetup = pyback.getappsetup()
projvars = appsetup['project']
sessionv = {}
uielem = {'conf': {}, 'acts': [], 'objs': [], 'logix': [], 'funcs': []}
pytkui.appuisetup (appset = appsetup, root =  frame_conf, uiset = uielem['conf'])
lstoryui = {}

def key_press(event):
    if event.char in ['0', '1', '2', '3', '4', '5']: nb.select(int(event.char))
    if event.char in ['x', 'X']:
        nb.select(5)
        frame_story_story()
root.bind('<Alt_L><Key>', key_press)

frame_acts = pytkui.addcnvframe (nb, "Defined Actions")
frame_objs = pytkui.addcnvframe (nb, "Defined Objects")
frame_logix = pytkui.addcnvframe (nb, "Logical Statements")
conf_frames = {'conf': frame_conf, 'acts': frame_acts, 'objs': frame_objs, 'logix': frame_logix}
frame_procs = pytkui.addcnvframe (nb, "Pre and Post processing")
frame_story = pytkui.addstdframe (nb, "User Stories and play")

lstoryui = pytkui.storyroomsetup (frame_story, projvars = projvars, boarditems = boarditems, session = session)
lprocsui = pytkui.procsfuncsetup (frame_procs, projvars = projvars, procsitems = procsitems)
#lstoryui['storybox'].insert(1.0, mystory)

def frame_acts_save ():
    cacts = pytkui.actsuiread(uiset = uielem['acts'], expand = projvars['expand'])
    pyback.saveuniv(which = 'actions', what = cacts, where = projvars['folder']+'/universe.js')

def frame_objs_save ():
    cobjs = pytkui.objsuiread(uiset = uielem['objs'])
    pyback.saveuniv(which = 'objects', what = cobjs, where = projvars['folder']+'/universe.js')

def frame_logix_save ():
    clogix = pytkui.logixuiread(uiset = uielem['logix'])
    pyback.saveuniv(which = 'logicals', what = clogix, where = projvars['folder']+'/universe.js')

def refresh_frame_buttons ():
    frame_size = frame_acts.grid_size()
    btn_acts_save = ttk.Button(frame_acts, text="\tSave Action configuration\t", command=frame_acts_save).grid(column=2, row=frame_size[1], sticky='ne')
    frame_size = frame_objs.grid_size()
    btn_objs_save = ttk.Button(frame_objs, text="\tSave Object configuration\t", command=frame_objs_save).grid(column=3, row=frame_size[1], sticky='ne')
    frame_size = frame_logix.grid_size()
    btn_logix_save = ttk.Button(frame_logix, text="\tSave Logical configuration\t", command=frame_logix_save).grid(column=3, row=frame_size[1], sticky='ne')

univ = pytkui.refresh_universe(uielem = uielem, conf_frames = conf_frames, appsetup = appsetup)
refresh_frame_buttons ()

def frame_conf_save():
    pytkui.port_conf_save (uielem['conf'], appsetup, univ)

def refresh_full_universe():
    lportui['acts'] = lportui['objs'] = lportui['logix'] = lportui['funcs'] = []
    if pyback.checkProject (folder = uielem['conf']['folder'].get()) == 1:
        UREP = messagebox.askquestion("Create New Project", "The project folder does not exists and would be created.\nAre you sure?")
        if UREP == 'no': return 0
        else: pyback.createProject (uielem['conf']['folder'].get())
    pytkui.refresh_universe(uielem = uielem, conf_frames = conf_frames, appsetup = appsetup)
    appsetup = pyback.getappsetup()
    projvars = appsetup['project']
    global gappvars
    gappvars['imgdest'] = pyback.getbasedir(lconf['portf_dir'])+'/rushes/'
    refresh_frame_buttons ()

btn_conf_save = ttk.Button(frame_conf, text="Save the configuration\n[Project level info]", command=frame_conf_save)
btn_conf_save.grid(sticky = 'w', column=4, row=5, rowspan = 3)
btn_conf_open = ttk.Button(frame_conf, text="     Open Workdir          ", command=refresh_full_universe)
btn_conf_open.grid(sticky = 'w', column=4, row=4)
gappvars['logtext'] = scrolledtext.ScrolledText(frame_conf, undo=True, width=115, height=25, bg="grey")
gappvars['logtext'].bind('<1>', lambda event: gappvars['logtext'].focus_set())
gappvars['logtext'].grid(column=1, row=12, sticky='n', columnspan=6)
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
    animation = pyback.response_textplay (gappvars['animurl'], {'Content-type': 'application/json'}, cuniv, storytext)
    cline = pyback.getchanged (gappvars['laststory'], storytext, change)
    serialized = p3dfunc.serialize (universe = cuniv, animation = animation, deserial = cline, portfolio = portf_dir.stem)
    serialized['inprod'] = str(inprod)
    if inprod == 1:    serialized['imgdest'] = gappvars['imgdest'] + 'pngs' + lstoryui['mprefix'].get()
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

def frame_stop_pngs():
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

def exec_play_frame (entparams = [], appsetup = {}, uielem = {}):
    session['stopact'] = 0
    params = pyback.framerunparams (entparams = entparams, appsetup = appsetup)
    imgdest = appsetup['project']['folder']+'/rushes/'
    print ("params", params)
    for frid in range(params['fromfr'], params['tillfr']+1):
        print ("frid", frid)
        imgfile = imgdest+"rush__"+"%04d"%(frid)+".png"
        if not os.path.isfile(imgfile): break
        image = Image.open(imgfile)
        image = image.resize((params['scrwide'], params['scrhigh']), Image.ANTIALIAS)
        root.myimg = myimg = ImageTk.PhotoImage(image)
        uielem['canvas'].create_image((250,250), image=myimg, anchor='center')
        uielem['canvas'].update()
        if session['stopact'] == 1:
            image.close()
            return 1
        time.sleep(1/params['fps'])
    return 1

def frame_story_cmd ():
    option1 = lstoryui['lbox1'].get(list(lstoryui['lbox1'].curselection())[0])
    option2 = lstoryui['lbox2'].get(list(lstoryui['lbox2'].curselection())[0])
    entparams = []
    for entry in lstoryui['param_ent']:
        entparams.append(entry['entry'].get())
    storytext = lstoryui['storybox'].get("1.0",END)
    coordstxt = lstoryui['coordbox'].get("1.0",END)
    cacts = pytkui.actsuiread(uiset = uielem['acts'], expand = projvars['expand'])
    cobjs = pytkui.objsuiread(uiset = uielem['objs'])
    clogix = pytkui.logixuiread(uielem['logix'])
    universe = {"actions": cacts, "objects": cobjs, "logicals": clogix}
    print("option1:", option1, "option2:", option2, "entparams:", entparams)
    retv = -1
    if option1.lower() == "Current rush".lower() and option2.lower() == "Play story".lower():
        retv = pyback.exec_play_story (entparams = entparams, appsetup = appsetup, universe = universe, story = storytext)
    if option1.lower() == "Current rush".lower() and option2.lower() == "Replay frames".lower():
        retv = exec_play_frame (entparams = entparams, appsetup = appsetup, uielem = lstoryui)
    if option1.lower() == "Current rush".lower() and option2.lower() == "Export video".lower():
        retv = pyback.exec_pic_export (entparams = entparams, appsetup = appsetup)
    if option1.lower() == "Current rush".lower() and option2.lower() == "Delete rush frames".lower():
        retv = pyback.exec_pic_delete (entparams = entparams, appsetup = appsetup)
    if option1.lower() == "Story".lower() and option2.lower() == "Save story".lower():
        retv = pyback.exec_save_story (entparams = entparams, appsetup = appsetup, story = storytext)
    if option1.lower() == "Story".lower() and option2.lower() == "Open story".lower():
        retv = pyback.exec_open_story (entparams = entparams, appsetup = appsetup)
        lstoryui['storybox'].delete('1.0', END)
        lstoryui['storybox'].insert(1.0, retv['data'])
    if option1.lower() == "Story".lower() and option2.lower() == "List stories".lower():
        retv = pyback.exec_list_filesets (entparams = entparams, appsetup = appsetup, folder = 'stories', suffix = '.story')
        lstoryui['coordbox'].delete('1.0', END)
        lstoryui['coordbox'].insert(1.0, "\n".join(retv['data']))
    if option1.lower() == "Co-ord".lower() and option2.lower() == "Save coords".lower():
        retv = pyback.exec_save_coords (entparams = entparams, appsetup = appsetup, coord = coordstxt, revert = 0)
    if option1.lower() == "Co-ord".lower() and option2.lower() == "Quick coords".lower():
        entparams[2] = '__quicktemp__'
        retv = pyback.exec_save_coords (entparams = entparams, appsetup = appsetup, coord = coordstxt, revert = 1)
        lstoryui['coordbox'].delete('1.0', END)
        lstoryui['coordbox'].insert(1.0, "\n".join(retv))
    if option1.lower() == "Co-ord".lower() and option2.lower() == "Open coords".lower():
        retv = pyback.exec_open_coords (entparams = entparams, appsetup = appsetup)
        lstoryui['coordbox'].delete('1.0', END)
        for ix in range(0, len(retv)-1):
            lstoryui['canvas'].create_line((retv[ix][0], retv[ix][1], retv[ix+1][0], retv[ix+1][1]))
        session['coords'] = retv
        lstoryui['coordbox'].insert(1.0, pprint.pformat(session['coords'], indent=2))
    if option1.lower() == "Co-ord".lower() and option2.lower() == "List coords".lower():
        retv = pyback.exec_list_filesets (entparams = entparams, appsetup = appsetup, folder = 'coords', suffix = '.coord')
        lstoryui['coordbox'].delete('1.0', END)
        lstoryui['coordbox'].insert(1.0, "\n".join(retv['data']))
    if option1.lower() == "Co-ord".lower() and option2.lower() == "Merge coords".lower():
        retv = pyback.exec_merge_coords (entparams = entparams, appsetup = appsetup)
    if option1.lower() == "Co-ord".lower() and option2.lower() == "Transform coords".lower():
        retv = pyback.exec_transform_coords (entparams = entparams, appsetup = appsetup)
    if option1.lower() == "Co-ord".lower() and option2.lower() == "Translate coords".lower():
        retv = pyback.exec_translate_coords (entparams = entparams, appsetup = appsetup)
    if option1.lower() == "Audio/ Video".lower() and option2.lower() == "List Audios".lower():
        retv = pyback.exec_list_filesets (entparams = entparams, appsetup = appsetup, folder = 'coords', suffix = ['.aac', '.mp3'])
        lstoryui['coordbox'].delete('1.0', END)
        lstoryui['coordbox'].insert(1.0, "\n".join(retv['data']))
    if option1.lower() == "Audio/ Video".lower() and option2.lower() == "List Videos".lower():
        retv = pyback.exec_list_filesets (entparams = entparams, appsetup = appsetup, folder = 'coords', suffix = ['.gif', '.mp4', '.mov', '.avi', '.wmv', '.webm'])
        lstoryui['coordbox'].delete('1.0', END)
        lstoryui['coordbox'].insert(1.0, "\n".join(retv['data']))
    if option1.lower() == "Audio/ Video".lower() and option2.lower() == "Merge Audio+Video".lower():
        retv = pyback.exec_save_merge (entparams = entparams, appsetup = appsetup)
    if option1.lower() == "Project".lower() and option2.lower() == "Fork project".lower():
        retv = pyback.exec_fork_project (entparams)
    if option1.lower() == "Project".lower() and option2.lower() == "Go Supernova!".lower():
        UREP = messagebox.askquestion("Go Supernova!", "All the data and files (not Videos) will be deleted\nAre you sure?")
        if UREP == 'no': return 0
        UREP = messagebox.askquestion("Final reminder**", "***Data will be deleted***\n***Data will not be recoverable***\n(Except media/ video folder)\nCancel now?")
        if UREP == 'yes': return 0
        return 1

btn_story_story = ttk.Button(frame_story, text="Execute the command (Selected Options)", command=frame_story_cmd).grid(column=1, row=3, columnspan=5, sticky="w")

def frame_procs_cmd ():
    fncix = lprocsui['flist'].get()
    print ("fncix", fncix)
    entparams = []
    for entry in lprocsui['param_ent']:
        entparams.append(entry['entry'].get())
    print ("entparams", entparams)
    if fncix == 'AddAudio: Add audio upon existing video file':
        retv = imagings.addaudiotovideo (videoentparams)
    if fncix == 'GetContours: Get image coordinates for doodling':
        retv = imagings.ui_find_image_contours (entparams = entparams, appsetup = appsetup)
    if fncix == 'Manipulation: Basic image manipulation functions':
        retv = imagings.ui_image_manipulation_basic (entparams = entparams, appsetup = appsetup)
    if fncix == 'Manipulation: Advanced image manipulation - Remove background':
        retv = imagings.ui_image_manipulation ('setcolortransparent', entparams = entparams, appsetup = appsetup)
    if fncix == 'MovieCreate: Make a movie from existing rush frames':
        retv = imagings.ui_basic_movie_creation (entparams = entparams, appsetup = appsetup)
    if fncix == 'MovieCreate: Make a transparent gif from existing rush frames':
        retv = imagings.ui_transparent_movie_creation (entparams = entparams, appsetup = appsetup)
    if fncix == 'MovieCreate: Remove blue/ green screen from existing rushes':
        retv = imagings.ui_remove_background_movie (entparams = entparams, appsetup = appsetup)
    if fncix == 'ImageCreate: Make text image':
        retv = imagings.ui_text_image_creation (entparams = entparams, appsetup = appsetup)
    return 1

btn_procs_procs = ttk.Button(frame_procs, text="Execute the command (Selected Options)", command=frame_procs_cmd).grid(column=2, row=18, sticky="w")

nb.enable_traversal()
root.mainloop()