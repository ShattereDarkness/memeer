import os
from pathlib import Path
import pprint
import json
import re
import shutil
import p3dfunc
import subprocess
from itertools import chain
import copy

import requests
appfile = 'appsetup.js'
basedir = Path()

def port_conf_save (appsetup):
    appfile = 'appsetup.js'
    print ("writng", appsetup)
    putUniverseJS (appsetup, appfile)
    saveuniv (which = 'projectinfo', what = appsetup['project'], where = appsetup['project']['name']+'/universe.js')

def saveuniv(which = 'XXX', what = [], where = 'XXX'):
    nuniv = getUniverseJS (where)
    nuniv[which] = what
    putUniverseJS (nuniv, where)

def getappsetup ():
    with open(appfile) as lujs: appsetup = json.load(lujs)
    return appsetup

def putappsetup (appsetup):
    with open(appfile, "w") as lujs: json.dump(appsetup, lujs, indent=4)
    return 1

def getUniverseJS (univfile):
    with open(univfile) as lujs: univ = json.load(lujs)
    return univ

def putUniverseJS (univ, univfile):
    with open(univfile, "w") as lujs: json.dump(univ, lujs, indent=4)
    return 1

def savethedata(lportui):
    print(lportui['desc'].get())
    return 1

def getbasedir(portf_dir):
    portf_dir = Path(portf_dir)
    return portf_dir.stem

def checkProject (name =  ''):
    projdir = Path(name)
    if not projdir.is_dir(): return 0
    return 1

def createProject (name =  ''):
    retval = {}
    projdir = Path() / name
    if not projdir.exists(): projdir.mkdir (parents = False, exist_ok = True)
    if not projdir.exists() or not projdir.is_dir(): return {}
    universe = projdir / 'universe.js'
    if not universe.is_file():
        projectinfo = {"winsize": "500,500", "preview": 1, "fps": "24", "detail": "Universe from template", "expand": 1, "canvas": "500,500"}
        projectinfo['name'] = projdir.stem
        retval = projectinfo
        univ = {'projectinfo': projectinfo, 'namedetail': 'from Meemer'}
        with open(universe, "w") as lujs: json.dump(univ, lujs)
    else:
        with open(universe) as lujs: univ = json.load(lujs)
        retval = univ['projectinfo']
    for directory in ['media', 'temp', 'model', 'model/action', 'coords', 'stories', 'video', 'audio', 'rushes', 'rushes/temp']:
        newdir = projdir / directory
        newdir.mkdir (parents = False, exist_ok = True)
    return retval

def check2files (path1=Path('.'), path2=Path('.'), fstem='', suffix1='', suffix2=''):
    if (path1 / (fstem+suffix1)).exists() and (path2 / (fstem+suffix2)).exists(): return 0
    if (path1 / (fstem+suffix1)).exists() and not (path2 / (fstem+suffix2)).exists(): return 1
    if not (path1 / (fstem+suffix1)).exists() and (path2 / (fstem+suffix2)).exists(): return 2
    return 3

def getpermissiblefps (*args):
    print (f"getpermissiblefps:\n\targs{args}")
    for val in args:
        if isinstance(val, int) and val > 0: return val
        if isinstance(val, dict) and 'fps' in val and isinstance(val['fps'], int) and val['fps']> 0: return val['fps']
    return 24

def create_movie_frames (ifile = Path(), folder = Path(), owrite = 0, resize = 0):
    print (f"create_movie_frames:\n\tifile={ifile}\n\tfolder={folder}\n\towrite={owrite}")
    retval = {'fps': 1, 'frame': 0}
    cmdstr = "ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=avg_frame_rate \"" + str(ifile) + "\""
    print (f"cmdstr: {cmdstr}")
    avgfps = (subprocess.run(cmdstr, capture_output=True)).stdout.decode('unicode_escape')[:-2]
    print (f"avgfps: {avgfps}")
    retval['fps'] = round(float(avgfps.split('/')[0])/float(avgfps.split('/')[1]))
    if folder['vid'].exists() and owrite == 0: return retval
    if folder['vid'].exists():
        files = folder['vid'].glob('*.png')
        for f in files: f.unlink()
    else:
        folder['vid'].mkdir()
        folder['aud'].mkdir (exist_ok=True)
    if resize == 0: videocmd = "ffmpeg -i \"" + str(ifile) + "\" -vf scale=320:-1 -vsync 0 \"" + str(folder['vid']) + "/frame__%6d.png" + "\" -loglevel error"
    else: videocmd = "ffmpeg -i \"" + str(ifile) + "\" -vsync 0 \"" + str(folder['vid']) + "/frame__%6d.png" + "\" -loglevel error"
    print ("videocmd:", videocmd)
    os.system(videocmd)
    audiocmd = "ffmpeg -i \"" + str(ifile) + "\" -vn -acodec copy \"" + str(folder['aud']) + ".aac" + "\" -y -loglevel error"
    print ("audiocmd:", audiocmd)
    os.system(audiocmd)
    return retval

