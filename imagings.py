from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont
# import mrcnn
# import mrcnn.config
# import mrcnn.model
# import mrcnn.visualize
import cv2
import os
import matplotlib.font_manager
import numpy
import random
import math

import json
import pyback
import copy
import shutil
import time
import ast

yes_synos = ['y', 'yea', 'yeah', 'yo', 'yes', 'aye', 'aaye', 'ya', 'yup', 'yaap']
nah_synos = ['n', 'no', 'nop', 'nope', 'nay', 'ei', 'not']
def_imgsize = (2000, 2000)

def confirm_file (filestr, ftype = 'video', fback = '', appsetup = {}, isnew = 0):
    print (f"confirm_file:\n\tfilestr={filestr}\n\tftype={ftype}\n\tfback={fback}\n\tisnew={isnew}")
    if isnew == 1 and filestr == '' and fback != '':
        if (ftype != 'folder' and fback.suffix != '') or (ftype == 'folder'):
            nfile = Path(appsetup['project']['name']) / 'temp' / 'tempcreation_'+time.time()+fback.suffix
            return nfile, []
    elif isnew == 0 and filestr != '':
        nfile = Path(appsetup['project']['name']) / filestr
        if (ftype != 'folder' and nfile.is_file()) or (ftype == 'folder' and nfile.is_dir()): return nfile, []
    elif isnew == 1 and filestr != '':
        nfile = Path(appsetup['project']['name']) / filestr
        if nfile.suffix == '' and ftype == 'model': nfile = Path(appsetup['project']['name']) / (filestr+'.egg')
        if nfile.suffix == '' and ftype == 'image': nfile = Path(appsetup['project']['name']) / (filestr+'.png')
        if nfile.suffix == '' and ftype == 'video': nfile = Path(appsetup['project']['name']) / (filestr+'.mp4')
        if nfile.parent == appsetup['project']['name']:
            if ftype in ['video', 'image']: nfile = Path(appsetup['project']['name']) / 'video' / filestr
            if ftype == 'model': nfile = Path(appsetup['project']['name']) / 'model' / filestr
            if nfile.is_file():
                fnfile = Path(nfile.parent) / nfile.stem+time.time()+nfile.suffix
                return fnfile, ['WARNING', "The file mentioned already exists, new file name have been changed"]
        else: return nfile, []
    return '', []

def parse_additionals (strtext = ''):
    if strtext == '': return {}
    try: return ast.literal_eval('{' + strtext + '}')
    except: return {}

def check_system_fonts (fontlike = '', fontsize = 16):
    '''Returns the font file for the given name - best match for the name'''
    if fontlike == '':
        ffont = ImageFont.load_default()
        return ffont
    inputt = fontlike.lower().split(' ')
    flist = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    maxmatch = 0
    exptdfname = ''
    for fname in flist:
        fontname = matplotlib.font_manager.FontProperties(fname=fname).get_name()
        fontpath = Path(fname)
        if fontname == fontlike or fontpath.stem.lower() == fontlike:
            exptdfname = fname
            break
        names = fontname.lower().split(' ') + [fontpath.stem.lower()]
        match = len(list(set(names) & set(inputt)))
        if match > maxmatch:
            exptdfname = fname
            maxmatch = match
    if exptdfname == '': ffont = ImageFont.load_default()
    else: ffont = ImageFont.truetype(exptdfname, fontsize)
    return ffont

