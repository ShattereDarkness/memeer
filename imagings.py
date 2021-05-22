from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont
import mrcnn
import mrcnn.config
import mrcnn.model
import mrcnn.visualize
import cv2
import os
import cv2
import matplotlib.font_manager
import numpy
import argparse
import random

import pyback

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

def ui_find_image_contours (entparams = [], appsetup = {}):
	ifile = entparams[0]
	ofile = entparams[1]
	campos = entparams[2]
	bcenter = entparams[3]
	print ("ifile, ofile, campos, bcenter", ifile, ofile, campos, bcenter)
	proc = find_image_contours (ifile = ifile, ofile = ofile)
	ofileo = Path(ofile)
	contours = proc['data']['contours']
	logictxt, thisf, lastf = '', 1, 1
	for ix, contour in enumerate(contours):
		pxdata = []
		cofile = "%04d" % (ix) + ofileo.stem + '.coord'
		for jx, item in enumerate(contour):
			if jx-1 > len(contour)/2: break
			pxdata.append([item[0][0], item[0][1]])
		print ("pxdata", pxdata)
		pyback.exec_save_coords (entparams = [campos, bcenter, cofile], appsetup = appsetup, coord = str(pxdata), revert = 0)
		thisf = lastf + len(pxdata)
		logictxt = logictxt + "line is drawn @f(" + cofile + ") #" + str(lastf) + "-#" + str(thisf) + "\n"
		lastf = thisf
	return {'code': 'OK', 'estack': [], 'data': {'logictxt': logictxt, 'imgfile': ofile, 'count': len(contours)}}

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

def set_transparency (ctype = 'B', analog = 0, ifile = '', ofile = ''):
	'''Black background converts to transparent - BINARY'''
	img = Image.open(ifile)
	img = img.convert("RGBA")
	datas = img.getdata()
	newData = []
	for item in datas:
		if ctype == 'W' and item[0] == 255 and item[1] == 255 and item[2] == 255:
			newData.append((255, 255, 255, 0))
		elif ctype == 'B' and item[0] == 0 and item[1] == 0 and item[2] == 0:
			newData.append((0, 0, 0, 0))
		elif  ctype == 'A':
			newtrans = (765 - (item[0]+item[1]+item[2]))/765
			newData.append((item[0], item[1], item[2], 1))
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

def image_resize (ifile = '', high = 1, wide = 1, rtype = 'rel'):
	if rtype not in ['rel', 'abs', 'sim']: return 1
	image = Image.open(ifile)
	if rtype == 'abs': nimage = image.resize((high, wide), Image.ANTIALIAS)
	if rtype == 'rel':
		width, height = im.size
		nimage = image.resize((width*wide, height*high), Image.ANTIALIAS)
	if rtype == 'sim': nimage = image.thumbnail((high, wide), Image.ANTIALIAS)
	nimage.save(ofile)
	return 0
	
def check_sysytem_fonts (fontlike):
	'''Returns the font file for the given name - best match for the name'''
	inputt = fontlike.split(' ')
	flist = flist = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
	maxmatch = -1
	retval = ''
	for fname in flist:
		if matplotlib.font_manager.FontProperties(fname=fname).get_name() == fontlike: return fname
		names = matplotlib.font_manager.FontProperties(fname=fname).get_name().split(' ')
		match = set(names) & set(inputt)
		if match > maxmatch: retval = fname
	return retval
	
def text_as_image (xy = [0, 0], imgtext = '', ifile = '', ofile = '', fill=None, font=None, anchor=None, spacing=4, align='left', size = 10,
		direction=None, features=None, language=None, stroke_width=0, stroke_fill=None, embedded_color=False):
	'''Black background converts to transparent - BINARY'''
	if font == '': lfont = ImageFont.load_default()
	else: lfont = ImageFont.truetype(font, size)
	image = Image.open(ifile)
	draw = ImageDraw.Draw(image)
	draw.text(xy, imgtext, font=lfont, fill=fill)
	image.save(ofile)
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
	if loc[2] == 'abs':	center = (loc[0], loc[1])
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