def create_media_p3dmodel (ifile = Path(), owrite = 0, appsetup = {}, fps = -1):
    print (f"create_media_p3dmodel:\n\tifile={ifile}\n\towrite={owrite}\n\tappsetup={appsetup}")
    retval = {'msg': '', 'param': {}}
    projdir = Path(appsetup['project']['name'])
    eggfile = projdir / 'model' / (ifile.stem+'.egg')
    if eggfile.exists() and owrite == 0: return {'return': 'pass', 'reason': "file already exists"}
    if ifile.parent != projdir / 'media':
        newfile = projdir/'media'/ifile.name
        print ("Newfile", newfile, newfile.resolve().exists())
        if not newfile.exists() or (newfile.exists() and owrite == 1):
            shutil.copytree(ifile, newfile)
        ifile = newfile
    asmovie = ifile.is_dir()
    cmf = None
    if ifile.suffix in appsetup['movies']:
        existf = {'vid': projdir/'media'/ifile.stem, 'aud': projdir/'audio'/ifile.stem}
        cmf = create_movie_frames (ifile = ifile, folder = existf, owrite = owrite, resize=appsetup['vidtoimg'])
        asmovie = 1
    errorinnamecorrection = ifile.stem.replace(' ', '?')
    if asmovie == 1:
        fps = getpermissiblefps (cmf, fps, appsetup, 30)
        cmdstr = "egg-texture-cards -o \"" + ifile.stem + ".egg\" -b -p 10,10 -fps "+str(fps)+" ../media/" + errorinnamecorrection + "/*.png"
    else: cmdstr = "egg-texture-cards -o \"" + ifile.stem + ".egg\" -b -p 10,10 ../media/" + errorinnamecorrection + ifile.suffix
    print (f"create_media_p3dmodel: cmdstr={cmdstr}")
    try:
        os.chdir(projdir / 'model')
        print ("before: os.getcwd()", os.getcwd())
        cmdval = os.system(cmdstr)
    finally: os.chdir('../..')
    print ("after: os.getcwd()", os.getcwd())
    return cmdval

def reverse_file_check (univ={}, appsetup={}, model_dir = Path(), action_dir = Path()):
    for mobject in univ['objects']:
        newacts = {}
        for msyn in mobject['syns']:
            for mact, mactd in mobject['acts'].items():
                objactf = [action_dir / (msyn+"__"+mact+".bam"), action_dir / (msyn+"__"+mact+".egg")]
                if (objactf[0].is_file() or objactf[1].is_file()) and mact not in newacts: newacts[mact] = mactd
        mobject['acts'] = copy.deepcopy(newacts)
    print (f"reverse_file_check univ: {univ}")
    return univ['objects']

