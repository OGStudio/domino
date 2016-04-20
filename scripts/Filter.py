
from pymjin2 import *

FILTER_ACTION_DROP       = "move.default.dropTile"
FILTER_ACTION_ROTATE     = "rotate.default.rotateFilter"
FILTER_ACTION_TRANSITION = "move.default.transitionTile"
FILTER_LEAF_NAME         = "filterLeaf0"
FILTER_LEAF_NAME_PREFIX  = "filterLeaf"
FILTER_LEAF_SLOT1        = 1
FILTER_LEAF_SLOT2        = 2
FILTER_NAME              = "filter"
FILTER_TILE_FACTORY      = "tileFactory"

FILTER_SEQUENCE_ALIGN_TO_DST  = ["filter.prepareAlignRotation",
                                 "$ROTATE.$SCENE.$NODE.active"]
FILTER_SEQUENCE_MATCH_FAILURE = ["$DROP.$SCENE.$TILE1.active",
                                 "$DROP.$SCENE.$TILE2.active",
                                 "filter.deallocateDroppedTiles"]
FILTER_SEQUENCE_TILE_ACCEPT   = ["$ROTATE.$SCENE.$NODE.active",
                                 "filter.changeTileParent",
                                 "$TRANSITION.$SCENE.$TILE.active",
                                 "filter.matchTiles"]

class FilterImpl(object):
    def __init__(self, c):
        self.c = c
        self.filterName = None
        self.rotationSpeed = None
        self.tiles = { FILTER_LEAF_SLOT1 : None,
                       FILTER_LEAF_SLOT2 : None }
        self.lastFreeSlot = None
        self.lastSuccessfulSlot = FILTER_LEAF_SLOT1
        self.c.set("esequence.filter.alignToDestination.sequence",
                   FILTER_SEQUENCE_ALIGN_TO_DST)
        self.c.set("esequence.filter.matchFailure.sequence",
                   FILTER_SEQUENCE_MATCH_FAILURE)
        self.c.set("esequence.filter.acceptTile.sequence",
                   FILTER_SEQUENCE_TILE_ACCEPT)
    def __del__(self):
        self.c = None
    def prepareRotation(self, slot):
        # The first call.
        if (self.rotationSpeed is None):
            point = self.c.get("$ROTATE.point")[0]
            v = point.split(" ")
            # Get rotation speed from the file.
            self.rotationSpeed = int(v[0])
        # Destination rotation = -30 - 120 * (slot - 1).
        point = "{0} 0 0 {1}".format(self.rotationSpeed,
                                     -30 - 120 * (slot - 1))
        self.c.set("$ROTATE.point", point)
    def setAcceptTile(self, key, value):
        tileName = value[0]
        for slot in self.tiles.keys():
            if (self.tiles[slot] is None):
                self.lastFreeSlot = slot
                break
        self.tiles[self.lastFreeSlot] = tileName
        self.prepareRotation(self.lastFreeSlot)
        self.c.setConst("TILE", tileName)
        self.c.set("esequenceConst.filter.TILE.value", tileName)
        # Start accept sequence.
        self.c.set("esequence.filter.acceptTile.active", "1")
    def setChangeTileParent(self, key, value):
        # Record old absolute position and rotation.
        vpold = self.c.get("node.$SCENE.$TILE.positionAbs")[0].split(" ")
        vrold = self.c.get("node.$SCENE.$TILE.rotationAbs")[0].split(" ")
        # Change parent.
        parent = "{0}{1}".format(FILTER_LEAF_NAME_PREFIX, self.lastFreeSlot)
        self.c.set("node.$SCENE.$TILE.parent", parent)
        # Record new absolute position and rotation.
        vpnew = self.c.get("node.$SCENE.$TILE.positionAbs")[0].split(" ")
        vrnew = self.c.get("node.$SCENE.$TILE.rotationAbs")[0].split(" ")
        # Place tile at the correct hight to make it fall.
        # Keep its absolute position and rotation intact.
        vpos = self.c.get("node.$SCENE.$TILE.position")[0].split(" ")
        pos = "{0} {1} {2}".format(vpos[0],
                                   vpos[1],
                                   float(vpold[2]) - float(vpnew[2]))
        self.c.set("node.$SCENE.$TILE.position", pos)
        vrot = self.c.get("node.$SCENE.$TILE.rotation")[0].split(" ")
        rot = "{0} {1} {2}".format(vrot[0],
                                   vrot[1],
                                   float(vrold[2]) - float(vrnew[2]))
        self.c.set("node.$SCENE.$TILE.rotation", rot)
        # Notify tile of its parent plate change.
        self.c.set("tile.$TILE.plate", FILTER_NAME)
        # Report method finish.
        self.c.report("filter.changeTileParent", "0")
    def setDeallocateDroppedTiles(self, key, value):
        # Deallocate tiles.
        for slot in self.tiles.keys():
            tileName = self.tiles[slot]
            self.tiles[slot] = None
            self.c.setConst("TILE", tileName)
            self.c.set("node.$SCENE.$TILE.parent", "")
        # Report method finish.
        self.c.report("filter.deallocateDroppedTiles", "0")
        # Report match failure.
        self.c.report("filter.match", "0")
    def setMatchTiles(self, key, value):
        # Report method finish.
        self.c.report("filter.matchTiles", "0")
        if (self.lastFreeSlot == FILTER_LEAF_SLOT2):
            self.validateTiles()
    def setPrepareAlignRotation(self, key, value):
        # 1 -> 2.
        if (self.lastSuccessfulSlot == FILTER_LEAF_SLOT1):
            self.lastSuccessfulSlot = FILTER_LEAF_SLOT2
        # 2 -> 1. Prepare for the next round.
        else:
            self.lastSuccessfulSlot = FILTER_LEAF_SLOT1
        slot = self.lastSuccessfulSlot
        # Destination rotation = 30 + 120 * (slot - 1).
        point = "{0} 0 0 {1}".format(self.rotationSpeed,
                                     30 + 120 * (slot - 1))
        self.c.set("$ROTATE.point", point)
        # Report method finish.
        self.c.report("filter.prepareAlignRotation", "0")
    def setReset(self, key, value):
        # Create 1 filter tile.
        self.filterName = self.c.get("$TF.newTile")[0]
        # Change parent to the first tile leaf.
        self.c.setConst("NAME", self.filterName)
        self.c.set("node.$SCENE.$NAME.parent", FILTER_LEAF_NAME)
    def validateTiles(self):
        self.c.setConst("NAME", self.filterName)
        # Field ID -> [matching slot IDs].
        matches = {}
        fids = self.c.get("tile.$NAME.id")
        for slot in self.tiles.keys():
            tileName = self.tiles[slot]
            self.c.setConst("NAME", tileName)
            ids = self.c.get("tile.$NAME.id")
            for i in xrange(0, 2):
                for fi in xrange(0, 2):
                    #print "{0}:{1} {2} = {3}".format(slot, i, fi, ids[i] == fids[fi])
                    if (fi not in matches):
                        matches[fi] = []
                    # New match.
                    if ((ids[i] == fids[fi]) and
                        slot not in matches[fi]):
                        matches[fi].append(slot)
                        print "{0} -> {1}".format(fi, slot)
        # Slot = 1 in fi = 0, slot = 2 in fi = 1.
        ok1021 = ((FILTER_LEAF_SLOT1 in matches[0]) and
                  (FILTER_LEAF_SLOT2 in matches[1]))
        # Slot = 2 in fi = 0, slot = 1 in fi = 1.
        ok2011 = ((FILTER_LEAF_SLOT2 in matches[0]) and
                  (FILTER_LEAF_SLOT1 in matches[1]))
        self.lastFreeSlot = None
        if (ok1021 or ok2011):
            self.c.report("filter.match", "1")
        else:
            self.c.set("esequenceConst.filter.TILE1.value", self.tiles[1])
            self.c.set("esequenceConst.filter.TILE2.value", self.tiles[2])
            # Start failure sequence.
            # Report filter.match only at the sequence end.
            self.c.set("esequence.filter.matchFailure.active", "1")

