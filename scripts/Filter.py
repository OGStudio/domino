
from pymjin2 import *

FILTER_LEAF_NAME        = "filterLeaf1"
FILTER_LEAF_NAME_PREFIX = "filterLeaf"
FILTER_TILE_FACTORY     = "tileFactory"

class FilterImpl(object):
    def __init__(self, c):
        self.c = c
        self.filterName = None
    def __del__(self):
        self.c = None
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
        self.c.setConst("SCENE", sceneName)
        self.c.setConst("NODE",  nodeName)
        self.c.setConst("TF",    FILTER_TILE_FACTORY)
        self.c.provide("filter.reset", self.impl.setReset)
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