def getUniverseData (name =  '', appsetup = {}):
    print (f"getUniverseData:\n\tname={name}\n\tappsetup={appsetup}")
    defaultmove = ['move', 'locate', 'generate']
    projdir = Path() / name
    if not projdir.is_dir(): return retval
    universe = projdir / 'universe.js'
    with universe.open('r') as univjs: univ = json.load(univjs)
    if 'namedetail' not in univ or univ['namedetail'] == '':
        univ['namedetail'] = 'Basic environment for create at '+appsetup['project']['name']+'. Self initialized'
    model_dir = projdir / 'model'
    action_dir = model_dir / 'action'
    media_dir = projdir / 'media'
    # Start checking for models and actions
    if 'actions' not in univ: univ['actions'] = []
    if 'objects' not in univ: univ['objects'] = []
    for mfile in media_dir.iterdir():
        if not mfile.is_file(): continue
        create_media_p3dmodel (ifile = mfile, owrite = 0, appsetup = appsetup)
    univobjects = []
    for muniv in univ['objects']:
        if (model_dir / (muniv['file'])).exists(): univobjects.append(muniv)
    univ['objects'] = univobjects
    for mfile in chain(model_dir.glob('*.egg'), model_dir.glob('*.bam'), model_dir.glob('*.gltf')):
        if len(list(filter(lambda x : x['file'] == mfile.name, univ['objects']))) > 0: continue
        univ['objects'].append({'syns': [mfile.stem], 'move': defaultmove, 'jjrb': [], 'acts': {}, 'joint': '', 'file': mfile.name})
    for commact in ['move', 'locate', 'generate', 'draw']:
        if len(list(filter(lambda x : x['func'] == commact, univ['actions']))) == 0:
            univ['actions'].append({"func": commact, "syns": [commact],"jjrb": []})
    for afile in chain(action_dir.glob('*.egg'), action_dir.glob('*.bam')):
        print ("afile", afile)
        if '__' not in afile.stem: continue
        actor, anime = afile.stem.split ('__', 1)
        actorfile = [actor+'.egg', actor+'.bam']
        if len(list(filter(lambda x : actor in x['syns'], univ['objects']))) == 0: continue
        if len(list(filter(lambda x : x['func'] == anime, univ['actions']))) == 0:
            univ['actions'].append({'jjrb': [], 'syns': [anime], 'func': anime, 'show': 1})
        mobjects = list(filter(lambda x : actor in x['syns'], univ['objects']))
        print ("mobjects and anime: ", mobjects, anime)
        for mobject in mobjects:
            if anime in mobject['acts']: continue
            mobject['acts'][anime] = {"fstart": 1, "flast": 9999}
    univ['objects'] = reverse_file_check(univ=univ, appsetup=appsetup, model_dir = model_dir, action_dir = action_dir)
    print (f"Now the univ is: {univ}")
    if 'logicals' not in univ: univ['logicals'] = []
    if 'projectinfo' not in univ: univ['projectinfo'] = appsetup['project']
    with universe.open('w') as univjs: json.dump(univ, univjs, indent=4)
    return univ

def entdefaultparams (ix, params, projvars):
    if params[ix] == 'FPS': return projvars['fps']
    if params[ix] == 'Screen Size (Wide x Height)': return projvars['winsize']
    if params[ix] == 'Canvas Size (Wide x Height)': return projvars['canvas']
    if params[ix] == 'Play from frame#': return '1'
    if params[ix] == 'From frame#': return '1'
    if params[ix] == 'Upto frame#': return '-1'
    if params[ix] == 'Draft (Yes/No)': return projvars['preview']
    if params[ix] == 'Frames range': return '1, -1'
    if params[ix] == '*NAME LIKE*': return '*'
    if params[ix] == 'Camera Location (3D)': return '0, -120, 0'
    if params[ix] == 'Camera Looks at/\nWhiteboard Center': return '0, 0, 0'
    return ""

def splittext (text = '', rtyp = str, sep = ','):
    retval = []
    for nstr in text.split(sep):
        if nstr == '': continue
        retval.append(rtyp(nstr.strip()))
    return retval

def loadsynos (uwords, verbjs, expand):
    retval = []
    for uword in uwords:
        if ((expand == 0 and not re.match(".+\+$", uword)) or (expand == 1 and re.match(".+-$", uword))):
            retval.append(uword)
            continue
        if re.match(".+\+$", uword): uword = uword[:-1]
        for fwords in verbjs:
            if not uword in fwords: continue
            retval.extend(fwords)
        retval.append(uword)
    retval=list(set(retval))
    return retval

def updateuniverseforsend (universe = {}, appsetup = {}):
    def removeextraverb (actions):
        for action in actions:
            nsyns = []
            for syns in action['syns']:
                verbs = syns.split(",")
                for verb in verbs:
                    nverb = verb.strip()
                    if re.match(".+-$", nverb):
                        nverb = nverb[:-1]
                    nsyns.append(nverb)
            action['syns'] = nsyns
        return 1
    def updatejoints (objects, joints = {}):
        for model in objects:
            if model['joint'] == '' or model['joint'] not in joints: continue
            model['joint'] = joints[model['joint']]
    def additionalobj (objects):
        objects.insert(0, {'file': 'camera', 'acts': {}, 'syns': ['camera'], 'jjrb': [], 'move': ['move', 'locate', 'looks'], 'joint': ''})
        objects.insert(1, {'file': 'line', 'acts': {}, 'syns': ['line'], 'jjrb': [], 'move': ['draw'], 'joint': ''})
        objects.insert(2, {'file': 'subtext', 'acts': {}, 'syns': ['subtitle', 'text'], 'jjrb': [], 'move': ['draw'], 'joint': ''})
    def parselogical (logicals):
        print ("logicals", logicals)
        for logical in logicals:
            logical['basic'] = p3dfunc.storyparse (logical['basic'])[0]
            logical['addon'] = p3dfunc.storyparse ("\n".join(logical['addon']))
        return 1
    removeextraverb (universe['actions'])
    updatejoints (universe['objects'], joints = appsetup['joint'])
    additionalobj (universe['objects'])
    parselogical (universe['logicals'])
    return 1

