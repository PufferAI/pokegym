from pdb import set_trace as T
import numpy as np
import json


MAP_PATH = __file__.rstrip('game_map.py') + 'map_data.json'

MAP_DATA = json.load(open(MAP_PATH, 'r'))['regions']
MAP_DATA = {int(e['id']): e for e in MAP_DATA}

# Handle KeyErrors
def local_to_global(r, c, map_n):
    try:
        map_x, map_y,= MAP_DATA[map_n]['coordinates']
        return r + map_y, c + map_x
    except KeyError:
        print(f'Map id {map_n} not found in map_data.json.')
        return r + 0, c + 0