def ui_addaudiotovideo (entparams = [], appsetup = {}):
    print (f"ui_addaudiotovideo:\n\tentparams={entparams}\n\tappsetup={appsetup}")
    vidfile, _X = confirm_file (entparams[0], ftype = 'video', appsetup = appsetup, isnew = 0)
    audfile, _X = confirm_file (entparams[1], ftype = 'audio', isnew = 0)
    vistart = pyback.forceint(entparams[2], 0)
    austart = pyback.forceint(entparams[3], 0)
    alength = pyback.forceint(entparams[4], -1)
    outfile, _X = confirm_file (entparams[5], ftype = 'video', fback = 'tempcreation_'+str(time.time())+vidfile.suffix, isnew = 1)
    if vidfile == '' or audfile == '' or outfile == '': return ['ERROR', 'The command could not be executed as files are not found']
    if austart != 0:
        newaudfile = Path(audfile.parent) / (vidfile.stem+"__"+str(austart)+vidfile.suffix)
        cmdstr = f"ffmpeg -i {audfile} -ss {austart} -to {austart+alength} -c copy -y {newaudfile}"
        audfile = newaudfile
    cmdstr = f"ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 {vidfile}"
    audcod = (subprocess.run(cmdstr, capture_output=True)).stdout.decode('unicode_escape')
    if audcod == '':
        cmdstr = f"ffmpeg -i {vidfile} -itsoffset {vistart} -t {vistart+alength} -i {audfile} -map 0:v:0 -map 1:a:0 -async 1 -y {outfile}"
    else:
        cmdstr = f"ffmpeg -i {vidfile} -itsoffset {vistart} -t {vistart+alength} -i {audfile}  -filter_complex amix -map 0:v -map 0:a -map 1:a -async 1 -y {outfile}"
    try: os.system(cmdstr)
    except: return ['ERROR', 'The command could not be executed!']
    if outfile.parent == 'temp':
        vidfile.rename(Path(vidfile.parent) / (vidfile.stem+int(time.time())+vidfile.suffix))
        outfile.rename(vidfile)
    return []

def ui_text_image_creation (entparams = [], appsetup = {}):
    print (f"ui_text_image_creation:\n\tentparams={entparams}\n\tappsetup={appsetup}")
    is_single = 1
    if entparams[4].lower() in yes_synos:
        imgfile, _Xtra = confirm_file (entparams[0], ftype = 'folder', appsetup = appsetup, isnew = 1)
        imgfile.mkdir()
        is_single = 0
    else: imgfile, _Xtra = confirm_file (entparams[0], ftype = 'image', appsetup = appsetup, isnew = 1)
    textstr = entparams[1]
    ffont = check_system_fonts (fontlike = entparams[2], fontsize = pyback.forceint (entparams[3], 16))
    if imgfile == '' or textstr == '': return ['ERROR', 'Image file or text string is invalid']
    paramadd = parse_additionals (strtext = entparams[5])
    imgsize = def_imgsize
    print ("ffont", ffont)
    if is_single == 1:
        create_image_fortext (file = imgfile, imgsize=imgsize, text = textstr, font = ffont, paramadd = paramadd)
    else:
        maxsize = create_image_fortext (file = None, imgsize=imgsize, text = textstr, font = ffont, paramadd = paramadd)
        for ix in range(len(textstr)+1):
            thistext = textstr[:ix]
            framefile = imgfile / ("frame__"+"%06d"%(ix)+".png")
            create_image_fortext (file = framefile, imgsize=maxsize, text = thistext, font = ffont, paramadd = paramadd, nocrop = 1)
    return _Xtra