def getscreensize (text, w, h):
    try:
        winsize = text.replace('X', 'x')
        winsize = text.replace('x', ',')
        scrwide = list(map(int, winsize.split(',')))[0]
        scrhigh = list(map(int, winsize.split(',')))[1]
        if scrwide * scrhigh < 90: return w, h
        else: return scrwide, scrhigh
    except: return w, h
    return 500, 500

def forceint(text, default = -1):
    try: return int(text)
    except: return default

def exec_play_story (entparams = [], appsetup = {}, universe = {}, story = ''):
    print ("appsetup:", appsetup)
    print ("entparams:", entparams)
    fps = appsetup['project']['fps'] if forceint(entparams[0]) == -1 else forceint(entparams[0])
    scrwide, scrhigh = getscreensize (entparams[1], 0, 0) 
    if scrwide * scrhigh < 2: scrwide, scrhigh = getscreensize (appsetup['project']['winsize'], 500, 500) 
    fframe = 1 if forceint(entparams[2]) == -1 else forceint(entparams[2])
    print ("fps, scrwide, scrhigh, frame", fps, scrwide, scrhigh, fframe)
    updateuniverseforsend (universe = universe, appsetup = appsetup)
    nlu = response_textplay (appsetup['meemerurl'], {'Content-type': 'application/json'}, universe, p3dfunc.storyparse(story), appsetup)
    if nlu == -1: return {'code': -1, 'data': 'error_connection'}
    serialized = p3dfunc.serialized (nlu['cmdlets'], nlu['rushobjlst'], universe = universe, appsetup = appsetup, fframe = fframe, fps = fps, winsize = [scrwide, scrhigh])
    os.system('ppython p3dpreview.py ' + str(serialized["data"]))
    imgsrc = Path(appsetup['project']['name']) / 'rushes' / 'temp/'
    imgdst = Path(appsetup['project']['name']) / 'rushes'
    png_overwrites (csframe = 1, tdframe = 1, clframe = 999999, imgsrc = imgsrc, imgdst = imgdst, owrite = 1, action = ['move', 'refresh'])
    return {'code': 0, 'data': 'temp_rushframes'}

def png_overwrites (csframe = 1, tdframe = 0, clframe = 999999, imgsrc = Path(), imgdst = Path(), owrite = 0, action = ['append', 'copy']):
    print (f"png_overwrites:\n\tcsframe={csframe}\n\ttdframe={tdframe}\n\tclframe={clframe}\n\timgsrc={imgsrc}\n\timgdst={imgdst}\n\towrite={owrite}\n\taction={action}")
    if not imgdst.is_dir(): imgdst.mkdir(parents=True, exist_ok=True)
    counts = 0
    if 'append' in action:
        for frid in range(1, 999999):
            oldimg = imgdst / ("frame__"+"%06d"%(frid)+".png")
            if oldimg.is_file(): tdframe = -1*frid
            else: break
        print (f"tdframe: {tdframe}")
    for frid in range(csframe, clframe+1):
        if frid < csframe: continue
        oldimg = imgsrc / ("frame__"+"%06d"%(frid)+".png")
        if 'append' in action: newimg = imgdst / ("frame__"+"%06d"%(frid-tdframe-csframe+1)+".png")
        else: newimg = imgdst / ("frame__"+"%06d"%(frid-tdframe)+".png")
        if not oldimg.is_file(): break
        if newimg.exists() and owrite == 1: newimg.unlink()
        if owrite == 0 and newimg.is_file(): continue
        shutil.copy(oldimg, newimg)
        if  'move' in action: oldimg.unlink()
        counts = counts + 1
    if 'refresh' in action:
        for file in imgsrc.iterdir(): file.unlink()
    print ("PNG COPY COMPLETED")
    return counts

