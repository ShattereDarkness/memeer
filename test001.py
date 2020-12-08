import FNC_default

import os.path
from os import path
import sys

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import loadPrcFileData
import logging
import time
import pprint

logging.basicConfig(filename='test001.js', filemode='w', format='%(message)s')

fexpand = [{'qpno': [1, 2], 'act': [0], 'tag': {}, 'text': 'young lady was standing', 'mmatch': [{'qseq': '0', 'fseq': '0'}, {'qseq': '3', 'fseq': '1'}, {'qseq': '1', 'fseq': '0'}, {'qseq': '3', 'fseq': '1'}], 'node': {'0': {'file': 'P3DModels/A20GFLC_base', '3dpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'tags': {'vagaries': ['base', 'sanscloth'], 'synonyms': []}, 'acts': {'walk': 'P3DModels/A20GFLC-A20g01_02', 'stand': 'P3DModels/A20GFLC-A20g77_02', 'default': 'P3DModels/A20GFLC-A20g77_02', 'run': 'P3DModels/A20GFLC-A20g02_03', 'kick': 'P3DModels/A20GFLC-A20g10_02', 'trnl': 'P3DModels/A20GFLC-A20g16_17', 'trnr': 'P3DModels/A20GFLC-A20g16_19'}, 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['selfmove', 'young'], 'synonyms': ['lady', 'human', 'she']}}, '1': {'file': 'P3DModels/A20GFLC-A20g77_02', 'tags': {'vagaries': ['defaultact'], 'synonyms': ['wait', 'loiter', 'stand', 'ladyacts']}, 'frames': [[[-2.77, -0.648, 0, 0, 0, 0, 1, 1, 1], 10, 83]], 'name': 'stand', 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['selfmove', 'young'], 'synonyms': ['lady', 'human', 'she']}}}, 'fnmatch': {'fname': 'she_standing', 'ftag': '2node', 'fseq': 0, 'foid': '57'}}, {'qpno': [0], 'act': [1], 'tag': {}, 'text': 'a furniture was laying there', 'mmatch': [{'qseq': '1', 'fseq': '0'}, {'qseq': '3', 'fseq': '1'}], 'node': {'0': {'file': 'P3DModels/CoffeeTable', '3dpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'tags': {'vagaries': ['base', 'physical'], 'synonyms': ['stool', 'furniture', 'coffee table', 'table']}, 'acts': {}, 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['static'], 'synonyms': ['stool', 'furniture', 'table']}}, '1': {'tags': {'vagaries': [], 'synonyms': ['lay']}, 'name': 'lay', 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['static'], 'synonyms': ['stool', 'furniture', 'table']}}}, 'fnmatch': {'fname': 'object_lay', 'ftag': 'text', 'fseq': 1, 'foid': '56'}}, {'qpno': [], 'act': [2], 'tag': {}}, {'qpno': [0], 'act': [2, 1], 'tag': {}, 'text': 'she walked till furniture', 'mmatch': [{'qseq': '0', 'fseq': '0'}, {'qseq': '1', 'fseq': '1'}], 'node': {'0': {'file': 'P3DModels/A20GFLC_base', '3dpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'tags': {'vagaries': ['base', 'sanscloth'], 'synonyms': []}, 'acts': {'walk': 'P3DModels/A20GFLC-A20g01_02', 'stand': 'P3DModels/A20GFLC-A20g77_02', 'default': 'P3DModels/A20GFLC-A20g77_02', 'run': 'P3DModels/A20GFLC-A20g02_03', 'kick': 'P3DModels/A20GFLC-A20g10_02', 'trnl': 'P3DModels/A20GFLC-A20g16_17', 'trnr': 'P3DModels/A20GFLC-A20g16_19'}, 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['selfmove', 'young'], 'synonyms': ['lady', 'human', 'she']}}, '1': {'file': 'P3DModels/A20GFLC-A20g01_02', 'tags': {'vagaries': [], 'synonyms': ['move', 'stroll', 'walk', 'ladyacts']}, 'frames': [[[0, 0, 0, 0, 0, 0, 1, 1, 1], 1, 17]], 'modl': {'deny': [], 'allow': [], 'default': []}, 'name': 'walk', 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['selfmove', 'young'], 'synonyms': ['lady', 'human', 'she']}}}, 'fnmatch': {'fname': 'she_standing', 'ftag': '2node', 'fseq': 0, 'foid': '57'}}, {'qpno': [0], 'act': [2, 2], 'tag': {'0': 'dirfrom'}, 'text': 'she kicked', 'mmatch': [{'qseq': '0', 'fseq': '0'}, {'qseq': '1', 'fseq': '1'}], 'node': {'0': {'file': 'P3DModels/A20GFLC_base', '3dpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'tags': {'vagaries': ['base', 'sanscloth'], 'synonyms': []}, 'acts': {'walk': 'P3DModels/A20GFLC-A20g01_02', 'stand': 'P3DModels/A20GFLC-A20g77_02', 'default': 'P3DModels/A20GFLC-A20g77_02', 'run': 'P3DModels/A20GFLC-A20g02_03', 'kick': 'P3DModels/A20GFLC-A20g10_02', 'trnl': 'P3DModels/A20GFLC-A20g16_17', 'trnr': 'P3DModels/A20GFLC-A20g16_19'}, 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['selfmove', 'young'], 'synonyms': ['lady', 'human', 'she']}}, '1': {'file': 'P3DModels/A20GFLC-A20g10_02', 'tags': {'vagaries': [], 'synonyms': ['kick', 'ladyacts']}, 'frames': [[[0, 0, 0, 0, 0, 0, 1, 1, 1], 35, 118]], 'name': 'kick', 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['selfmove', 'young'], 'synonyms': ['lady', 'human', 'she']}}}, 'fnmatch': {'fname': 'she_standing', 'ftag': '2node', 'fseq': 0, 'foid': '57'}}, {'qpno': [0], 'act': [2, 3], 'tag': {'0': 'dirto'}, 'text': 'furniture thrown 3 meters away', 'mmatch': [{'qseq': '0', 'fseq': '0'}, {'qseq': '1', 'fseq': '1'}], 'node': {'0': {'file': 'P3DModels/CoffeeTable', '3dpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'tags': {'vagaries': ['base', 'physical'], 'synonyms': ['stool', 'furniture', 'coffee table', 'table']}, 'acts': {}, 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['static'], 'synonyms': ['stool', 'furniture', 'table']}}, '1': {'tags': {'vagaries': [], 'synonyms': ['thrown', 'kicked']}, 'name': 'kick', 'gpoint': [0, 0, 0, 0, 0, 0, 1, 1, 1], 'gtags': {'vagaries': ['static'], 'synonyms': ['stool', 'furniture', 'table']}}}, 'fnmatch': {'fname': 'object_thrown', 'ftag': 'wdist', 'fseq': 0, 'foid': '63'}}]
world = {'models': [], 'scene': [-1], 'nscene': 1, 'lsframe': 0, 'scenery': {}, 'tagval': {}}
FNC_default.fexpand = fexpand
FNC_default.world = world

def addposhprscl (pos1 = [0, 0, 0], pos2 = [0, 0, 0]):
	return [[pos1[0]+pos2[0], pos1[1]+pos2[1], pos1[2]+pos2[2]]]

def addonposhpr (actor = {}, pos2 = []):
	cpos = actor['actor'].getTightBounds()
	actor['actor'].setPos(actor['actor'], pos2[0], pos2[1], pos2[2])

# Define a procedure to move the camera.
def defaultTask(task):
	logging.error('Current frame: '+str(task.frame))
	if len(world['models']) > 0:
		ppos = world['models'][0]['actor'].getTightBounds()
		ppos3 = [(ppos[0][0]+ppos[1][0])/2, (ppos[0][1]+ppos[1][1])/2, (ppos[0][2]+ppos[1][2])/2]
		logging.error("Current pos for lady is "+pprint.pformat(ppos3))
	if world['nscene'] == 1:
		FNC_default.setupscenes(lastscene = world['scene'])
		logging.error("Current state of the world...")
		logging.error(pprint.pformat(world))
		world['nscene'] = 0
		world['lsframe'] = task.frame
	if world['sceneid'] not in world['scenery']: sys.exit()
	if world['scenery'][world['sceneid']] == []:
		world['nscene'] = 1
		return Task.cont
	scframe = task.frame - world['lsframe']
	logging.error('Scene frame: '+str(scframe)+" and world lsframe: "+str(world['lsframe']))
	for ss, scenery in enumerate(world['scenery'][world['sceneid']]):
		if scframe > scenery['animat'][len(scenery['animat'])-1]['frid']:
			world['scenery'][world['sceneid']].pop(ss)
			continue
		actor = world['models'][scenery['model']]
		if actor['render'] == 1:
			actor['actor'].reparentTo(render)
			actor['render'] = 0
		tasks = list(filter(lambda x : x['frid'] == scframe, scenery['animat']))
		for utask in tasks:
			if utask['type'] == 'posit':
				addonposhpr (actor = actor, pos2 = utask['param'])
			if utask['type'] == 'posin':
				actor['actor'].pose(utask['param']['name'], utask['param']['pseq'])
			if utask['type'] == 'noact':
				pass
	if len(world['scenery'][world['sceneid']]) == 0:
		world['nscene'] = 1
	return Task.cont

ShowBase()
scene = loader.loadModel("P3DModels/BeachTerrain")
scene.reparentTo(render)
base.disableMouse()
camera.setPos(0, -120, 10)
camera.setHpr(0, 0, 0)
taskMgr.add(defaultTask, "defaultTask")
logging.error('######################## Starting ########################')
base.run()