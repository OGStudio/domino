
from pymjin2 import *

MAIN_SOURCE_NAME = "source"
MAIN_SOUND_START = "soundBuffer.default.start"

class MainImpl(object):
    def __init__(self, c):
        self.c = c
        self.isStarted = False
        self.sourceTile = None
    def __del__(self):
        self.c = None
    def onSourceStopped(self, key, value):
        self.c.set("filter.acceptTile", self.sourceTile)
    def onSourceTile(self, key, value):
        self.sourceTile = value[0]
    def onStart(self, key, value):
        if (self.isStarted):
            return
        self.isStarted = True
        print "Start the game"
        self.c.set("$SNDSTART.state", "play")
        self.c.set("filter.reset", "1")
        self.c.set("source.reset", "1")

class Main(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Main")
        self.impl = MainImpl(self.c)
        self.c.setConst("SCENE",    sceneName)
        self.c.setConst("SOURCE",   MAIN_SOURCE_NAME)
        self.c.setConst("SNDSTART", MAIN_SOUND_START)
        self.c.listen("input.SPACE.key",     "1",  self.impl.onStart)
        self.c.listen("source.moving",       "0",  self.impl.onSourceStopped)
        self.c.listen("source.selectedTile", None, self.impl.onSourceTile)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return Main(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

