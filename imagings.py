from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont
import cv2
import os
import matplotlib.font_manager
import numpy
import random
import math
from tkinter import messagebox
import ast

import json
import pyback
import copy
import shutil
import time
import subprocess

yes_synos = ['y', 'yea', 'yeah', 'yo', 'yes', 'aye', 'aaye', 'ya', 'yup', 'yaa', 'jaa']
nah_synos = ['n', 'no', 'nop', 'nope', 'nay', 'ei', 'not']
def_imgsize = (2000, 2000)
colorcode = {
    'white': [255,255,255],
    'black': [0,0,0],
    'red': [255, 0, 0],
    'green': [0,255,0],
    'blue': [0,0,255],
    'panda3d': [105,105,105],
    'all white': [[170,0,200], [190,20,255]],
    'all black': [[0,0,0], [10,200,10]],
    'all red': [[0,50,100], [15,255,255]],
    'all green': [[45,50,100], [75,255,255]],
    'all blue': [[105,50,100], [135,255,255]],
    'all panda3d': [[0,0,35], [0,0,50]]
}

def base_function (funcname, entparams = {}, appsetup = {}):
    retval = globals()[funcname] (entparams = entparams, appsetup = appsetup)
    return retval

def localmessage (mtype = 'info', title = '', message = ''):
    UREP = 'cancel'
    if mtype == 'info': messagebox.showinfo (title=title, message=message)
    if mtype == 'warn': messagebox.showwarning (title=title, message=message)
    if mtype == 'error': messagebox.showerror (title=title, message=message)
    if mtype == 'ask': UREP = messagebox.askokcancel (title=title, message=message)
    return UREP

def confirm_file (filestr, ftype = 'input', fback = '', appsetup = {}, isnew = 0):
    print ("filestr, ftype, fback, isnew", filestr, ftype, fback, isnew)
    projdir = Path(appsetup['project']['name'])
    filestr = filestr.replace('\\', '/').strip()
    fnames = filestr.split('/')
    toorel = 1 if fnames[0] not in ['model', 'media', 'audio', 'video', 'temp'] else 0
    if isnew == 0:
        if filestr == '': return ''
        if ftype == 'model': return projdir / 'model' / fnames[-1:]
        else: return projdir / filestr
    else:
        if filestr == '' and fback != '':
            return projdir / 'temp' / (str(time.time())+fback)
        elif filestr == '' and fback == '': return ''
        else:
            nfile = projdir / filestr
            if ftype == 'model':
                if nfile.suffix != '.egg': return projdir / 'model' / (fnames[-1]+'.egg')
                else: return projdir / 'model' / (fnames[-1:])
            else:
                if fnames[0] == 'model': return ''
                elif len(fnames) > 1 and toorel == 0:
                    retfile = projdir / filestr
                    if ftype == 'image' and retfile.suffix not in appsetup['images']: retfile = projdir / (filestr+'.png')
                    if ftype == 'movie' and retfile.suffix not in appsetup['movies']: retfile = projdir / (filestr+'.mp4')
                    return retfile
                elif len(fnames) == 1:
                    if fback.startswith ('temp/'):  return projdir / fback
                    else: return projdir / fback / filestr
    return ''

def parse_additionals (strtext = ''):
    if strtext == '': return {}
    try: return ast.literal_eval('{' + strtext + '}')
    except: return {}

