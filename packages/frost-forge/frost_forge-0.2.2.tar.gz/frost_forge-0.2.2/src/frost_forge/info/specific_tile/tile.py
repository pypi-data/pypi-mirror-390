from ..render import FPS


FLOOR = {
    "brick floor",
    "coal mineable",
    "copper brick floor",
    "copper door",
    "copper door open",
    "copper mineable",
    "copper pit",
    "dirt",
    "ice",
    "log floor",
    "moist dirt",
    "mushroom door",
    "mushroom door open",
    "mushroom floor",
    "pebble",
    "rail 0",
    "rail 1",
    "rail 2",
    "rail 3",
    "rail 4",
    "rail 5",
    "sand",
    "slime door",
    "slime door open",
    "slime floor",
    "stone brick floor",
    "stone floor",
    "void",
    "water",
    "wood door",
    "wood door open",
    "wood floor",
}
FLOOR_TYPE = {
    "copper pit": "fluid",
    "ice": "block",
    "void": "block",
    "water": "fluid",
}
SOIL_STRENGTH = {
    "dirt": 1,
    "moist dirt": 1.25,
}
GROW_TIME = {
    "bluebell": 400,
    "carrot": 160,
    "copper pit": 600,
    "copper sapling": 300,
    "copper treeling": 500,
    "water": 60,
    "potato": 240,
    "rabbit child": 200,
    "sapling": 80,
    "spore": 120,
    "slime summon": 40,
    "tin sapling": 400,
    "tin treeling": 600,
    "treeling": 100,
}
GROW_TILES = {
    "bluebell": {"kind": "bluebell grown", "inventory": {"bluebell": 2}},
    "carrot": {"kind": "carrot grown", "inventory": {"carrot": 2}},
    "copper pit": {"kind": "copper pit grown", "inventory": {"copper ingot": 1}},
    "copper sapling": {"kind": "copper treeling", "inventory": {"raw copper": 1, "copper sapling": 1, "log": 1}},
    "copper treeling": {"kind": "copper tree", "inventory": {"raw copper": 2, "copper ingot": 1, "copper sapling": 1, "log": 2}},
    "water": {"floor": "ice"},
    "potato": {"kind": "potato grown", "inventory": {"potato": 2}},
    "rabbit child": {
        "kind": "rabbit adult",
        "inventory": {"rabbit fur": 1, "rabbit meat": 1},
    },
    "sapling": {"kind": "treeling", "inventory": {"sapling": 1, "log": 1}},
    "slime summon": {"kind": "slime prince", "inventory": {"slife crystal": 1, "slime shaper": 1}},
    "spore": {"kind": "mushroom", "inventory": {"spore": 2}},
    "tin sapling": {"kind": "tin treeling", "inventory": {"raw tin": 1, "tin sapling": 1, "log": 1}},
    "tin treeling": {"kind": "tin tree", "inventory": {"raw tin": 2, "tin ingot": 1, "tin sapling": 1, "log": 2}},
    "treeling": {"kind": "tree", "inventory": {"sapling": 2, "log": 2}},
}
GROW_REQUIREMENT = {
    "bluebell": 1.25,
    "copper treeling": 1.25,
    "tin sapling": 1.25,
    "tin treeling": 1.4,
}
GROW_DIRT_IGNORE = {
    "rabbit child",
    "slime summon",
}
MULTI_TILES = {
    "copper boiler": (3, 2),
    "copper constructor": (2, 2),
    "furnace": (2, 2),
    "manual press": (2, 1),
    "masonry bench": (2, 1),
    "obelisk": (1, 2),
    "sawbench": (2, 1),
    "sewbench": (2, 1),
    "wooden bed": (1, 2),
}
PROCESSING_TIME = {
    "burner drill": 30 * FPS,
    "composter": 2 * FPS,
    "copper boiler": 5 * FPS,
    "copper constructor": 15 * FPS,
    "copper press": 20 * FPS,
    "furnace": 10 * FPS,
    "void convertor": 20 * FPS,
    "wood crucible": 60 * FPS,
    "wooden sieve": 15 * FPS,
}
STORAGE = {
    "small barrel": (1, 512),
    "small crate": (8, 64),
    "void crate": (8, 64),
}
UNBREAK = {
    "coal mineable",
    "copper mineable",
    "copper pit",
    "glass lock",
    "left",
    "obelisk",
    "player",
    "slime summon",
    "up",
    "void",
    "void convertor",
    "void crate",
}
MODIFICATIONS = {"rail": 6}