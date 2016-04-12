
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
    def id(self):
        random.seed()
        i = random.randint(TILE_MATERIAL_MIN, TILE_MATERIAL_MAX)
        # TODO: provide 2 random numbers.
        return [str(i), str(i)]
    def newTile(self, key):
        name = self.tileName()
        id = self.id()
        material = "{0}{1}{2}".format(TILE_MATERIAL_PREFIX, id[0], id[1])
        self.c.setConst("NAME", name)
        self.c.set("node.$SCENE.$NAME.parent",   "ROOT")
        self.c.set("node.$SCENE.$NAME.model",    TILE_MODEL)
        self.c.set("node.$SCENE.$NAME.material", material)
        self.c.set("node.$SCENE.$NAME.script",   TILE_SCRIPT)
        self.c.set("tile.$NAME.id",              id)
        return [name]
    def tileName(self):
        self.lastTileID = self.lastTileID + 1
        return TILE_NAME_PREFIX + str(self.lastTileID)

class TileFactory(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "TileFactory")
        self.impl = TileFactoryImpl(self.c)
        self.c.setConst("SCENE", sceneName)
        self.c.setConst("NODE",  nodeName)
        self.c.provide("tileFactory.newTile", None, self.impl.newTile)
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