def check_system_fonts (fontlike = '', fontsize = 16):
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
    vidfile = confirm_file (entparams[0], ftype = 'video', appsetup = appsetup, isnew = 0)
    audfile = confirm_file (entparams[1], ftype = 'audio', appsetup = appsetup, isnew = 0)
    vistart = pyback.forceint(entparams[2], 0)
    austart = pyback.forceint(entparams[3], 0)
    alength = pyback.forceint(entparams[4], 0)
    outfile = confirm_file (entparams[5], ftype = 'video', fback = vidfile.name, isnew = 1, appsetup = appsetup)
    if isinstance(vidfile, str) or not vidfile.exists() or isinstance(audfile, str) or not audfile.exists():
        localmessage (mtype = 'error', title = 'Input files are missing', message = f"Input Audio ({audfile}) or Video ({vidfile}) is missing, kindly check path")
        return -1
    if austart != 0:
        newaudfile = Path(audfile.parent) / (vidfile.stem+"__"+str(austart)+audfile.suffix)
        cmdstr = f"ffmpeg -i \"{audfile}\" -ss {austart} -to {austart+alength} -c copy -y \"{newaudfile}\" -loglevel error"
        print (f"executing command: {cmdstr}")
        try: os.system(cmdstr)
        except: return ['ERROR', 'The command could not be executed!']
        audfile = newaudfile
    cmdstr = f"ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 \"{vidfile}\" -loglevel error"
    print (f"executing command: {cmdstr}")
    audcod = (subprocess.run(cmdstr, capture_output=True)).stdout.decode('unicode_escape')
    if audcod == '':
        cmdstr = f"ffmpeg -i \"{vidfile}\" -itsoffset {vistart} -t {vistart+alength} -i \"{audfile}\" -map 0:v:0 -map 1:a:0 -async 1 -y \"{outfile}\" -loglevel error"
    else:
        cmdstr = f"ffmpeg -i \"{vidfile}\" -itsoffset {vistart} -t {vistart+alength} -i \"{audfile}\"  -filter_complex amix -map 0:v -map 0:a -map 1:a -async 1 -y \"{outfile}\" -loglevel error"
    print (f"executing command: {cmdstr}")
    try: os.system(cmdstr)
    except: return ['ERROR', 'The command could not be executed!']
    if outfile.parent == 'temp':
        vidfile.rename(Path(vidfile.parent) / (vidfile.stem+int(time.time())+vidfile.suffix))
        outfile.rename(vidfile)
    return []

def ui_prepare_watermark (entparams = [], appsetup = {}):
    print (f"ui_addaudiotovideo:\n\tentparams={entparams}\n\tappsetup={appsetup}")
    imgfile = confirm_file (entparams[0], ftype = 'image', appsetup = appsetup, isnew = 0)
    vidfile = confirm_file (entparams[1], ftype = 'video', appsetup = appsetup, isnew = 0)
    outfile = confirm_file (entparams[3], ftype = 'video', fback = 'temp/'+str(time.time())+vidfile.name, isnew = 1, appsetup = appsetup)
    pixels = entparams[2].split(',')
    wpixel = pyback.forceint(pixels[0], 100)
    hpixel = 100 if len(pixels) < 2 else pyback.forceint(pixels[1], 100)
    cmdstr = f"ffmpeg -i {vidfile} -i {imgfile} -filter_complex \"overlay={wpixel}:{hpixel}\" {outfile} -loglevel error"
    print (f"cmdstr: {cmdstr}")
    try: os.system(cmdstr)
    except: return ['ERROR', 'The command could not be executed!']

def ui_text_image_creation (entparams = [], appsetup = {}):
    print (f"ui_text_image_creation:\n\tentparams={entparams}\n\tappsetup={appsetup}")
    is_single = 1
    if entparams[4].lower() in yes_synos:
        imgfile = confirm_file (entparams[0], ftype = 'folder', appsetup = appsetup, isnew = 1)
        imgfile.mkdir()
        is_single = 0
    else: imgfile = confirm_file (entparams[0], ftype = 'image', appsetup = appsetup, isnew = 1)
    print (f"FINAL FILE NAME: {imgfile}")
    if imgfile.exists():
        localmessage (mtype = 'error', title = 'Such file already exist', message = f"New file ({imgfile}) exists, kindly delete it or rename this file")
        return -1
    textstr = entparams[1]
    ffont = check_system_fonts (fontlike = entparams[2], fontsize = pyback.forceint (entparams[3], 16))
    if imgfile == '' or textstr == '':
        localmessage (mtype = 'error', title = 'Missing usable parameters', message = f"New file ({imgfile}) or Text ({textstr}) could not be used")
        return -1
    paramadd = parse_additionals (strtext = entparams[5])
    print (f"paramadd: {paramadd}")
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
    if not imgfile.exists():
        messagebox (mtype = 'error', title = 'File could not be created', message = f"New file ({imgfile}) or Text ({textstr}) could not be used")
    return 1

