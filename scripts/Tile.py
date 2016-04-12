
from pymjin2 import *

class TileImpl(object):
    def __init__(self, c):
        self.c = c
        self.id = None
    def __del__(self):
        self.c = None
    def getID(self, key):
        return self.id
    def onSelection(self, key, value):
        self.c.report("tile.$NODE.selected", value[0])
    def setID(self, key, value):
        self.id = value
    def setPlate(self, key, value):
        pass
        #self.c.setConst("PLATE", value[0])

class Tile(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Tile/" + nodeName)
        self.impl = TileImpl(self.c)
        self.c.setConst("SCENE", sceneName)
        self.c.setConst("NODE",  nodeName)
        self.c.provide("tile.$NODE.id", self.impl.setID, self.impl.getID)
        self.c.provide("tile.$NODE.plate", self.impl.setPlate)
        self.c.provide("tile.$NODE.selected")
        # Listen to this node selection.
        self.c.listen("node.$SCENE.$NODE.selected", "1", self.impl.onSelection)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Tile(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

