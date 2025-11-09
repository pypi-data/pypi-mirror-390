from .point import left, up
from ..entity_behaviour.animal import animal
from ..entity_behaviour.enemy import enemy
from .growth import grow
from ..left_click import recipe
from ...info import ATTRIBUTES, GROW_TILES, PROCESSING_TIME


def update_tile(
    current_tile,
    chunks,
    chunk,
    tile,
    tick,
    location,
    inventory_key,
    health,
    create_tile,
):
    attributes = ATTRIBUTES.get(current_tile["kind"], ())
    if current_tile["kind"] == "left":
        chunks = left(chunks, chunk, tile)
    elif current_tile["kind"] == "up":
        chunks = up(chunks, chunk, tile)
    elif "machine" in attributes:
        if tick % PROCESSING_TIME[current_tile["kind"]] == 0 and current_tile.get("recipe", -1) >= 0:
            if "inventory" not in current_tile:
                current_tile["inventory"] = {}
            if "drill" in attributes and "floor" in current_tile:
                if current_tile["floor"].split(" ")[-1] == "mineable":
                    current_tile["inventory"][current_tile["floor"]] = 1
            chunks[chunk][tile]["inventory"] = recipe(current_tile["kind"], current_tile["recipe"], current_tile["inventory"], (20, 64))
    elif current_tile["kind"] in GROW_TILES:
        chunks[chunk][tile] = grow(current_tile)
        if chunks[chunk][tile] == {}:
            del chunks[chunk][tile]
    if "animal" in attributes or "enemy" in attributes:
        player_distance_x = abs(chunk[0] * 16 + tile[0] - location[0] * 16 - location[2])
        player_distance_y = abs(chunk[1] * 16 + tile[1] - location[1] * 16 - location[3])
        player_distance = player_distance_x ** 2 + player_distance_y ** 2
        if "animal" in attributes:
            chunks, create_tile = animal(
                chunks,
                chunk,
                tile,
                current_tile,
                location,
                inventory_key,
                player_distance,
                create_tile,
            )
        else:
            chunks, health, create_tile = enemy(
                chunks,
                chunk,
                tile,
                current_tile,
                location,
                health,
                player_distance,
                create_tile,
            )
    return chunks, health, create_tile