def create_image_fortext (file = (), imgsize=def_imgsize, text = '', font = None, paramadd = None, nocrop = 0):
    cmdkeys = {'fill': (1, 1, 1, 255), 'anchor': None, 'spacing': 4, 'direction': None, 'features': None,
        'language': None, 'stroke_width': 0, 'stroke_fill': None, 'embedded_color': False}
    image = Image.new('RGBA', imgsize, color = (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    for param in cmdkeys.keys():
        if param in paramadd: cmdkeys[param] = paramadd[param]
    draw.text((0,0), text, font=font, fill=cmdkeys['fill'], anchor=cmdkeys['anchor'], spacing=cmdkeys['spacing'],
        direction=cmdkeys['direction'], features=cmdkeys['features'], language=cmdkeys['language'], stroke_width=cmdkeys['stroke_width'],
        stroke_fill=cmdkeys['stroke_fill'], embedded_color=cmdkeys['embedded_color'])
    imageBox = image.getbbox()
    if nocrop == 1: cropped=image
    else: cropped = image.crop(imageBox)
    if file == None: return (2*cropped.size[0], 2*cropped.size[1])
    cropped.save(file)
    return 1

def ui_p3dmodel_creation (entparams = [], appsetup = {}):
    imgfile, _Xtra = confirm_file (entparams[0], ftype = 'image', appsetup = appsetup, isnew = 0)
    modfile = None
    fps = -1
    if imgfile == '':
        imgfile, _Xtra = confirm_file (entparams[0], ftype = 'folder', appsetup = appsetup, isnew = 0)
        if not imgfile.exists(): return ['ERROR', 'No available information on mentioned file']
        csframe = pyback.forceint(entparams[1].split(",")[0], 1)
        clframe = pyback.forceint(entparams[1].split(",")[0], 999999)
        fps = pyback.forceint(entparams[2], -1)
        if str(Path(imgfile.parent)) != str(Path(appsetup['project']['name']) / 'model'):
            imgdst = Path(appsetup['project']['name']) / 'media' / imgfile.name
            pyback.png_overwrites (csframe = csframe, tdframe = 0, clframe = clframe, imgsrc = imgfile, imgdst = imgdst, owrite = 1, action = ['copy'])
            imgfile = imgdst
    pyback.create_media_p3dmodel (ifile = imgfile, owrite = 1, appsetup = appsetup, fps = fps)
    return _Xtra
    
def ui_prepare_stage (entparams = [], appsetup = {}):
    inputlst = entparams[0]
    output = entparams[1]
    for idir in inputlist:
        ipath = Path(appsetup['project']['name']) / 'video' / idir
        if not ipath.is_dir(): continue
        pyback.pngoverwrites (fframe = 1, lframe = 9999, imgsource = sourcep, imgdest = destmed, overwrite = 1, action='copy')

def ui_mrcnn_objects (params):
    ifile = params[0]
    ofiles = params[1]
    if params[0] == '' or params[1] == '': return 1
    mrcnn_image_retrieval (ifile = ifile, ofiles = ofiles, color = '', params = '', appsetup = '')
    return 1

def int_proc_filenames (entparams = [], appsetup = {}, defextn = '.png', basedir = 'media'):
    ifile = entparams[0]
    ofile = entparams[1]
    bdir = Path(appsetup['project']['name']) / basedir
    ifile, ofile = bdir / ifile, bdir / ofile
    if ifile.suffix == '': ifile = bdir / (entparams[0] + defextn)
    if ofile.suffix == '': ofile = bdir / (entparams[1] + defextn)
    return {'ifile': ifile, 'ofile': ofile}

def ui_image_manipulation_basic (entparams = [], appsetup = {}):
    files = int_proc_filenames (entparams = entparams, appsetup = appsetup)
    ifile, ofile = files['ifile'], files['ofile']
    if entparams[2] != '': image_resize (ifile = ifile, ofile = ofile, nsize = entparams[2])
    return 1

def ui_image_manipulation (function = '', entparams = [], appsetup = {}):
    print ("function, entparams, appsetup", function, entparams, appsetup)
    return 1
    replace = 0
    if entparams[1] == '':
        entparams[1] = 'REPLACE_'+entparams[0]
        replace = 1
    files = int_proc_filenames (entparams = entparams, appsetup = appsetup, basedir = 'video')
    ifile, ofile = files['ifile'], files['ofile']
    color = 'black' if entparams[2] == '' else entparams[2]
    color = 'IBRT' if color not in appsetup['colorcode'] else entparams[2]
    if function not in ('settransparent'): return 1
    function = 'setcolortransparent'
    if color in ['IBRT']: function = 'ibrt__OPHoperHPO'
    function = "f_" + function
    globals()[function] (ifile, ofile, color = entparams[2], params = entparams[3], appsetup = appsetup)
    if replace == 1:
        ifile.rename(Path(ifile.parent) / (ifile.stem+'_REPLACED'+ifile.suffix))
        ofile.rename(ifile)
    return 1

def ui_find_image_contours (entparams = [], appsetup = {}):
    files = int_proc_filenames (entparams = entparams, appsetup = appsetup)
    ifile, ofile = files['ifile'], files['ofile']
    campos = entparams[2]
    bcenter = entparams[3]
    print ("ifile, ofile, campos, bcenter", ifile, ofile, campos, bcenter)
    pwide, phigh = Image.open(ifile).size
    proc = find_image_contours (ifile = str(ifile), ofile = str(ofile))
    contours = proc['data']['contours']
    logictxt, thisf, lastf, groups = '', 1, 1, [0]
    canwide, canhigh = pyback.getscreensize (appsetup['project']['canvas'], 500, 500)
    diffw, diffh = int((canwide-pwide)/2), int((canhigh-phigh)/2)
    pxdata = []
    for ix, contour in enumerate(contours):
        for jx, item in enumerate(contour):
            if jx-1 > len(contour)/2: break
            pxdata.append([item[0][0]+diffw, item[0][1]+diffh])
        groups.append(len(pxdata))
    pyback.exec_save_coords (entparams = [campos, bcenter, ofile.stem], appsetup = appsetup, coord = str(pxdata), addxtra = {'group': groups})
    pyback.set_multifile_coords (file = ofile.stem, appsetup = appsetup, addlogic = 1)
    return 1

def ui_basic_movie_creation (entparams = [], appsetup = {}):
    if entparams[2] == '': return 0
    cmodel = 0 if entparams[2].lower() in ('no', 'n', 'nope') == '' else 1
    sframe = pyback.forceint(entparams[0], default = 1)
    lframe = pyback.forceint(entparams[1], default = 1)
    sourcep = Path(appsetup['project']['name']) / 'rushes'
    destinp = Path(appsetup['project']['name']) / 'video' / entparams[2]
    destmed = Path(appsetup['project']['name']) / 'media' / entparams[2]
    pyback.pngoverwrites (fframe = 2-sframe, lframe = lframe, imgsource = sourcep, imgdest = destinp, overwrite = 1, action='copy')
    if cmodel == 1:
        pyback.pngoverwrites (fframe = 2-sframe, lframe = lframe, imgsource = sourcep, imgdest = destmed, overwrite = 1, action='copy')
    pyback.exec_pic_export (entparams = [entparams[2], appsetup['project']['fps'], "1, -1"], appsetup = appsetup, rushes = '/video/'+entparams[2]+'/')
    if cmodel == 0: return 1
    os.chdir(Path(appsetup['project']['name']) / 'model')
    cmdstr = "egg-texture-cards -o \"" + destmed.stem + ".egg\" -fps "+str(appsetup['project']['fps'])+" \"../media/" + outname + "/*.png\""
    os.system(cmdstr)
    os.chdir('../..')

def ui_transparent_movie_creation (entparams = [], appsetup = {}):
    print ("entparams, appsetup", entparams, appsetup)
    framep = Path(appsetup['project']['name']) / 'video/'
    framer = Path(appsetup['project']['name']) / 'rushes/'
    bframe = pyback.forceint(entparams[0], default = 2)
    sframe = pyback.forceint(entparams[1], default = 3)
    lframe = pyback.forceint(entparams[2], default = 9999)
    if entparams[3] == '': return 1
    _fn = Path(entparams[3])
    outname = _fn.name if _fn.suffix == '.gif' else _fn.stem
    outpath = framep / outname
    finpath = framep / (outname+"_final")
    shutil.rmtree(outpath)
    shutil.rmtree(finpath)
    os.mkdir(str(outpath))
    os.mkdir(str(finpath))
    basefile = outpath / ("baseframe__"+outname+".png")
    fcount = pyback.pngoverwrites (fframe = 2-sframe, lframe = lframe, imgsource = framer, imgdest = outpath, action = 'copy')
    shutil.copyfile(framer / ("rush__"+"%04d"%(int(bframe))+".png"), basefile)
    image_manual_bgremoval (ipath = outpath, opath = finpath, basefile = basefile, trans = [0,0,0], keeps = [255,255,255], alpha = 255)
    newfps = lcount
    pyback.exec_pic_export (entparams = [outname, -1, '1, -1'], appsetup = appsetup, rushes = "video/"+outname+"_final")
    shutil.copytree(finpath, Path(appsetup['project']['name']) / 'media' / outname)
    os.chdir(Path(appsetup['project']['name']) / 'model')
    cmdstr = "egg-texture-cards -o " + finpath.stem + ".egg -fps "+str(appsetup['project']['fps'])+" ../media/" + outname + "/*.png"
    os.system(cmdstr)
    os.chdir('../..')

def ui_remove_background_movie (entparams = [], appsetup = {}):
    print ("entparams, appsetup", entparams, appsetup)
    framep = Path(appsetup['project']['name']) / 'video/'
    framer = Path(appsetup['project']['name']) / 'rushes/'
    sframe = pyback.forceint(entparams[0], default = 3)
    lframe = pyback.forceint(entparams[1], default = 9999)
    if entparams[2] == '': return 1
    if entparams[3].lower() not in ['red','green','blue','white','black','yellow']: return 1
    _fn = Path(entparams[2])
    outname = _fn.name if _fn.suffix == '.gif' else _fn.stem
    outpath = framep / outname
    finpath = framep / (outname+"_final")
    try:
        shutil.rmtree(outpath)
        shutil.rmtree(finpath)
        os.mkdir(str(outpath))
        os.mkdir(str(finpath))
    except: print ("Maybe some issue in files")
    basefile = outpath / ("baseframe__"+outname+".png")
    fcount = pyback.pngoverwrites (fframe = 2-int(sframe), lframe = lframe, imgsource = framer, imgdest = outpath, action = 'copy')
    for ifile in outpath.iterdir():
        image_bgscreen_removal (ifile = ifile, ofile = finpath / (ifile.stem+'.png'), color = entparams[3].lower())
    pyback.exec_pic_export (entparams = [outname, -1, '1, -1'], appsetup = appsetup, rushes = "video/"+outname+"_final")
    shutil.copytree(finpath, Path(appsetup['project']['name']) / 'media' / outname)
    os.chdir(Path(appsetup['project']['name']) / 'model')
    cmdstr = "egg-texture-cards -o " + outname + ".egg -fps "+str(appsetup['project']['fps'])+" ../media/" + outname + "/*.png"
    os.system(cmdstr)
    os.chdir('../..')

def image_bgscreen_removal (ifile = Path(), ofile = Path(), color = 'green'):
    limits = {'blue': {'lower': [0, 0, 100], 'upper': [120, 120, 255]},
              'green': {'lower': [0, 100, 0], 'upper': [120, 255, 120]},
              'red': {'lower': [100, 0, 0], 'upper': [255, 120, 120]},
              'yellow': {'lower': [100, 0, 0], 'upper': [255, 120, 120]}
    }
    image = cv2.imread(str(ifile))
    image_copy = numpy.copy(image)
    image_copy = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)
    mask = cv2.inRange(image_copy, numpy.array(limits[color]['lower']), numpy.array(limits[color]['upper']))
    cv2.imwrite('temp/image_bgscreen_removal_mask.png',mask)
    ximg = Image.open(str(ifile))
    ximg = ximg.convert("RGBA")
    xstate = ximg.getdata()
    mimg = Image.open('temp/image_bgscreen_removal_mask.png')
    mimg = mimg.convert("RGBA")
    mstate = mimg.getdata()
    pcount = ximg.size[0] * ximg.size[1]
    newData = []
    for ix in range(0, pcount):
        mitem, xitem = mstate[ix], xstate[ix]
        if mitem[0] == 0 and mitem[1] == 0 and mitem[2] == 0:
            toappend = (xitem[0], xitem[1], xitem[2], 255)
        else: toappend = (xitem[0], xitem[1], xitem[2], 0)
        newData.append(toappend)
    ximg.putdata(newData)
    ximg.save(str(ofile), "PNG")

def image_manual_bgremoval (ipath = Path(), opath = Path(), basefile = Path(), trans = [0,0,0], keeps = [255,255,255], alpha = 255):
    bimg = Image.open(basefile)
    bimg = bimg.convert("RGBA")
    bstate = bimg.getdata()
    for file in ipath.iterdir():
        if file.name == basefile.name: continue
        pixwise_removal (ifile = file, ofile = opath / file.name, bstate = bstate, trans = trans, keeps = keeps, alpha = alpha)

def pixwise_removal (ifile = Path(), ofile = Path(), bstate = [], trans = [0,0,0], keeps = [255,255,255], alpha = 255):
    ximg = Image.open(str(ifile))
    ximg = ximg.convert("RGBA")
    xstate = ximg.getdata()
    pcount = ximg.size[0] * ximg.size[1]
    newData = []
    for ix in range(0, pcount):
        bitem, xitem = bstate[ix], xstate[ix]
        if (xitem[0] == trans[0] and xitem[1] == trans[1] and xitem[2] == trans[1]):
            if (bitem[0] == keeps[0] and bitem[1] == keeps[1] and bitem[2] == keeps[2]):
                toappend = (bitem[0], bitem[1], bitem[2], 0)
            else:
                toappend = (bitem[0], bitem[1], bitem[2], alpha)
        else:
            toappend = (xitem[0], xitem[1], xitem[2], 0)
        newData.append(toappend)
    ximg.putdata(newData)
    ximg.save(str(ofile), "PNG")
    return 1

def f_ibrt__OPHoperHPO (ifile = '', ofiles = '', color = '', params = '', appsetup = ''):
    os.chdir("ibrt")
    cmdstr = 'ppython main.py -i "../' + str(ifile) + '" -o "../' + str(ofile) + '" -m u2net'
    rval = os.system(cmdstr)
    os.chdir("..")
    return rval

def mrcnn_image_retrieval (ifile = '', ofiles = '', color = '', params = '', appsetup = ''):
    CLASS_NAMES = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']
    class SimpleConfig(mrcnn.config.Config):
        NAME = "coco_inference"
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
        PRE_NMS_LIMIT = 6000
        NUM_CLASSES = len(CLASS_NAMES)
    filename = ifile
    nfilename = "C:/ProgramData/Memeer/portfolio/media/child22.png"
    model = mrcnn.model.MaskRCNN(mode="inference", config=SimpleConfig(), model_dir=os.getcwd())
    model.load_weights(filepath="C:/ProgramData/Memeer/Trained/Mask_RCNN/mask_rcnn_coco.h5", by_name=True)
    image = cv2.imread(filename)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    r = model.detect([image], verbose=0)
    r = r[0]
    mask = r['masks']
    mask = mask.astype(int)
    mask.shape
    for i in range(mask.shape[2]):
        temp = cv2.imread(filename)
        for j in range(temp.shape[2]):
            temp[:,:,j] = temp[:,:,j] * mask[:,:,i]
        cv2.imwrite((str(i)+"__"+ofiles), temp)

def f_setcolortransparent (ifile, ofile, color = 'black', params = '', appsetup = {}):
    print ("f_setcolortransparent: ifile, ofile, color, params", ifile, ofile, color, params)
    dirname = 'video/'+ifile.stem+'/'
    if ifile.suffix in appsetup['movies'] and not os.path.isdir(str(ifile.parent)+'/'+str(ifile.stem)):
        cmdstr = "ffmpeg -i ../media/" + file.name + " -vf scale=320:-1 -vsync 0 ../media/" + file.stem + "/series%4d.png"
        os.system(cmdstr)
    opath = ofile.parent / ofile.stem
    ipath = ifile.parent / ifile.stem
    for file in ipath.iterdir():
        if file.suffix not in appsetup['pictures']: continue
        set_transparency (ctype = color.lower(), ifile = file, ofile = opath / (file.stem+'.png'))
    cmdstr = "ffmpeg -framerate 48  -start_number 1 -t 5.2 -i /demo/video/test22/rush__%04d.png -y"

def set_transparency (ctype = 'black', ifile = '', ofile = ''):
    img = Image.open(ifile)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for ix, item in enumerate(datas):
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            newData.append((item[0],item[1],item[2], 0))
            print (ix)
        else:
            newData.append(item)
    img.putdata(newData)
    img.save(ofile, "PNG")

def modify_images (ifile = '', ofile = '', param = [], nval = 1.0):
    image = Image.open(ifile)
    if param == 'contrast':
        contrast = ImageEnhance.Contrast(image)
        contrast.enhance(nval).save(ofile)
    if param == 'color':
        color = ImageEnhance.Color(image)
        color.enhance(nval).save(ofile)
    if param == 'brightness':
        brightness = ImageEnhance.Brightness(image)
        brightness.enhance(nval).save(ofile)
    if param == 'contrast':
        sharpness = ImageEnhance.Sharpness(image)
        sharpness.enhance(nval).save(ofile)
    if param == 'greyscale':
        greyscale = image.convert('L')
        greyscale.save(ofile)
    if param == 'invert':
        rgbimg = image.convert('RGB')
        rgbimginv = ImageOps.invert(rgbimg)
        rgbimginv.save(ofile)
    return 1

def image_resize (ifile = '', ofile = '', nsize = 100):
    image = Image.open(ifile)
    cwide, chigh = image.size
    if pyback.forceint(nsize, default = -1) != -1:
        nwide, nhigh = int(cwide*int(nsize)/100), int(chigh*int(nsize)/100)
    else:
        nwide, nhigh = pyback.getscreensize (nsize, cwide, chigh)
    nimage = image.resize((nwide, nhigh), Image.ANTIALIAS)
    nimage.save(ofile)
    return 0
    
def find_image_contours (ifile = '', ofile = '', thresh = 100):
    random.seed(12345)
    if thresh > 255: thresh = 255
    def thresh_callback(val):
        threshold = val
        canny_output = cv2.Canny(src_gray, threshold, threshold * 2)
        contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        drawing = numpy.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=numpy.uint8)
        for ix in range(len(contours)):
            color = (random.randint(0,256), random.randint(0,256), random.randint(0,256))
            cv2.drawContours(drawing, contours, ix, color, 2, cv2.LINE_8, hierarchy, 0)
        cv2.imwrite(ofile, drawing)
        return contours
    src = cv2.imread(ifile)
    src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    src_gray = cv2.blur(src_gray, (3,3))
    max_thresh = 255
    contours = thresh_callback(thresh)
    return {'code': 'OK', 'estack': [], 'data': {'contours': contours, 'ofile': ofile}}

