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
from tkinter import messagebox 
from tkinter.messagebox import showinfo
import tkinter.scrolledtext as scrolledtext

import json    
import requests
import os
import re
import pprint
import time
from pathlib import Path
from PIL import ImageTk, Image

import p3dfunc
import pyback
import imagings
import pytkui

projvars = {}
projvars['animurl'] = 'http://localhost:5000/getanim'
session = {'coords': [], 'stopact': 0, 'logtext': None}

root = tkinter.Tk()
root.geometry("950x650")
root.resizable(0,0)
root.iconphoto(False, tkinter.PhotoImage(file='imgs/icon.png'))
root.title("Meme'er")

boarditems = [
    {"Current rush": [{"Play story": ["FPS", "Screen Size (Wide x Height)", "Play from frame#"]}, {"Replay frames": ["From frame#", "Upto frame#", "FPS"]}, {"Export video": ["Name of video", "FPS", "Frames range"]}, {"Delete rush frames": []}]},
    {"Story": [{"Save story": ["Name"]}, {"Open story": ["Name"]}, {"List stories": ["*NAME LIKE*"]}]},
    {"Co-ord": [{"Save coords": ["Camera Location (3D)", "Camera Looks at/\nWhiteboard Center", "Name"]}, 
        {"Quick coords": ["Camera Location (3D)", "Camera Looks at/\n(Whiteboard Center)"]}, {"Open coords": ["Name"]}, 
        {"List coords": ["*NAME LIKE*"]}, {"Merge coords": ["X list file", "Y list file", "Z list file"]}, 
        {"Screen Coordinates": ["Canvas Size (Wide x Height)", "Camera Location (3D)", "Camera Looks at/\nWhiteboard Center"]},
        {"Transform coords": ["Name", "Canvas Size (Wide x Height)", "Screen Size (Wide x Height)"]}, 
        {"Translate coords": ["Name", "Movement to right", "Movement to bottom"]},
        {"Get Screen Coordinates": ["Screen Size (Wide x Height)", "Camera Location (3D)", "Camera Looks at/\n(Whiteboard Center)"]}]},
    {"Audio/ Video": [{"List Audios": ["*NAME LIKE*"]}, {"List Videos": ["*NAME LIKE*"]}, {"Merge Audio+Video": ["Audio file", "Video file", "Output file"]}]},
    {"Project": [{"Fork project": ["Name"]}, {"Go Supernova!": []}]}
]

procsitems = [
       { "fname": "MovieCreate", "text": "Add audio upon existing video file", "descimage": "imgs/icon.png",
        "function": "ui_addaudiotovideo", "xtraprocess": {},
        "params": ["Video file (with/ without existing audio)", "Name of the audio file to be appended",
        "Starting time within video (seconds, default 0)", "Starting time for the audio (seconds, default 0)", "Length of the audio file to addup (seconds, default 0)",
        "Output file (blank for same video file)"]
    }, {"fname": "MediaCreate", "text": "Make image/video for a Text or Subtitle", "descimage": "imgs/icon.png" ,
        "function": "ui_text_image_creation", "xtraprocess": {},
        "params": ["Output file name", "Text to be imaged", "Font name (atleast 4 characters)", "Font size (default 16)", "As characterwise frames (1 char per frame, default NO)?"],
        "additional": "'color': (1, 1, 1, 255), 'spacing': 4"
    }, {"fname": "ModelCreate", "text": "Make Panda3d model for frameset/video", "descimage": "imgs/icon.png" ,
        "function": "ui_p3dmodel_creation", "xtraprocess": {},
        "params": ["Input file/folder", "Output file name", "Frames range (default is all frames)", "FPS (leave blank for using video's default)"]
    }, {"fname": "Pre-process", "text": "Basic image manipulation functions", "descimage": "imgs/icon.png",
        "function": "ui_image_manipulation_basic", "xtraprocess": {},
        "params": ["Input image file", "Output file name", "Feature of the Image to be changed\n('contrast'/'color'/'brightness'/'sharpness'/'invert')", "New value (number)\n Or type 'range' for values from 0 to 100 (100 images)"]
    }, {"fname": "Pre-process", "text": "Advanced image manipulation - Background processing", "descimage": "imgs/icon.png" ,
        "function": "ui_image_manipulation_rmback", "xtraprocess": {},
        "params": ["Input image file", "Output file name", "Background removal method (mrcnn / ibrt / screen / color)", "Color if method is 'screen' or 'color'"]
    }, {"fname": "Pre-process", "text": "Generate illustrations from existing image/s", "descimage": "imgs/icon.png" ,
        "function": "ui_image_manipulation_craft", "xtraprocess": {},
        "params": ["Input image/s", "Output file name", "Special effect type (doodle / cartoon / pencil sketch)"]
    }, {"fname": "Pre-process", "text": "Make a transparent movie from manipulated rush frames", "descimage": "imgs/icon.png" ,
        "function": "image_manual_bgremoval", "xtraprocess": {},
        "params": ["Final image frame", "Start frame", "Last Frame", "Output movie name"]
    }, {"fname": "Release", "text": "Prepare stage for release", "descimage": "imgs/icon.png" ,
        "function": "ui_prepare_stage", "xtraprocess": {},
        "params": ["Movie folder names (comma separated list)", "Output Stage Name", "Movie format (mp4, mov etc.)"]
    }
]

