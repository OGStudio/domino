
from pymjin2 import *

FILTER_ACTION_ROTATE    = "rotate.default.rotateFilter"
FILTER_LEAF_NAME        = "filterLeaf0"
FILTER_LEAF_NAME_PREFIX = "filterLeaf"
FILTER_LEAF_SLOT_MIN    = 1
FILTER_LEAF_SLOT_MAX    = 2
FILTER_NAME             = "filter"
FILTER_TILE_FACTORY     = "tileFactory"

class FilterImpl(object):
    def __init__(self, c):
        self.c = c
        self.filterName = None
        self.rotationSpeed = None
        self.tiles = {}
        for i in xrange(FILTER_LEAF_SLOT_MIN, FILTER_LEAF_SLOT_MAX + 1):
            self.tiles[i] = None
    def __del__(self):
        self.c = None
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
        print "acceptTile", key, value
        tileName = value[0]
        freeSlot = None
        for slot in self.tiles.keys():
            if (self.tiles[slot] is None):
                freeSlot = slot
                break
        # TODO: Validate tiles.
        if (freeSlot == FILTER_LEAF_SLOT_MAX):
            pass
        self.prepareRotation(freeSlot)
        # Rotate filter.
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")
        # TODO: Do it after rotation finish.
        # Take node.
        self.tiles[freeSlot] = tileName
        self.c.setConst("NAME", tileName)
        # TODO: add fall action.
        parent = "{0}{1}".format(FILTER_LEAF_NAME_PREFIX, freeSlot)
        self.c.set("node.$SCENE.$NAME.parent", parent)
        self.c.set("tile.$NAME.plate", FILTER_NAME)
    def setReset(self, key, value):
        # Create 1 filter tile.
        self.filterName = self.c.get("$TF.newTile")[0]
        # Change parent to the first tile leaf.
        self.c.setConst("TILE", self.filterName)
        self.c.set("node.$SCENE.$TILE.parent", FILTER_LEAF_NAME)

class Filter(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Filter")
        self.impl = FilterImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.setConst("ROTATE", FILTER_ACTION_ROTATE)
        self.c.setConst("TF",     FILTER_TILE_FACTORY)
        self.c.provide("filter.acceptTile", self.impl.setAcceptTile)
        self.c.provide("filter.reset",      self.impl.setReset)
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