def exec_save_story (entparams = [], appsetup = {}, story = ''):
    if entparams[0] == '': return 0
    filename = Path(appsetup['project']['name']) / 'stories' / entparams[0]
    if filename.suffix != '.story': filename = Path(appsetup['project']['name']) / 'stories' / (entparams[0]+'.story')
    filename.write_text(story)
    return 1

def exec_open_story (entparams = [], appsetup = {}):
    if entparams[0] == '': return 0
    filename = Path(appsetup['project']['name']) / 'stories' / entparams[0]
    if filename.suffix != '.story': filename = Path(appsetup['project']['name']) / 'stories' / (entparams[0]+'.story')
    if not filename.is_file(): return {'code': 1, 'data': ''}
    return {'code': 0, 'data': filename.read_text()}

def exec_list_filesets (entparams = [], appsetup = {}, folder = '___', suffix = '.tmp'):
    retval = {'code': 0, 'data': []}
    dirpath = Path(appsetup['project']['name']) / folder
    entparams[0] = '*' + entparams[0] + '*'
    entparams[0] = re.sub("\*+", "*", entparams[0])
    for file in list(dirpath.glob(entparams[0])):
        if isinstance(suffix, str) and file.suffix != suffix: continue
        if isinstance(suffix, list) and file.suffix not in suffix: continue
        if file.suffix == '.coord':
            with open(file) as lpts: coordls = json.load(lpts)
            if 'pixel' in coordls: retval['data'].append('File name: ' + file.name + ', Frames: ' + str(len(coordls['pixel'])))
            else: retval['data'].append('File name: ' + file.name + ', Frames: *PIXEL INFO MISSING*')
        else:
            retval['data'].append(file.name)
    return retval

def exec_save_coords (entparams = [], appsetup = {}, coord = [], revert = 0, addxtra = {}):
    if entparams[0] == '': entparams[0] = '0, -120, 0'
    if entparams[1] == '': entparams[1] = '0, 0, 0'
    if entparams[2] == '': return 1
    filename = Path(appsetup['project']['name']) / 'coords' / entparams[2]
    if filename.suffix != '.coord': filename = Path(appsetup['project']['name']) / 'coords' / (entparams[2]+'.coord')
    jsondat = {'campos': entparams[0], 'bcenter': entparams[1], 'pixel': json.loads(coord), 'coord': [], 'addxtra': addxtra}
    if revert == 0: jsondat['pixel'].append (jsondat['pixel'][len(jsondat['pixel'])-1])
    with open(filename, "w") as lpts: json.dump(jsondat, lpts)
    os.system('ppython p3dcoords.py ' + str(filename))
    if revert == 0: return 1
    with open(filename) as lpts: coordls = json.load(lpts)
    return list(map(str, coordls['coord']))

def exec_open_coords (entparams = [], appsetup = {}, jskey = 'pixel'):
    if entparams[0] == '': return 1
    filename = Path(appsetup['project']['name']) / 'coords' / entparams[0]
    if filename.suffix != '.coord': filename = Path(appsetup['project']['name']) / 'coords' / (entparams[0]+'.coord')
    with open(filename) as lpts: coordls = json.load(lpts)
    if jskey == 'all': return coordls
    return coordls[jskey]

def exec_merge_coords (entparams = [], appsetup = {}):
    fdata = [None, None, None]
    def fixinitemlist (lfrom = 1, linto = 1):
        retval = [0]
        for ix in range(1, linto):
            fix = round(ix*(lfrom/(linto-1)), 0)
            retval.append(int(fix))
        return retval
    for ix in range(0,3):
        if entparams[ix] == '': return 2
        fdata[ix] = exec_open_coords (entparams = [entparams[ix], '', ''], appsetup = appsetup, jskey = 'coord')
        fdata[ix].pop()
    datalen = min(len(fdata[0]), len(fdata[1]), len(fdata[2]))
    itemls = [None, None, None]
    for ix in range(0,3):
        itemls[ix] = fixinitemlist (lfrom = len(fdata[ix])-1, linto = datalen)
    coordjs = {'X_coord': entparams[0], 'Y_coord': entparams[1], 'Z_coord': entparams[2], 'coord': []}
    for ix in range(0, datalen):
        X_coord = fdata[0][itemls[0][ix]][0]
        Y_coord = fdata[1][itemls[1][ix]][1]
        Z_coord = fdata[2][itemls[2][ix]][2]
        coordjs['coord'].append([X_coord, Y_coord, Z_coord])
    filename = Path(appsetup['project']['name']) / 'coords' / ("+".join(entparams)+'.coord')
    with open(filename, "w") as lpts: json.dump(coordjs, lpts)
    return 1

