
from pymjin2 import *

SOURCE_ACTION_ROTATE    = "rotate.default.rotateSource"
SOURCE_LEAF_NAME_PREFIX = "sourceLeaf"
SOURCE_NAME             = "source"
SOURCE_TILE             = "tile"
SOURCE_TILE_FACTORY     = "tileFactory"

class SourceImpl(object):
    def __init__(self, c):
        self.c = c
        self.tiles = []
    def __del__(self):
        self.c = None
    def onTileSelection(self, key, value):
        print "onTileSelection", key, value
        self.c.set("$ROTATE.$SCENE.$NODE.active", "1")
    def setReset(self, key, value):
        # Create 6 tiles.
        for i in xrange(1, 7):
            name = self.c.get("$TF.newTile")[0]
            # Change parent to corresponding tile leaf.
            self.c.setConst("NAME", name)
            parent = SOURCE_LEAF_NAME_PREFIX + str(i)
            self.c.set("node.$SCENE.$NAME.parent",     parent)
            self.c.set("node.$SCENE.$NAME.selectable", "1")
            self.c.set("$TILE.$NAME.plate",            SOURCE_NAME)
            self.tiles.append(name)
            # Listen to tile selection.
            self.c.listen("$TILE.$NAME.selected", "1", self.onTileSelection)

class Source(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Source")
        self.impl = SourceImpl(self.c)
        self.c.setConst("SCENE",  sceneName)
        self.c.setConst("NODE",   nodeName)
        self.c.setConst("ROTATE", SOURCE_ACTION_ROTATE)
        self.c.setConst("TF",     SOURCE_TILE_FACTORY)
        self.c.setConst("TILE",   SOURCE_TILE)
        self.c.provide("source.reset", self.impl.setReset)
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

