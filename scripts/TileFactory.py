
from pymjin2 import *
import random

TILE_MODEL           = "models/tile.osgt"
TILE_MATERIAL_MIN    = 0
TILE_MATERIAL_MAX    = 3
TILE_MATERIAL_PREFIX = "tile"
TILE_NAME_PREFIX     = "tile"
TILE_SCRIPT          = "scripts/Tile.py"

class TileFactoryImpl(object):
    def __init__(self, c):
        self.c = c
        self.lastTileID = 0
    def __del__(self):
        self.c = None
    def materialName(self):
        random.seed()
        i = random.randint(TILE_MATERIAL_MIN, TILE_MATERIAL_MAX)
        return "{0}{1:02d}{2:02d}".format(TILE_MATERIAL_PREFIX, i, i)
    def tileName(self):
        self.lastTileID = self.lastTileID + 1
        return TILE_NAME_PREFIX + str(self.lastTileID)
    def getNewTile(self, key):
        name = self.tileName()
        material = self.materialName()
        self.c.setConst("TILE", name)
        self.c.set("node.$SCENE.$TILE.parent",   "ROOT")
        self.c.set("node.$SCENE.$TILE.model",    TILE_MODEL)
        self.c.set("node.$SCENE.$TILE.material", material)
        self.c.set("node.$SCENE.$TILE.script",   TILE_SCRIPT)
        return [name]

class TileFactory(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "TileFactory")
        self.impl = TileFactoryImpl(self.c)
        self.c.setConst("SCENE", sceneName)
        self.c.setConst("NODE",  nodeName)
        self.c.provide("tileFactory.newTile", None, self.impl.getNewTile)
    def __del__(self):
        # Tear down.
        self.c.clear()
        # Destroy.
        del self.impl
        del self.c

def SCRIPT_CREATE(sceneName, nodeName, env):
    return TileFactory(sceneName, nodeName, env)

def SCRIPT_DESTROY(instance):
    del instance