def exec_transform_coords (entparams = [], appsetup = {}):
    if entparams[0] == '': return 1
    if entparams[1] == '': entparams[1] = appsetup['project']['canvas']
    if entparams[2] == '': entparams[2] = appsetup['project']['winsize']
    framerunparams (entparams = entparams, appsetup = appsetup)
    canw, canh = getscreensize (entparams[1], 500, 500)
    winw, winh = getscreensize (entparams[2], 500, 500)
    nratio = max(winw, winh)/min(winw, winh)
    coordfdata = exec_open_coords (entparams = entparams, appsetup = appsetup, jskey = 'all')
    campos = coordfdata['campos']
    bcenter = coordfdata['bcenter']
    pixels = coordfdata['pixel']
    npixels = []
    for pixel in pixels:
        rwpix, rhpix = 250+int((pixel[0]-250)*nratio), 250+int((pixel[1]-250)*nratio)
        print ("from pixel to rwpix, rhpix", pixel, rwpix, rhpix)
        npixels.append([rwpix, rhpix])
    nfile = 'T_' + entparams[0]
    exec_save_coords (entparams = [campos, bcenter, nfile], appsetup = appsetup, coord = str(npixels), revert = 0, addxtra = {'tform': entparams})

def set_multifile_coords (file = '', appsetup = {}, addlogic = 0):
    ifile = Path(appsetup['project']['name']) / 'coords' / file
    if ifile.suffix != '.coord': ifile = Path(appsetup['project']['name']) / 'coords' / (file + '.coord')
    coordls = exec_open_coords (entparams = [ifile.stem], appsetup = appsetup, jskey = 'all')
    if 'addxtra' not in coordls or 'group' not in coordls['addxtra']: return 1
    groups = coordls['addxtra']['group']
    startf, addons = 1, []
    for gx in range(1, len(groups)):
        npixels = coordls['pixel'][groups[gx-1]:groups[gx]] + [coordls['pixel'][groups[gx]-1]]
        ncoords = coordls['coord'][groups[gx-1]:groups[gx]] + [coordls['coord'][groups[gx]-1]]
        nfilenm = Path(ifile.parent.parent) / 'coords' / ("%04d" % (gx) + ifile.stem + ".coord")
        njson = {'campos': coordls['campos'], 'bcenter': coordls['bcenter'], 'pixel': npixels, 'coord': ncoords, 'basef': ifile.stem}
        with open(nfilenm, "w") as lpts: json.dump(njson, lpts)
        addons.append("line is drawn @f(" + nfilenm.stem + ") #"+str(startf)+'-#'+str(startf+len(npixels)))
        startf = startf + len(npixels)
    print (addlogic, "addlogic")
    if addlogic == 0: return 1
    univfile = Path(appsetup['project']['name']) / 'universe.js'
    universe = getUniverseJS (univfile)
    universe['logicals'].append({'basic': 'line is drawn logic for image '+ifile.name, 'addon': addons})
    putUniverseJS (universe, univfile)
    return 1

def exec_translate_coords (entparams = [], appsetup = {}):
    if entparams[0] == '': return 1
    entparams[1] = 0 if entparams[1] == '' else forceint(entparams[1], default = 0)
    entparams[2] = 0 if entparams[2] == '' else forceint(entparams[2], default = 0)
    if entparams[1] == 0 and entparams[2] == 0: return 1
    coordfdata = exec_open_coords (entparams = entparams, appsetup = appsetup, jskey = 'all')
    campos = coordfdata['campos']
    bcenter = coordfdata['bcenter']
    pixels = coordfdata['pixel']
    npixels = []
    for pixel in pixels:
        npixels.append([pixel[0]+entparams[1], pixel[1]+entparams[2]])
    nfile = 'Tl_' + entparams[0]
    exec_save_coords (entparams = [campos, bcenter, nfile], appsetup = appsetup, coord = str(npixels), revert = 0, addxtra = {'tlate': entparams})
    set_multifile_coords (file = nfile, appsetup = appsetup, addlogic = 0)

