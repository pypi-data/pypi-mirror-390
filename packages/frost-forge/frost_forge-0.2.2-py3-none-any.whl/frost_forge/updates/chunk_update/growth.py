from random import random

from ...info import GROW_TIME, GROW_TILES, GROW_REQUIREMENT, SOIL_STRENGTH


def grow(tile, guarantee=False):
    if "kind" in tile:
        old_kind = tile["kind"]
        grow_floor = False
    else:
        old_kind = tile["floor"]
        grow_floor = True
    if random() < SOIL_STRENGTH.get(tile.get("floor"), 1) / (GROW_TIME[old_kind] * 6) or guarantee:
        if GROW_REQUIREMENT.get(old_kind, 1) <= SOIL_STRENGTH.get(tile.get("floor"), 1):
            for info in GROW_TILES[old_kind]:
                tile[info] = GROW_TILES[old_kind][info]
            if "inventory" in GROW_TILES[old_kind]:
                tile["inventory"] = {}
                for item in GROW_TILES[old_kind]["inventory"]:
                    tile["inventory"][item] = GROW_TILES[old_kind]["inventory"][item]
    if grow_floor and "kind" in tile:
        del tile["floor"]
    return tile
