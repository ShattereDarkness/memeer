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

import json
import pyback
import copy
import shutil

def ui_addaudiotovideo (params):
    if params[2] == '': params[2] = '00:00:10'
    if params[4] == '': params[4] = params[0]
    rval = f_add_audio_video_timewise (vfile = params[0], afile = params[1], startt = params[2], tlen = params[3], outfile = params[4])
    return rval

def ui_mrcnn_objects (params):
    ifile = params[0]
    ofiles = params[1]
    if params[0] == '' or params[1] == '': return 1
    mrcnn_image_retrieval (ifile = ifile, ofiles = ofiles)
    return 1

def int_proc_filenames (entparams = [], appsetup = {}, defextn = '.png', basedir = 'media'):
    ifile = entparams[0]
    ofile = entparams[1]
    bdir = Path(appsetup['project']['name']) / basedir
    ifile, ofile = bdir / ifile, bdir / ofile
    if ofile.suffix == '': ofile = bdir / (entparams[1] + defextn)
    return {'ifile': ifile, 'ofile': ofile}

def ui_image_manipulation_basic (entparams = [], appsetup = {}):
    files = int_proc_filenames (entparams = entparams, appsetup = appsetup)
    ifile, ofile = files['ifile'], files['ofile']
    if entparams[2] != '': image_resize (ifile = ifile, ofile = ofile, nsize = entparams[2])
    return 1

def ui_image_manipulation (function = '', entparams = [], appsetup = {}):
    print ("function, entparams, appsetup", function, entparams, appsetup)
    files = int_proc_filenames (entparams = entparams, appsetup = appsetup, basedir = 'video')
    ifile, ofile = files['ifile'], files['ofile']
    if entparams[2] == '': entparams[2] = 'black'
    if function not in ('setcolortransparent'): return 1
    function = "f_" + function
    globals()[function] (ifile, ofile, color = entparams[2], params = entparams[3], appsetup = appsetup)
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
    sframe = pyback.forceint(entparams[0], default = 1)
    lframe = pyback.forceint(entparams[1], default = 1)
    sourcep = Path(appsetup['project']['name']) / 'rushes'
    destinp = Path(appsetup['project']['name']) / 'video' / entparams[2]
    pyback.pngoverwrites (fframe = 2-sframe, lframe = lframe, imgsource = sourcep, imgdest = destinp, overwrite = 1, action='copy')
    pyback.exec_pic_export (entparams = [entparams[2], appsetup['project']['fps'], "1, -1"], appsetup = appsetup, rushes = '/video/'+entparams[2]+'/')

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

def ui_text_image_creation (entparams = [], appsetup = {}):
    if entparams[0] == '': return 1
    if entparams[1] == '': return 1
    file = Path(appsetup['project']['name']) / 'media' / entparams[0]
    if file.suffix != '.png': file = Path(appsetup['project']['name']) / 'media' / (entparams[0]+'.png')
    imgsize = pyback.getscreensize (appsetup['project']['winsize'], 500, 500)
    font = check_system_fonts (entparams[2])
    fontsize = pyback.forceint (entparams[3], 16)
    text_as_image (file = file, imgsize=(imgsize), color = (1, 1, 1, 255), pixloc = (0,0), text = entparams[1], font = font, fontsize = fontsize, align = 'left')
    os.chdir(Path(appsetup['project']['name']) / 'model')
    print ("os.getcwd()", os.getcwd())
    cmdstr = "egg-texture-cards -o " + file.stem + ".egg -fps "+str(appsetup['project']['fps'])+" ../media/" + file.stem + ".png"
    os.system(cmdstr)
    print ("cmdstr", cmdstr)
    os.chdir('../..')
    print ("os.getcwd()", os.getcwd())
    return 1

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

def f_add_audio_video_timewise (vfile = '', afile = '', startt = '', tlen = '', outfile = ''):
    ''' Example is ffmpeg -ss 00:00:10  -t 5 -i "video.mp4" -ss 0:00:01 -t 5 -i "music.m4a" -map 0:v:0 -map 1:a:0 -y out.mp4 '''
    cmdstr = 'ffmpeg -i ' + vfile + ' -ss ' + startt + ' -t ' +  tlen + ' -i ' + afile + ' -map 0:v:0 -map 1:a:0 -y ' + outfile
    rval = os.system(cmdstr)
    return rval

def ibrt__OPHoperHPO (ifile = '', ofiles = ''):
    cmdstr = 'ppython ibrt/main.py -i ' + ifile + ' -o ' + ofile + ' -m u2net'
    rval = os.system(cmdstr)
    return rval

def mrcnn_image_retrieval (ifile = '', ofiles = ''):
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
    
def check_system_fonts (fontlike):
    '''Returns the font file for the given name - best match for the name'''
    inputt = fontlike.lower().split(' ')
    flist = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    maxmatch = 0
    retval = ''
    for fname in flist:
        fontname = matplotlib.font_manager.FontProperties(fname=fname).get_name()
        fontpath = Path(fname)
        if fontname == fontlike or fontpath.stem.lower() == fontlike: return fname
        names = fontname.lower().split(' ') + [fontpath.stem.lower()]
        match = len(list(set(names) & set(inputt)))
        if match > maxmatch:
            retval = fname
            maxmatch = match
    return retval

def text_as_image (file = Path(), imgsize=(500,500), color = (1, 1, 1, 255), pixloc = (10,10), text = '', font = '', fontsize = 10, align = 'left'):
    '''Black background converts to transparent - BINARY'''
    image = Image.new('RGBA', imgsize, color = (255, 255, 255, 0))
    if font == '': ffont = ImageFont.load_default()
    else: ffont = ImageFont.truetype(font, fontsize)
    draw = ImageDraw.Draw(image)
    draw.text((0,0), text, font=ffont, fill=color)
    image.save(str(file), "PNG")
    return 1

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