def exec_screen_coords (entparams = [], appsetup = {}):
    if entparams[0] == '': entparams[0] = appsetup['project']['winsize']
    if entparams[1] == '': entparams[1] = '0, -120, 0'
    if entparams[2] == '': entparams[2] = '0, 0, 0'
    cmdstr = "python p3dlimits.py \""+str(entparams[2])+"\" \""+str(entparams[1])+"\" \""+str(entparams[0])+"\""
    retval = (subprocess.run(cmdstr, capture_output=True)).stdout.decode('unicode_escape')
    return retval

def exec_save_merge (entparams = [], appsetup = {}):
    for ix in range(0,3):
        if entparams[ix] == '': return 2
    audio = Path(appsetup['project']['name']) / 'audio' / entparams[0]
    video = Path(appsetup['project']['name']) / 'video' / entparams[1]
    merge = Path(appsetup['project']['name']) / 'video' / entparams[2]
    if merge.suffix == '': merge = Path(appsetup['project']['name']) / 'video' / (entparams[2]+video.suffix)
    cmdstr = "ffmpeg -i " + video.name + " -i " + aidio.name + " -c:v copy -map 0:v:0 -map 1:a:0 " + merge.name
    os.system(cmdstr)
    return 1

def exec_fork_project (entparams = [], appsetup = {}):
    if entparams[0] == '': return 2
    shutil.copytree(Path(appsetup['project']['name']), entparams[0])
    shutil.rmtree(entparams[0]+'video')
    shutil.rmtree(entparams[0]+'audio')
    shutil.rmtree(entparams[0]+'rushes')
    os.mkdir(entparams[0]+'video')
    os.mkdir(entparams[0]+'audio')
    os.mkdir(entparams[0]+'rushes')
    os.mkdir(entparams[0]+'rushes/temp')
    return 1

def response_textplay (animurl, headers, cuniverse, story, appsetup):
    if appsetup['democheck'] == 1:
        return {'cmdlets': [{'bspec': {'locupto': [], 'locfrom': [], 'locpos': [0.0, 2.0, 7.0, 0.0, 0.0, 0.0, 75.0, 50.0, 50.0], 'locfile': '', 'sttmts': [], 'frames': [1, 120], 'oid': 303}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_named', 'params': {'modid': 1, 'weight': 1, 'isnew': 1}, 'frames': [1, 120]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [], 'locfile': 'somelist1', 'sttmts': [], 'frames': [61, 120], 'oid': 304}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_exists', 'params': {'modid': 2, 'weight': 1, 'isnew': 1}, 'frames': [61, 120]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [], 'locfile': '', 'sttmts': [], 'frames': [121, 150], 'oid': 310}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_exists', 'params': {'modid': 1, 'weight': 4, 'isnew': 0}, 'frames': [121, 150]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [], 'locfile': '', 'sttmts': [], 'frames': [], 'oid': 306}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_named', 'params': {'modid': 3, 'weight': 1, 'isnew': 1}, 'frames': [151, 271]}, {'bspec': {'locupto': [21.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0], 'locfrom': [-21.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0], 'locpos': [], 'locfile': '', 'sttmts': [], 'frames': [61, 120], 'oid': 307}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_does', 'params': {'modid': 3, 'weight': 6, 'isnew': 0, 'type': 'acts', 'func': 'run', 'repeat': 0}, 'frames': [61, 120]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [], 'locfile': 'Y_driveaway', 'sttmts': [], 'frames': [1, 60], 'oid': 308}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_does', 'params': {'modid': 4, 'weight': 4, 'isnew': 1, 'type': 'move', 'func': 'move', 'repeat': 0}, 'frames': [1, 60]}, {'bspec': {'locupto': [], 'locfrom': [], 'locpos': [-21.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0], 'locfile': '', 'sttmts': [], 'frames': [], 'oid': 309}, 'cspec': {'locfile': '', 'locfrom': [], 'locupto': [], 'locpos': [], 'frames': []}, 'func': 'object_exists', 'params': {'modid': 5, 'weight': 2, 'isnew': 1}, 'frames': [272, 392]}], 'rushobjlst': [{'file': 'camera', 'acts': {}, 'syns': ['camera'], 'jjrb': [], 'move': ['move', 'locate', 'looks'], 'joint': '', 'type': 'move'}, {'file': 'earth', 'acts': {}, 'syns': ['earth'], 'jjrb': [], 'move': ['move', 'locate', 'l'], 'joint': '', 'rname': 'Mypicture'}, {'file': 'line', 'acts': {}, 'syns': ['line'], 'jjrb': [], 'move': ['draw'], 'joint': ''}, {'file': 'lady', 'acts': {'run': {'fstart': 1, 'flast': -1}}, 'syns': ['lady'], 'jjrb': [], 'move': ['move', 'moving', 'moved', 'locate', 'located', 'locating', 'vanish', 'vanished', 'vanishing'], 'joint': {'legs': {'include': ['LHipJoint', 'RHipJoint'], 'exclude': []}, 'hand': {'include': ['LeftShoulder', 'RightShoulder'], 'exclude': []}, 'head': {'include': ['Neck'], 'exclude': ['LHipJoint', 'RHipJoint']}}, 'rname': 'Ruchika'}, {'file': 'SUVfront', 'acts': {}, 'syns': ['SUV'], 'jjrb': ['front', 'front facing'], 'move': ['move', 'locate', 'l'], 'joint': ''}, {'file': 'SUVfront', 'acts': {}, 'syns': ['SUV'], 'jjrb': ['front', 'front facing'], 'move': ['move', 'locate', 'l'], 'joint': ''}]}
    mydata=json.dumps({'story': story, 'universe': cuniverse, 'user': {'user': appsetup['user_idnt'], 'pass': appsetup['secrettxt']}})
    response = requests.post(animurl, headers=headers, data=mydata)
    if response.status_code not in [200, 201]: return -1
    animation = json.loads(response.text)
    return animation

