
from pymjin2 import *

DESTINATION_ACTION_ROTATE        = "rotate.default.rotateDestination"
DESTINATION_ACTION_TRANSITION    = "move.default.transitionTile"
DESTINATION_LEAF_NAME_PREFIX     = "destinationLeaf"
DESTINATION_LEAFS_NB             = 10
DESTINATION_NAME                 = "destination"
DESTINATION_SEQUENCE_TILE_ACCEPT = ["destination.findFreeSlot",
                                    "$DST_ROTATE.$SCENE.$DST_NODE.active",
                                    "destination.changeTileParent",
                                    "$DST_TRANSITION.$SCENE.$TILE.active"]

class DestinationImpl(object):
    def __init__(self, c):
        self.c = c
        self.rotationSpeed = None
        self.tiles = {}
        for slot in xrange(0, DESTINATION_LEAFS_NB):
            print "dst tile slot {0} set to None".format(slot)
            self.tiles[slot] = None
        self.c.set("esequence.destination.acceptTile.sequence",
                   DESTINATION_SEQUENCE_TILE_ACCEPT)
        self.lastFreeSlot = None
    def __del__(self):
        self.c = None
    def setChangeTileParent(self, key, value):
        # Change parent and keep absolute orientation intact.
        parent = "{0}{1}".format(DESTINATION_LEAF_NAME_PREFIX, self.lastFreeSlot)
        self.c.set("node.$SCENE.$TILE.parentAbs", parent)
        # Notify tile of its parent plate change.
        self.c.set("tile.$TILE.plate", DESTINATION_NAME)
        # Report method finish.
        self.c.report("destination.changeTileParent", "0")
    def setFindFreeSlot(self, key, value):
        print "find free slot"
        for slot in self.tiles.keys():
            print "checking slot", slot
            # Free slot.
            if (self.tiles[slot] is None):
                self.lastFreeSlot = slot
                break
        print "dst last free slot", slot
        tileName = self.c.get("esequenceConst.TILE.value")[0]
        self.c.setConst("TILE", tileName)
        self.tiles[slot] = tileName
        self.prepareAlignRotation(self.lastFreeSlot)
        # Report method finish.
        self.c.report("destination.findFreeSlot", "0")
    def prepareAlignRotation(self, slot):
        # The first call.
        if (self.rotationSpeed is None):
            point = self.c.get("$ROTATE.point")[0]
            v = point.split(" ")
            # Get rotation speed from the file.
            self.rotationSpeed = int(v[0])
        # Destination rotation = 90 - 36 * slot.
        point = "{0} 0 0 {1}".format(self.rotationSpeed,
                                     90 - 36 * slot)
        self.c.set("$ROTATE.point", point)

class Destination(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Destination")
        self.impl = DestinationImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.setConst("ROTATE", DESTINATION_ACTION_ROTATE)
        # Sequence constants.
        self.c.set("esequenceConst.DST_NODE.value",   nodeName)
        self.c.set("esequenceConst.DST_ROTATE.value", DESTINATION_ACTION_ROTATE)
        self.c.set("esequenceConst.DST_TRANSITION.value",
                   DESTINATION_ACTION_TRANSITION)
        # Public API.
        # Private API.
        self.c.provide("destination.changeTileParent",
                       self.impl.setChangeTileParent)
        self.c.provide("destination.findFreeSlot", self.impl.setFindFreeSlot)
        # Listen to tile plate change.
        #self.c.listen("$TILE..plate", None, self.impl.onPlate)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Destination(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