class Filter(object):
    def __init__(self, sceneName, nodeName, env):
        self.c = EnvironmentClient(env, "Filter")
        self.impl = FilterImpl(self.c)
        self.c.setConst("SCENE",      sceneName)
        self.c.setConst("NODE",       nodeName)
        self.c.setConst("DROP",       FILTER_ACTION_DROP)
        self.c.setConst("ROTATE",     FILTER_ACTION_ROTATE)
        self.c.setConst("TRANSITION", FILTER_ACTION_TRANSITION)
        self.c.setConst("TF",         FILTER_TILE_FACTORY)
        # Sequence constants.
        self.c.set("esequenceConst.filter.DROP.value", FILTER_ACTION_DROP)
        self.c.set("esequenceConst.filter.SCENE.value", sceneName)
        self.c.set("esequenceConst.filter.ROTATE.value",
                   FILTER_ACTION_ROTATE)
        self.c.set("esequenceConst.filter.TRANSITION.value",
                   FILTER_ACTION_TRANSITION)
        self.c.set("esequenceConst.filter.SCENE.value",   sceneName)
        self.c.set("esequenceConst.filter.NODE.value",    nodeName)
        # Public API.
        self.c.provide("filter.acceptTile", self.impl.setAcceptTile)
        self.c.provide("filter.match")
        self.c.provide("filter.reset",      self.impl.setReset)
        # Private API.
        self.c.provide("filter.changeTileParent", self.impl.setChangeTileParent)
        self.c.provide("filter.deallocateDroppedTiles",
                       self.impl.setDeallocateDroppedTiles)
        self.c.provide("filter.matchTiles", self.impl.setMatchTiles)
        self.c.provide("filter.prepareAlignRotation",
                       self.impl.setPrepareAlignRotation)
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