nb = ttk.Notebook(root)
nb.pack()

frame_conf = pytkui.addstdframe (nb, "Application Setup")
appsetup = pyback.getappsetup()
projvars = appsetup['project']
sessionv = {}
uielem = {'conf': {}, 'acts': [], 'objs': [], 'logix': []}
pytkui.appuisetup (appsetup = appsetup, root =  frame_conf, uiset = uielem['conf'])

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
    pyback.saveuniv(which = 'actions', what = cacts, where = projvars['name']+'/universe.js')

def frame_objs_save ():
    print ("i am in")
    cobjs = pytkui.objsuiread(uiset = uielem['objs'])
    print ("cobjs", cobjs)
    pyback.saveuniv(which = 'objects', what = cobjs, where = projvars['name']+'/universe.js')

def frame_logix_save ():
    clogix = pytkui.logixuiread(uiset = uielem['logix'])
    pyback.saveuniv(which = 'logicals', what = clogix, where = projvars['name']+'/universe.js')

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
    uielem['acts'] = uielem['objs'] = uielem['logix'] = []
    if pyback.checkProject (name = uielem['conf']['name'].get()) == 0:
        UREP = messagebox.askquestion("Create New Project", "The project folder does not exists and would be created.\nAre you sure?")
        if UREP == 'no': return 0
    projectinfo = pyback.createProject (uielem['conf']['name'].get())
    appsetup = pyback.getappsetup()
    appsetup['project'] = projectinfo
    pyback.putappsetup(appsetup)
    pytkui.refresh_universe(uielem = uielem, conf_frames = conf_frames, appsetup = appsetup)
    refresh_frame_buttons ()

btn_conf_save = ttk.Button(frame_conf, text="Save the configuration\n[Project level info]", command=frame_conf_save)
btn_conf_save.grid(sticky = 'w', column=4, row=5, rowspan = 3)
btn_conf_open = ttk.Button(frame_conf, text="Open/ Refresh this project", command=refresh_full_universe)
btn_conf_open.grid(sticky = 'w', column=4, row=4)
session['logtext'] = scrolledtext.ScrolledText(frame_conf, undo=True, width=115, height=25, bg="grey")
session['logtext'].bind('<1>', lambda event: appsetup['logtext'].focus_set())
session['logtext'].grid(column=1, row=12, sticky='n', columnspan=6)
pyback.logit (session['logtext'], "Application logging------------------------------------")

def exec_play_frame (entparams = [], appsetup = {}, uielem = {}):
    session['stopact'] = 0
    params = pyback.framerunparams (entparams = entparams, appsetup = appsetup)
    imgdest = appsetup['project']['name']+'/rushes/'
    print ("params", params)
    for frid in range(params['fromfr'], params['tillfr']+1):
        print ("frid", frid)
        imgfile = imgdest+"frame__"+"%06d"%(frid)+".png"
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
    if option1.lower() == "Co-ord".lower() and option2.lower() == "Get Screen Coordinates".lower():
        retv = pyback.exec_screen_coords (entparams = entparams, appsetup = appsetup)
        UREP = messagebox.askquestion("Visible screen limits/ coordniates", retv + "\n\nCopy to clipboard?")
        if UREP == 'yes':
            root.clipboard_clear()
            root.clipboard_append(retv)
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
    for cmbuitem in procsitems:
        if cmbuitem['fname'] + ": " + cmbuitem['text'] == fncix:
            imagings.base_function (cmbuitem['function'], entparams = entparams, appsetup = appsetup)
    return 1

btn_procs_procs = ttk.Button(frame_procs, text="Execute the command (Selected Options)", command=frame_procs_cmd).grid(column=2, row=18, sticky="w")

nb.enable_traversal()
root.mainloop()