def create_image_cartoon (ifile = '', ofile = '', num_down = 2, num_bilateral = 7):
    img_rgb = cv2.imread(ifile)
    img_color = img_rgb
    for _ in range(num_down):
        img_color = cv2.pyrDown(img_color)
    for _ in range(num_bilateral):
        img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=9, sigmaSpace=7)
    for _ in range(num_down):
        img_color = cv2.pyrUp(img_color)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)
    img_edge = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=9, C=2)
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
    img_cartoon = cv2.bitwise_and(img_color, img_edge)
    cv2.imwrite(ofile, img_cartoon)
    return 0

def image_cloning (imfile = '', objfile = '', ofile = '', typ = 'MIXED_CLONE', loc = [0, 0, 'abs']):
    im = cv2.imread(imfile)
    obj= cv2.imread(objfile)
    mask = 255 * numpy.ones(obj.shape, obj.dtype)
    width, height, channels = im.shape
    if loc[2] == 'abs':    center = (loc[0], loc[1])
    elif loc[2] == 'rel': center = (int(height*loc[0]), int(width*loc[1]))
    else: center = (0, 0)
    if 'typ' == 'NORMAL':
        clone = cv2.seamlessClone(obj, im, mask, center, cv2.NORMAL_CLONE)
        cv2.imwrite(objfile, clone)
    elif 'typ' == 'MIXED':
        clone = cv2.seamlessClone(obj, im, mask, center, cv2.MIXED_CLONE)
        cv2.imwrite(objfile, clone)
    else:
        clone = cv2.seamlessClone(obj, im, mask, center, cv2.NORMAL_CLONE)
        cv2.imwrite("NORMAL"+objfile, clone)
        clone[1] = cv2.seamlessClone(obj, im, mask, center, cv2.MIXED_CLONE)
        cv2.imwrite("MIXED"+objfile, clone)
    return 1

def create_image_pencil_sketch (ifile = '', ofile = '', gindex = 21, sigmaX = 0, sigmaY = 0):
    img = cv2.imread(ifile, 1)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_invert = cv2.bitwise_not(img_gray)
    img_smoothing = cv2.GaussianBlur(img_invert, (gindex, gindex), sigmaX=0, sigmaY=0)
    def dodgeV2(x, y):
        return cv2.divide(x, 255 - y, scale=256)
    nimage = dodgeV2(img_gray, img_smoothing)
    cv2.imwrite(ofile, nimage)
    return 1