def create_image_fortext (file = (), imgsize=def_imgsize, text = '', font = None, paramadd = None, nocrop = 0):
    cmdkeys = {'fill': (1, 1, 1, 255), 'anchor': None, 'spacing': 4, 'direction': None, 'features': None,
        'language': None, 'stroke_width': 0, 'stroke_fill': None, 'embedded_color': False}
    image = Image.new('RGBA', imgsize, color = (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    for param in cmdkeys.keys():
        print (f"updating for {param}")
        if param in paramadd: cmdkeys[param] = paramadd[param]
        print (f"updated for {param}: cmdkeys[param]: {cmdkeys[param]}")
    print (f"final cmdkeys: {cmdkeys} and paramadd was {paramadd}")
    draw.text((0,0), text, font=font, fill=cmdkeys['fill'], anchor=cmdkeys['anchor'], spacing=cmdkeys['spacing'],
        direction=cmdkeys['direction'], features=cmdkeys['features'], language=cmdkeys['language'], stroke_width=cmdkeys['stroke_width'],
        stroke_fill=cmdkeys['stroke_fill'], embedded_color=cmdkeys['embedded_color'])
    imageBox = image.getbbox()
    if nocrop == 1: cropped=image
    else: cropped = image.crop(imageBox)
    if file == None: return (2*cropped.size[0], 2*cropped.size[1])
    cropped.save(file)
    return 1

def create_output_path (param0 = None, param1 = None, appsetup = {}, outfolder = 1, getfps = 0):
    inpfile = confirm_file (param0, ftype = 'input', appsetup = appsetup, isnew = 0)
    cmf = {'fps': int(appsetup['project']['fps'])}
    if inpfile.suffix in appsetup['movies']:
        newfolder = inpfile.parent / inpfile.stem
        if newfolder.is_dir():
            UREP = localmessage (mtype = 'ask', title = 'Folder already exists', message = f"There is already a folder with name {newfolder}. Overwrite its content?")
            if UREP == 'cancel': return None, None
        existf = {'vid': newfolder, 'aud': Path(appsetup['project']['name'])/'temp'/inpfile.stem}
        cmf = pyback.create_movie_frames (ifile = inpfile, folder = existf, owrite = 1)
        inpfile = newfolder
    outfile = confirm_file (param1, ftype = 'input', appsetup = appsetup, isnew = 1, fback = str(inpfile.parent.stem))
    print ("outfile:", outfile)
    if not outfile.parent.is_dir():
        UREP = localmessage (mtype = 'error', title = 'Output Folder not valid', message = f"The folder with name {outfile} could not be created")
        print ("NOK")
        return None, None
    if outfile.exists():
        UREP = localmessage (mtype = 'ask', title = 'Path already exists', message = f"There is already a filepath with name {outfile}. Overwrite its content?")
        if UREP == 'cancel': return None, None
    if inpfile.is_dir() or outfolder == 1:
        if outfile.exists(): shutil.rmtree(outfile)
        if 'fps' not in cmf: cmf = {'fps': appsetup['project']['fps']}
        outfile.mkdir()
    if getfps == 1: return inpfile, outfile, cmf['fps']
    return inpfile, outfile

def ui_p3dmodel_creation (entparams = [], appsetup = {}):
    def get_filemapping (dirp = None, start = 1, last = 999999, tcount = 1):
        fcount = len(list(dirp.glob('frame__??????.png')))
        if fcount > last: fcount = last
        if start > 1: fcount = fcount - start + 1
        if (dirp / 'frame__000000.png').exists(): fcount = fcount - 1
        mapls = pyback.fixinitemlist (lfrom = fcount-1, linto = tcount)
        retval = [x + start for x in mapls]
        return retval
    def filemapcopy (cmap = [], imgsrc = None, imgdst = None):
        if not imgdst.is_dir(): imgdst.mkdir(parents=True, exist_ok=True)
        for ix, frid in enumerate(cmap):
            print (f"copying file {frid} as {ix}")
            oldimg = imgsrc / ("frame__"+"%06d"%(frid)+".png")
            newimg = imgdst / ("frame__"+"%06d"%(ix)+".png")
            if newimg.exists(): newimg.unlink()
            shutil.copy(oldimg, newimg)
        print ("PNG COPY COMPLETED")
    if '/' not in entparams[1]: entparams[1] = 'media/' + entparams[1]
    inpfile, outfile, curfps = create_output_path (param0 = entparams[0], param1 = entparams[1], appsetup = appsetup, outfolder = 1, getfps = 1)
    if isinstance(curfps, str): curfps = appsetup['project']['fps']
    thinned = pyback.forceint(entparams[4], 0)
    print ("create_output_path returned:", inpfile, outfile, curfps, isinstance(curfps, str))
    if inpfile == None or outfile == None or inpfile == outfile:
        localmessage(mtype = 'error', title = 'Input & Output path error', message = "Input or Output path are incorrect or same")
        return -1
    csframe = pyback.forceint(entparams[2].split(",")[0], 1)
    clframe = pyback.forceint(entparams[2].split(",")[1], 999999) if len(entparams[2].split(",")) > 1 else 999999
    if clframe < csframe: clframe = 999999
    curfps = curfps if pyback.forceint(entparams[3], curfps) < 1 else pyback.forceint(entparams[3], curfps) 
    if thinned == 0:
        pyback.png_overwrites (csframe = csframe, tdframe = csframe-1, clframe = clframe, imgsrc = inpfile, imgdst = outfile, owrite = 1, action = ['copy'])
    else:
        copymap = get_filemapping (dirp = inpfile, start = csframe, last = clframe, tcount = thinned)
        filemapcopy (cmap = copymap, imgsrc = inpfile, imgdst = outfile)
        print (f"copymap: {copymap}")
    pyback.create_media_p3dmodel (ifile = outfile, owrite = 1, appsetup = appsetup, fps = curfps)
    return 1

def ui_image_manipulation_craft (entparams = [], appsetup = {}):
    permissibles = ['doodle', 'cartoon', 'sketch']
    if entparams[2] not in permissibles:
        localmessage (mtype = 'error', title = 'Incorrect action type', message = f"The feature to be modified should be one of: {', '.join(permissibles)}")
        return -1
    inpfile, outfile = create_output_path (param0 = entparams[0], param1 = entparams[1], appsetup = appsetup, outfolder = 0)
    if inpfile.is_dir():
        for ifile in inpfile.iterdir():
            if not ifile.suffix in appsetup['images']: continue
            ofile = outfile / ifile.name
            image_createillustration (ifile = ifile, ofile = ofile, method = entparams[2], islist = 1, appsetup = appsetup)
    else: image_createillustration (ifile = inpfile, ofile = outfile, method = entparams[2], islist = 0, appsetup = appsetup)
    return 1

def image_createillustration (ifile = '', ofile = '', method = '', islist = 0, appsetup = {}):
    def create_image_doodle (ifile = '', ofile = '', thresh = 255):
        if thresh > 255: thresh = 255
        def thresh_callback(val):
            threshold = val
            canny_output = cv2.Canny(src_gray, threshold, threshold * 2)
            contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            drawing = numpy.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=numpy.uint8)
            for ix in range(len(contours)):
                cv2.drawContours(drawing, contours, ix, (255,255,255), 2, cv2.LINE_8, hierarchy, 0)
            cv2.imwrite(ofile, drawing)
            return contours
        src = cv2.imread(ifile)
        src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        max_thresh = 255
        contours = thresh_callback(thresh)
        return contours
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
    def create_image_sketch (ifile = '', ofile = '', gindex = 21, sigmaX = 0, sigmaY = 0):
        img = cv2.imread(ifile, 1)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_invert = cv2.bitwise_not(img_gray)
        img_smoothing = cv2.GaussianBlur(img_invert, (gindex, gindex), sigmaX=0, sigmaY=0)
        def dodgeV2(x, y):
            return cv2.divide(x, 255 - y, scale=256)
        nimage = dodgeV2(img_gray, img_smoothing)
        cv2.imwrite(ofile, nimage)
        return 1
    if method == 'sketch': create_image_sketch (ifile = str(ifile), ofile = str(ofile))
    elif method == 'cartoon': create_image_cartoon (ifile = str(ifile), ofile = str(ofile))
    elif method == 'doodle':
        contours = create_image_doodle (ifile = str(ifile), ofile = str(ofile))
        if islist == 1: return 1
        campos, bcenter = '0, -120, 0', '0, 0, 0'
        # pwide, phigh = Image.open(ifile).size
        # logictxt, thisf, lastf, groups = '', 1, 1, [0]
        # canwide, canhigh = 500, 500
        # diffw, diffh = int((canwide-pwide)/2), int((canhigh-phigh)/2)
        diffw, diffh = 0, 0
        groups, pxdata = [0], []
        for ix, contour in enumerate(contours):
            for jx, item in enumerate(contour):
                if jx-1 > len(contour)/2: break
                pxdata.append([item[0][0]+diffw, item[0][1]+diffh])
            groups.append(len(pxdata))
        pyback.exec_save_coords (entparams = [campos, bcenter, ofile.stem], appsetup = appsetup, coord = str(pxdata), addxtra = {'group': groups})
        pyback.set_multifile_coords (file = ofile.stem, appsetup = appsetup, addlogic = 1)
    return 1

def ui_image_manipulation_basic (entparams = [], appsetup = {}):
    permissibles = ['contrast', 'color', 'brightness', 'sharpness', 'invert']
    if entparams[2] not in permissibles:
        localmessage (mtype = 'error', title = 'Incorrect action type', message = f"The feature to be modified should be one of: {', '.join(permissibles)}")
        return -1
    newVal = pyback.forceint(entparams[3], 1) if entparams[3] != 'range' else 'range'
    outfolder = 1 if newVal == 'range' else 0
    inpfile, outfile = create_output_path (param0 = entparams[0], param1 = entparams[1], appsetup = appsetup, outfolder = outfolder)
    if inpfile.is_dir() and newVal == 'range':
        localmessage (mtype = 'error', title = 'Range is invalid', message = f"Setting range over already set of images will create too many media. Stopping")
        return -1
    if inpfile.is_dir():
        for ifile in inpfile.iterdir():
            ofile = outfile / ifile.name
            enhance_image_basic (ifile = ifile, ofile = ofile, param = entparams[2], nval = newVal)
    elif newVal == 'range':
        for frid in range(1, 101):
            newcVal = (frid-1)*0.1
            ofile = outfile / ("frame__"+"%06d"%(frid)+".png")
            enhance_image_basic (ifile = inpfile, ofile = ofile, param = entparams[2], nval = newcVal)
    else: enhance_image_basic (ifile = inpfile, ofile = outfile, param = entparams[2], nval = newVal)
    return 1

def enhance_image_basic (ifile = '', ofile = '', param = '', nval = 1.0):
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
    if param == 'sharpness':
        sharpness = ImageEnhance.Sharpness(image)
        sharpness.enhance(nval).save(ofile)
    if param == 'invert':
        rgbimg = image.convert('RGB')
        rgbimginv = ImageOps.invert(rgbimg)
        rgbimginv.save(ofile)
    return 1

# Below function is for internal consumption only
def _image_resize (ifile = '', ofile = '', nsize = 100):
    if ifile.suffix in appsetup['pictures']:
        image = Image.open(ifile)
        cwide, chigh = image.size
        if pyback.forceint(nsize, default = -1) != -1:
            nwide, nhigh = int(cwide*int(nsize)/100), int(chigh*int(nsize)/100)
        else:
            nwide, nhigh = pyback.getscreensize (nsize, cwide, chigh)
        nimage = image.resize((nwide, nhigh), Image.ANTIALIAS)
        nimage.save(ofile)
    elif ifile.suffix in appsetup['movies']:
        cmdstr = f"ffmpeg -i \"{ifile}\" -filter:v \"crop=960:1080:480:0\" \"{ofile}\""
        os.system(cmdstr)
    return 0

def ui_image_manipulation_rmback (entparams = [], appsetup = {}):
    permissibles = ['ibrt', 'static']
    if entparams[2].lower() not in permissibles:
        localmessage (mtype = 'error', title = 'Incorrect action type', message = f"The feature to be modified should be one of: {', '.join(permissibles)}")
        return -1
    inpfile, outfile = create_output_path (param0 = entparams[0], param1 = entparams[1], appsetup = appsetup, outfolder = 0)
    if inpfile.is_dir():
        for ifile in inpfile.iterdir():
            if not ifile.suffix in appsetup['images']: continue
            ofile = outfile / ifile.name
            image_removebackground (ifile = ifile, ofile = ofile, method = entparams[2].lower(), params = entparams[3].lower(), appsetup = appsetup)
    else: image_removebackground (ifile = inpfile, ofile = outfile, method = entparams[2].lower(), params = entparams[3].lower(), appsetup = appsetup)
    return 1

def image_removebackground (ifile = '', ofile = '', method = 'mrcnn', params = 'green', appsetup = {}):
    def ibrt_removebackground (ifile = '', ofile = ''):
        appdir = os.getcwd()
        try:
            os.chdir("ibrt")
            cmdstr = f'ppython main.py -i "{ifile}" -o "{ofile}"  -m u2net'
            rval = os.system(cmdstr)
        finally: os.chdir(appdir)
        return 1
    def screen_removebackground (ifile = '', ofile = '', crange = None):
        print (f"Crange: {crange}")
        image = cv2.imread(ifile)
        image_copy = numpy.copy(image)
        image_copy = cv2.cvtColor(image_copy, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(image_copy, numpy.array(crange[0]), numpy.array(crange[1]))
        cv2.imwrite('temp/image_bgscreen_removal_mask.png',mask)
        ximg = Image.open(ifile)
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
        return 1
    def color_removebackground (ifile = '', ofile = '', color = [0,0,0]):
        img = Image.open(ifile)
        img = img.convert("RGBA")
        datas = img.getdata()
        newData = []
        for ix, item in enumerate(datas):
            if item[0] == color[0] and item[1] == color[1] and item[2] == color[2]:
                newData.append((item[0],item[1],item[2], 0))
            else:
                newData.append(item)
        img.putdata(newData)
        img.save(ofile, "PNG")
    def canberange(params):
        rtl, rth = params.split(';', 1)
        rtlv, rthv = list(map (int, rtl.split(','))), list(map (int, rth.split(',')))
        return [rtlv,rthv]
    if method == 'ibrt': ibrt_removebackground (ifile = ifile.resolve(), ofile = ofile.resolve())
    elif method == 'static':
        if params in colorcode and params[:3] != 'all': color_removebackground (ifile = str(ifile), ofile = str(ofile), color = colorcode[params])
        elif params in colorcode and params[:3] == 'all': screen_removebackground (ifile = str(ifile), ofile = str(ofile), crange = colorcode[params])
        else:
            try:
                crange = canberange(params)
                screen_removebackground (ifile = str(ifile), ofile = str(ofile), crange = crange)
            except: localmessage (mtype = 'error', title = 'Incorrect color', message = "Please check documentation for correct color name/ range.")
    return 1

def ui_prepare_stage (entparams = [], appsetup = {}):
    outfile = confirm_file (entparams[1], ftype = 'input', fback = '', appsetup = appsetup, isnew = 1)
    for idir in entparams[0].split(','):
        ipath = confirm_file (idir, ftype = 'input', fback = '', appsetup = appsetup, isnew = 0)
        print (f"copying over data for {ipath}")
        if not ipath.is_dir(): continue
        pyback.png_overwrites (csframe = 1, clframe = 999999, imgsrc = ipath, imgdst = outfile, owrite = 0, action=['copy', 'append'])
    movfile = outfile.name+'.'+entparams[2]
    pyback.exec_pic_export (entparams = [movfile, appsetup['project']['fps'], "1, -1"], appsetup = appsetup, rushes = outfile, secon = 1)

def image_manual_bgremoval (entparams = [], appsetup = {}):
    ipath = Path(appsetup['project']['name']) / 'rushes'
    opath = confirm_file (entparams[1], ftype = 'video', fback = '', appsetup = appsetup, isnew = 1)
    if opath.exists():
        UREP = localmessage (mtype = 'ask', title = 'Path already exists', message = f"There is already a filepath with name {opath}. Overwrite its content?")
        if UREP == 'cancel': return -1
        else:
            shutil.rmtree(opath)
            opath.mkdir()
    else: opath.mkdir()
    basefile = ipath / ("frame__"+"%06d"%(pyback.forceint(entparams[0], 2))+".png")
    trans = colorcode[entparams[2]] if entparams[2] in colorcode else colorcode['black']
    keeps = [255,255,255]
    alpha = 255
    bimg = Image.open(basefile)
    bimg = bimg.convert("RGBA")
    bstate = bimg.getdata()
    def pixwise_removal (ifile = Path(), ofile = Path(), bstate = [], trans = [0,0,0], keeps = [255,255,255], alpha = 255):
        ximg = Image.open(str(ifile))
        ximg = ximg.convert("RGBA")
        xstate = ximg.getdata()
        pcount = ximg.size[0] * ximg.size[1]
        newData = []
        for ix in range(0, pcount):
            bitem, xitem = bstate[ix], xstate[ix]
            if (xitem[0] == trans[0] and xitem[1] == trans[1] and xitem[2] == trans[1]):
                toappend = (bitem[0], bitem[1], bitem[2], alpha)
            else:
                toappend = (xitem[0], xitem[1], xitem[2], 0)
            newData.append(toappend)
        ximg.putdata(newData)
        ximg.save(str(ofile), "PNG")
        return 1
    for file in ipath.iterdir():
        if file.name[:7] != 'frame__' or file.suffix != '.png' or not file.is_file(): continue
        pixwise_removal (ifile = file, ofile = opath / file.name, bstate = bstate, trans = trans, keeps = keeps, alpha = alpha)
    return 1

def ui_moverushstaging (entparams = [], appsetup = {}):
    inpfile = Path(appsetup['project']['name']) / 'rushes'
    outfile = confirm_file (entparams[0], ftype = 'input', fback = 'video/'+str(time.time())+"__blank__", isnew = 1, appsetup = appsetup)
    frames = entparams[1].split(',')
    fframe = pyback.forceint(frames[0], 1)
    lframe = 999999 if len(frames) < 2 else pyback.forceint(frames[1], 999999)
    if lframe < fframe: lframe = 999999 
    pyback.png_overwrites (csframe = fframe, clframe = lframe, imgsrc = inpfile, imgdst = outfile, owrite = 0, action = ['append', 'copy'])
    return 1