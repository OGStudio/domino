
from pymjin2 import *

class TileImpl(object):
    def __init__(self, c):
        self.c = c
    def __del__(self):
        self.c = None
    def setParent(self, key, value):
        print "setParent", key, value

class Tile(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Tile/" + nodeName)
        self.impl = TileImpl(self.c)
        self.c.setConst("SCENE", sceneName)
        self.c.setConst("NODE",  nodeName)
        #self.c.provide("tile.$NODE.parent", self.impl.setParent)
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

