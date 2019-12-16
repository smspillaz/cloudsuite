import numpy as np

SERVER_REQ_STR = "Outstanding requests per worker:"

class Benchmark:
    def __init__(self, key, values, endString=None):
        self.key = key
        self.values = values
        self.startString = "Signal handled: Interrupt"
        self.endString = endString or "seconds time elapsed"
        self.logVals = {}
    
    def addToMap(self, dictToUpdate, keySeq, v):
        if len(keySeq) == 1:
            dictToUpdate[keySeq[0]] = v
        else:
            if keySeq[0] not in dictToUpdate:
                dictToUpdate[keySeq[0]] = {}
            self.addToMap(dictToUpdate[keySeq[0]], keySeq[1:], v)

    def decodeLog(self, filename):
        with open(filename, "r") as f:
            # Pretty naive, but works
            inSegment = False
            parseServerReqs = False
            segmentCount = 0
            segmentKeys = []
            serverReqs = []
            for i, line in enumerate(f.readlines()):
                if self.endString in line:
                    # Compute avg. outstanding requests
                    try:
                        self.addToMap(self.logVals, segmentKeys +
                            ["Server queue"], sum(serverReqs) / len(serverReqs))
                    except Exception as e:
                        print(filename, i)
                        raise e

                    inSegment = False
                    segmentKeys = []
                    serverReqs = []
                    segmentCount += 1
                
                if inSegment:
                    # Parse server outstanding requests
                    if parseServerReqs:
                        #Format = "# # # # ..."
                        vals = [int(v) for v in line.strip().split(' ')]
                        serverReqs.append(sum(vals) / len(vals))
                        parseServerReqs = False

                    if SERVER_REQ_STR in line:
                        # Parse server outstanding requests in next line
                        parseServerReqs = True



                    # Parse performance counter stats
                    # Format: "#####    value       #comment"
                    tokens = line.split()
                    if len(tokens) > 1 and (tokens[1] in self.values):
                        k = tokens[1]
                        v = int(tokens[0])
                        self.addToMap(self.logVals, segmentKeys + [k], v)
                        #logVals[k].append(v)
                
                if line.startswith(self.key) and not inSegment:
                    #Format: "self.key, # x, # y, ..."
                    segments = line.replace(self.key,'').strip().split(",")
                    for seg in segments:
                        seg = seg.strip()
                        segmentKeys.append(seg)
                    inSegment = True


def appendIfNotInlist(l, v):
    if v not in l:
        l.append(v)

def extract2DValues(d, key):
    x = []
    y = []
    z = []

    for k1, v1 in d.items():
        x.append(k1)
        z_vals = []
        for k2, v2 in v1.items():
            appendIfNotInlist(y, k2)
            z_vals.append(v2[key])
        z.append(z_vals)

    return (x,y,z)

def extractMapFromMap(m, keys):
    if len(keys) > 0:
        return extractMapFromMap(m[keys[0]], keys[1:])
    else:
        return m

def extractKVFromMap(m, valueKey):
    # Assumes that the map is 1 level deep
    return { k: m[k][valueKey] for k, v in m.items()}

def listMerge(d1, d2):
    # Merge leaf values of d2 together with d1, as a list
    for k, v in d1.items():
        if type(v) is dict:
            listMerge(d1[k], d2[k])
        else:
            # update as a list
            if type(v) is list:
                d1[k].append(d2[k])
            else:
                d1[k] = [v, d2[k]]

def listdicToAvgStdDev(d1):
    # Transform a dict of leaf values into an average and standard deviation estimate
    for k, v in d1.items():
        if type(v) is dict:
            listdicToAvgStdDev(d1[k])
        else:
            avg = np.average(v)
            std = np.std(v)
            d1[k] = {"avg" : avg, "std" : std}


def genAvgStdDevForLogVals(benchmarkList):
    bm = benchmarkList[0]
    for bmx in benchmarkList[1:]:
        listMerge(bm.logVals, bmx.logVals)
    
    listdicToAvgStdDev(bm.logVals)

    return bm
