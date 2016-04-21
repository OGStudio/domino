
from pymjin2 import *

DESTINATION_ACTION_ROTATE        = "rotate.default.rotateDestination"
DESTINATION_LEAF_NAME_PREFIX     = "destinationLeaf"
DESTINATION_LEAFS_NB             = 10
DESTINATION_NAME                 = "destination"
DESTINATION_SEQUENCE_TILE_ACCEPT = ["destination.findFreeSlot",
                                    "$DST_ROTATE.$SCENE.$DST_NODE.active"]
#                                    "destination.changeTileParent",
#                                    "$DST_TRANSITION.$SCENE.$TILE.active"]

class DestinationImpl(object):
    def __init__(self, c):
        self.c = c
        self.rotationSpeed = None
        self.tiles = {}
        for slot in xrange(0, DESTINATION_LEAFS_NB):
            self.tiles[slot] = None
        self.c.set("esequence.destination.acceptTile.sequence",
                   DESTINATION_SEQUENCE_TILE_ACCEPT)
        self.lastFreeSlot = None
    def __del__(self):
        self.c = None
#    def onPlate(self, key, value):
#        print "destination.onPlate", key, value
#        tileName = key[1]
#        self.c.setConst("NAME", tileName)
#        # Tile has come to us.
#        if (value[0] == SOURCE_NAME):
#            self.c.set("node.$SCENE.$NAME.selectable", "1")
#            self.c.listen("$TILE.$NAME.selected", "1", self.onTileSelection)
#            return
#        # Tile has left somebody. Find slot if us.
#        tileSlot = None
#        for slot, tile in self.tiles.items():
#            if (tile == tileName):
#                tileSlot = slot
#                break
#        if (tileSlot is None):
#            return
#        # Remove record.
#        self.tiles[tileSlot] = None
#        # Make unselectable.
#        self.c.set("node.$SCENE.$NAME.selectable", "0")
#        # Do not listen to it.
#        self.c.unlisten("$TILE.$NAME.selected")
    def setFindFreeSlot(self, key, value):
        print "findFreeSlot"
        for slot in self.tiles.keys():
            # Free slot.
            if (self.tiles[slot] is None):
                self.lastFreeSlot = slot
                break
        self.prepareAlignRotation(self.lastFreeSlot)
        # Report method finish.
        self.c.report("destination.findFreeSlot", "0")
#    def onRotation(self, key, value):
#        self.c.report("source.moving", value[0])
    def prepareAlignRotation(self, slot):
        # The first call.
        if (self.rotationSpeed is None):
            point = self.c.get("$ROTATE.point")[0]
            v = point.split(" ")
            # Get rotation speed from the file.
            self.rotationSpeed = int(v[0])
        # slot 0: 90
        # slot 1: 126
        # Destination rotation = 90 + 36 * slot.
        point = "{0} 0 0 {1}".format(self.rotationSpeed,
                                     90 + 36 * self.lastFreeSlot)
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
        # Public API.
        # Private API.
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

