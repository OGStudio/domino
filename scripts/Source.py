
from pymjin2 import *

SOURCE_ACTION_ROTATE    = "rotate.default.rotateSource"
SOURCE_LEAF_NAME_PREFIX = "sourceLeaf"
SOURCE_NAME             = "source"
SOURCE_TILE             = "tile"
SOURCE_TILE_FACTORY     = "tileFactory"

class SourceImpl(object):
    def __init__(self, c):
        self.c = c
        self.rotationSpeed = None
        self.tiles = {}
    def __del__(self):
        self.c = None
    def createTile(self, slot):
        name = self.c.get("$TF.newTile")[0]
        # Change parent to corresponding tile leaf.
        self.c.setConst("NAME", name)
        parent = SOURCE_LEAF_NAME_PREFIX + str(slot)
        self.c.set("node.$SCENE.$NAME.parent",     parent)
        self.c.set("$TILE.$NAME.plate", SOURCE_NAME)
        # Each tile is in its designated slot.
        self.tiles[slot] = name
    def onPlate(self, key, value):
        tileName = key[1]
        self.c.setConst("NAME", tileName)
        # Tile has come to us.
        if (value[0] == SOURCE_NAME):
            self.c.set("node.$SCENE.$NAME.selectable", "1")
            self.c.listen("$TILE.$NAME.selected", "1", self.onTileSelection)
            return
        # Tile has left somebody. Find slot if us.
        tileSlot = None
        for slot, tile in self.tiles.items():
            if (tile == tileName):
                tileSlot = slot
                break
        if (tileSlot is None):
            return
        # Remove record.
        self.tiles[tileSlot] = None
        # Make unselectable.
        self.c.set("node.$SCENE.$NAME.selectable", "0")
        # Do not listen to it.
        self.c.unlisten("$TILE.$NAME.selected")
    def onRotation(self, key, value):
        self.c.report("source.moving", value[0])
    def onTileSelection(self, key, value):
        tileName = key[1]
        self.prepareRotation(tileName)
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")
        self.c.report("source.selectedTile", tileName)
    def prepareRotation(self, tileName):
        # The first call.
        if (self.rotationSpeed is None):
            point = self.c.get("$ROTATE.point")[0]
            v = point.split(" ")
            # Get rotation speed from the file.
            self.rotationSpeed = int(v[0])
        # Destination rotation = -90 - 60 * slot.
        for slot, tile in self.tiles.items():
            if (tile == tileName):
                point = "{0} 0 0 {1}".format(self.rotationSpeed,
                                             -90 - 60 * slot)
                self.c.set("$ROTATE.point", point)
    def setNewPair(self, key, value):
        print "newPair", key, value
        for slot, tile in self.tiles.items():
            if (tile is None):
                self.createTile(slot)
    def setReset(self, key, value):
        # Create 6 tiles.
        for slot in xrange(0, 6):
            self.createTile(slot)

class Source(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Source")
        self.impl = SourceImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.setConst("ROTATE", SOURCE_ACTION_ROTATE)
        self.c.setConst("TF",     SOURCE_TILE_FACTORY)
        self.c.setConst("TILE",   SOURCE_TILE)
        self.c.provide("source.moving")
        self.c.provide("source.newPair", self.impl.setNewPair)
        self.c.provide("source.reset",   self.impl.setReset)
        self.c.provide("source.selectedTile")
        # Listen to rotation.
        self.c.listen("$ROTATE.$SCENE.$NODE.active", None, self.impl.onRotation)
        # Listen to tile plate change.
        self.c.listen("$TILE..plate", None, self.impl.onPlate)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Source(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

