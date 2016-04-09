
from pymjin2 import *

SOURCE_LEAF_NAME_PREFIX = "sourceLeaf"
SOURCE_TILE_FACTORY     = "tileFactory"

class SourceImpl(object):
    def __init__(self, c):
        self.c = c
        self.tiles = []
    def __del__(self):
        self.c = None
    def setReset(self, key, value):
        # Create 6 tiles.
        for i in xrange(1, 7):
            name = self.c.get("$TF.newTile")[0]
            # Change parent to corresponding tile leaf.
            self.c.setConst("TILE", name)
            parent = SOURCE_LEAF_NAME_PREFIX + str(i)
            self.c.set("node.$SCENE.$TILE.parent", parent)
            self.tiles.append(name)

class Source(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Source")
        self.impl = SourceImpl(self.c)
        self.c.setConst("SCENE", sceneName)
        self.c.setConst("NODE",  nodeName)
        self.c.setConst("TF",    SOURCE_TILE_FACTORY)
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