def framerunparams (entparams = [], appsetup = {}):
    retval = {'fromfr': 1, 'tillfr': -1, 'fps': 1, 'width': 500, 'height': 500}
    retval['fromfr'] = 1 if forceint(entparams[0]) == -1 else forceint(entparams[0])
    retval['tillfr'] = 9999 if forceint(entparams[1]) == -1 else forceint(entparams[1])
    retval['fps'] = appsetup['project']['fps'] if forceint(entparams[2]) == -1 else forceint(entparams[2])
    retval['scrwide'], retval['scrhigh'] = getscreensize (appsetup['project']['winsize'], 500, 500)
    maxscr = max(retval['scrwide'], retval['scrhigh'])
    if maxscr <= 500: return retval
    retval['scrwide'], retval['scrhigh'] = int(retval['scrwide']*500/maxscr), int(retval['scrhigh']*500/maxscr)
    return retval

def exec_pic_export (entparams = [], appsetup = {}, rushes = "rushes", secon = 0):
    print (f"exec_pic_export:\n\tentparams={entparams}\n\trushes={rushes}")
    if entparams[0] == '': return 1
    filenm = Path(appsetup['project']['name']) / 'video' / entparams[0]
    if filenm.suffix == '': filenm = Path(appsetup['project']['name']) / 'video' / (entparams[0] + '.gif')
    fps = appsetup['project']['fps'] if forceint(entparams[1]) == -1 else forceint(entparams[1])
    rushes = Path(appsetup['project']['name']) / rushes if secon == 0 else rushes
    frange = entparams[2].split(",")
    fstart = int(frange[0].strip())
    flast = -1 if len(frange) == 1 else int(frange[1].strip())
    cmdstr = "ffmpeg -framerate " + str(fps) + " -start_number " + str(fstart) + " "
    if flast != -1:
        vlen = (flast+1 - fstart)/fps
        cmdstr = cmdstr + " -t " + str(vlen) + " "
    cmdstr = cmdstr + " -i " + str(rushes) + "/frame__%06d.png "
    print ("filenm", filenm, filenm.suffix, filenm.stem)
    if filenm.suffix in ['.mp4', '.mov']: cmdstr = cmdstr + " -pix_fmt yuv420p "
    cmdstr = cmdstr + str(filenm) + " -y"
    print ("cmdstr", cmdstr)
    os.system(cmdstr)
    return 1

def exec_pic_delete (entparams = [], appsetup = {}):
    rushes = Path(appsetup['project']['name']) / "rushes"
    for files in rushes.glob('*.png'):
        files.unlink()
    tempr = Path(appsetup['project']['name']) / "rushes" / "temp"
    for files in tempr.glob('*.png'):
        files.unlink()
    return 1

def fixinitemlist (lfrom = 1, linto = 1):
    retval = [0]
    for ix in range(1, linto):
        fix = round(ix*(lfrom/(linto-1)), 0)
        retval.append(int(fix))
    print ("fixinitemlist", retval)
    return retval

def logit (logtext, inputlog):
    logtext.insert('end', pprint.pformat(inputlog))