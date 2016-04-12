
from pymjin2 import *

FILTER_ACTION_FALL      = "move.default.tileFall"
FILTER_ACTION_ROTATE    = "rotate.default.rotateFilter"
FILTER_LEAF_NAME        = "filterLeaf0"
FILTER_LEAF_NAME_PREFIX = "filterLeaf"
FILTER_LEAF_SLOT1       = 1
FILTER_LEAF_SLOT2       = 2
FILTER_NAME             = "filter"
FILTER_TILE_FACTORY     = "tileFactory"

class FilterImpl(object):
    def __init__(self, c):
        self.c = c
        self.filterName = None
        self.rotationSpeed = None
        self.tiles = {}
        self.tiles[FILTER_LEAF_SLOT1] = None
        self.tiles[FILTER_LEAF_SLOT2] = None
        self.lastFreeSlot = None
    def __del__(self):
        self.c = None
    def onFallFinish(self, key, value):
        self.c.unlisten("$FALL.$SCENE.$NAME.active")
        if (self.lastFreeSlot == FILTER_LEAF_SLOT2):
            self.validateTiles()
    def onRotationFinish(self, key, value):
        # Record old absolute position and rotation.
        vpold = self.c.get("node.$SCENE.$NAME.positionAbs")[0].split(" ")
        vrold = self.c.get("node.$SCENE.$NAME.rotationAbs")[0].split(" ")
        # Change parent.
        parent = "{0}{1}".format(FILTER_LEAF_NAME_PREFIX, self.lastFreeSlot)
        self.c.set("node.$SCENE.$NAME.parent", parent)
        # Record new absolute position and rotation.
        vpnew = self.c.get("node.$SCENE.$NAME.positionAbs")[0].split(" ")
        vrnew = self.c.get("node.$SCENE.$NAME.rotationAbs")[0].split(" ")
        # Place tile at the correct hight to make it fall.
        # Keep its absolute position and rotation intact.
        vpos = self.c.get("node.$SCENE.$NAME.position")[0].split(" ")
        pos = "{0} {1} {2}".format(vpos[0],
                                   vpos[1],
                                   float(vpold[2]) - float(vpnew[2]))
        self.c.set("node.$SCENE.$NAME.position", pos)
        vrot = self.c.get("node.$SCENE.$NAME.rotation")[0].split(" ")
        rot = "{0} {1} {2}".format(vrot[0],
                                   vrot[1],
                                   float(vrold[2]) - float(vrnew[2]))
        self.c.set("node.$SCENE.$NAME.rotation", rot)
        # Notify tile of its parent plate change.
        self.c.set("tile.$NAME.plate", FILTER_NAME)
        # Run fall action.
        self.c.set("$FALL.$SCENE.$NAME.active", "1")
        # Listen to fall finish.
        self.c.listen("$FALL.$SCENE.$NAME.active", "0", self.onFallFinish)
    def prepareRotation(self, slot):
        # The first call.
        if (self.rotationSpeed is None):
            point = self.c.get("$ROTATE.point")[0]
            v = point.split(" ")
            # Get rotation speed from the file.
            self.rotationSpeed = int(v[0])
        # Destination rotation = -30 - 120 * (slot - 1).
        point = "{0} 0 0 {1}".format(self.rotationSpeed,
                                     -30 - 120 * (slot - 1))
        self.c.set("$ROTATE.point", point)
    def setAcceptTile(self, key, value):
        tileName = value[0]
        for slot in self.tiles.keys():
            if (self.tiles[slot] is None):
                self.lastFreeSlot = slot
                break
        self.prepareRotation(self.lastFreeSlot)
        # Rotate filter.
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")
        # Prepare to take the node.
        self.tiles[self.lastFreeSlot] = tileName
        self.c.setConst("NAME", tileName)
    def setReset(self, key, value):
        # Create 1 filter tile.
        self.filterName = self.c.get("$TF.newTile")[0]
        # Change parent to the first tile leaf.
        self.c.setConst("NAME", self.filterName)
        self.c.set("node.$SCENE.$NAME.parent", FILTER_LEAF_NAME)
    def validateTiles(self):
        print "validate tiles"
        self.c.setConst("NAME", self.filterName)
        # Field ID -> [matching slot IDs].
        matches = {}
        fids = self.c.get("tile.$NAME.id")
        for slot in self.tiles.keys():
            tileName = self.tiles[slot]
            self.c.setConst("NAME", tileName)
            ids = self.c.get("tile.$NAME.id")
            for i in xrange(0, 2):
                for fi in xrange(0, 2):
                    #print "{0}:{1} {2} = {3}".format(slot, i, fi, ids[i] == fids[fi])
                    if (fi not in matches):
                        matches[fi] = []
                    # New match.
                    if ((ids[i] == fids[fi]) and
                        slot not in matches[fi]):
                        matches[fi].append(slot)
                        print "{0} -> {1}".format(fi, slot)
        # Slot = 1 in fi = 0, slot = 2 in fi = 1.
        ok1021 = ((FILTER_LEAF_SLOT1 in matches[0]) and
                  (FILTER_LEAF_SLOT2 in matches[1]))
        # Slot = 2 in fi = 0, slot = 1 in fi = 1.
        ok2011 = ((FILTER_LEAF_SLOT2 in matches[0]) and
                  (FILTER_LEAF_SLOT1 in matches[1]))
        if (ok1021 or ok2011):
            print "Match detected"
        else:
            print "No match"

class Filter(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Filter")
        self.impl = FilterImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.setConst("FALL",   FILTER_ACTION_FALL)
        self.c.setConst("ROTATE", FILTER_ACTION_ROTATE)
        self.c.setConst("TF",     FILTER_TILE_FACTORY)
        self.c.provide("filter.acceptTile", self.impl.setAcceptTile)
        self.c.provide("filter.reset",      self.impl.setReset)
        # Listen to rotation finish.
        self.c.listen("$ROTATE.$SCENE.$NODE.active", "0", self.impl.onRotationFinish)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Filter(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

