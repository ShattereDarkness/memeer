import math
import pprint

def getlocations (action = {}, position = {}, frames = 0):
    retval = []
    fncname = action['locfunc']
    fromloc = list(map(int, position['locfrom']))
    uptoloc = list(map(int, position['locupto']))
    frames = min (frames, 1000)
    if fncname == 'linearmove':
        newHpr = getHpr (pfrom = fromloc, pupto = uptoloc)
        for ix in range(0, frames):
            retval.append([(uptoloc[0]-fromloc[0])*ix/frames, (uptoloc[1]-fromloc[1])*ix/frames, (uptoloc[2]-fromloc[2])*ix/frames, 0, 0, 0, 1, 1, 1])
        for ix in range(0, 3):
            retval[0][ix+3] = newHpr[ix] + action['initHpr'][ix]
    else:
        for ix in range(0, frames):
            retval.append([0, 0, 0, 0, 0, 0, 1, 1, 1])
    return retval

def serealize (animation = []):
    scenefunc = []
    for ano, anime in enumerate(animation):
        scene = anime['scene']['act']
        print ('Serealizing scene: ', scene, end='')
        stext = anime['qdets']['sttmts'][0] if 'qdets' in anime and 'sttmts' in anime['qdets'] and len(anime['qdets']['sttmts'])> 0 else ''
        scenefunc.append({'fncnm': 'screentext', 'text': stext})
        if 'camera' in anime['animat']:
            scenefunc.append({'fncnm': 'camerasetup', 'params': anime['animat']['camera']})
            frlen = anime['animat']['frlen'] if 'frlen' in anime['animat'] else 1
            for no in range(0, frlen):
                scenefunc.append({'fncnm': 'passblank'})
        if 'text' in anime['animat'] and 'mode' in anime['animat'] and anime['animat']['mode'] == 'error':
            frlen = anime['animat']['frlen'] if 'frlen' in anime['animat'] else 1
            for no in range(0, frlen):
                scenefunc.append({'text': anime['animat']['text'], 'mode': anime['animat']['mode']})
        if 'newobj' in anime['animat'] and 'acts' not in anime['animat']['newobj']:
            scenefunc.append({'fncnm': 'newmodel', 'params': anime})
            frlen = anime['animat']['frlen'] if 'frlen' in anime['animat'] else 1
            for no in range(0, frlen):
                scenefunc.append({'fncnm': 'passblank'})
        if 'newobj' in anime['animat'] and 'acts' in anime['animat']['newobj']:
            scenefunc.append({'fncnm': 'newactor', 'params': anime})
            maxfrs = anime['animat']['action']['frlen'] if 'frlen' in anime['animat']['action'] else 10000
            locarr = []
            if 'locfunc' in anime['animat']['action']:
                frcount = sum(map(lambda x: x[2]-x[1], anime['animat']['action']['frame']))
                if frcount > maxfrs: frcount = maxfrs
                locarr = getlocations (action = anime['animat']['action'], position = anime['qdets'], frames = frcount)
            frcount = 0
            for frset in anime['animat']['action']['frame']:
                for frid in range (frset[1], frset[2]):
                    scnfunc = {'fncnm': 'actorposes', 'frame': frid, 'params': {'model': anime['animat']['newobj']['file'],'action': anime['animat']['action']['name']}}
                    if (len(locarr) > frcount): scnfunc['params']['lochpr'] = locarr[frcount]
                    scenefunc.append(scnfunc)
                    #scenefunc.append({'fncnm': 'actorposes', 'frame': frid, 'params': {
                    #                   'model': anime['animat']['newobj']['file'],'action': anime['animat']['action']['name']}})
                    #if (len(locarr) > frcount): scenefunc[frcount]['lochpr'] = locarr[frcount]
                    frcount = frcount + 1
                if frcount > maxfrs: break
        print (len(scenefunc))
    return scenefunc

def getHpr (pfrom = [0, 0, 0, 0, 0, 0, 1, 1, 1], pupto = [0, 0, 0, 0, 0, 0, 1, 1, 1]):
    delX = int(pfrom[0]) - int(pupto[0])
    delY = int(pfrom[1]) - int(pupto[1])
    delZ = int(pfrom[2]) - int(pupto[2])
    camH = math.degrees(math.atan(delY/(0.00000001+delX)))
    camP = math.degrees(math.atan(delZ/(0.00000001+delY)))
    camR = math.degrees(math.atan(delX/(0.00000001+delZ)))
    return [camH, camP, camR]

def distance (pfrom = [0, 0, 0, 0, 0, 0, 1, 1, 1], pupto = [0, 0, 0, 0, 0, 0, 1, 1, 1]):
    delX = int(pfrom[0]) - int(pupto[0])
    delY = int(pfrom[1]) - int(pupto[1])
    delZ = int(pfrom[2]) - int(pupto[2])
    return math.sqrt(delX*delX + delY*delY + delZ*delZ)+0.00000001

def camerafocus (node = {}, fnmatch = {}, qdets = {}, tags = {}):
    camHpr = getHpr (pfrom = qdets['locfrom'], pupto = qdets['locupto'])
    return {'camera': [float(qdets['locfrom'][0]), float(qdets['locfrom'][1]), float(qdets['locfrom'][2]), camHpr[0], camHpr[1], camHpr[2]], 'frlen': 24}

def object_lay (node = {}, fnmatch = {}, qdets = {}, tags = {}):
    obj = {}
    if fnmatch['fseq'] in [0, 1, 6]: obj = node['0']
    if fnmatch['fseq'] in [2, 3, 4, 7, 8, 9, 10, 11]: obj = node['2']
    if obj == {}: return {}
    return {'newobj': {'file': obj['file'], 'gpoint': obj['gpoint']}, 'frlen': 24}

def she_standing (node = {}, fnmatch = {}, qdets = {}, tags = {}):
    obj, act = {}, {}
    if fnmatch['fseq'] == 4: obj, act = node['0'], node['1']
    if fnmatch['fseq'] == 5: obj, act = node['0'], node['1']
    if fnmatch['fseq'] == 6: obj, act = node['0'], node['1']
    if obj == {} or act == {}: return {}
    action = {'newobj': {'file': obj['file'], 'gpoint': obj['gpoint'], 'acts': obj['acts']},
                'action': {'name': act['name'], 'file': act['file'], 'frame': act['frames']}}
    action['action']['repeat'] = act['repeat'] if 'repeat' in act else 0
    if 'speed' in act and len(qdets['locfrom']) == 9 and len(qdets['locupto']) == 9:
        action['action']['initPos'] = qdets['locfrom']
        action['action']['initHpr'] = getHpr (pfrom = qdets['locfrom'], pupto = qdets['locupto'])
        action['action']['frlen'] = int(10*distance(pfrom = qdets['locfrom'], pupto = qdets['locupto'])/act['speed'])
        action['action']['locfunc'] = act['locfunc'] if 'locfunc' in act else 'passblank'
    return action

def object_thrown (node = {}, fnmatch = {}, qdets = {}, tags = {}):
    obj, act = {}, {}
    if fnmatch['fseq'] == 0: obj, act = node['0'], node['1']
    if obj == {} or act == {}: return {}
    if 'camera' in obj['gtags']['vagaries']:
        action = {'cameramove': {'initPos': qdets['locfrom'], 'uptoPos': qdets['locupto'], 'frlen': 24}}
    return action