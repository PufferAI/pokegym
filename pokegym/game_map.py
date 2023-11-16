import numpy as np

MAP_COORDS = {
    0: {"name": "Pallet Town", "coordinates": np.array([70, 7])},
    1: {"name": "Viridian City", "coordinates": np.array([60, 79])},
    2: {"name": "Pewter City", "coordinates": np.array([60, 187])},
    3: {"name": "Cerulean City", "coordinates": np.array([240, 205])},
    62: {"name": "Invaded house (Cerulean City)", "coordinates": np.array([290, 227])},
    63: {"name": "trade house (Cerulean City)", "coordinates": np.array([290, 212])},
    64: {"name": "Pokémon Center (Cerulean City)", "coordinates": np.array([290, 197])},
    65: {"name": "Pokémon Gym (Cerulean City)", "coordinates": np.array([290, 182])},
    66: {"name": "Bike Shop (Cerulean City)", "coordinates": np.array([290, 167])},
    67: {"name": "Poké Mart (Cerulean City)", "coordinates": np.array([290, 152])},
    35: {"name": "Route 24", "coordinates": np.array([250, 235])},
    36: {"name": "Route 25", "coordinates": np.array([270, 267])},
    12: {"name": "Route 1", "coordinates": np.array([70, 43])},
    13: {"name": "Route 2", "coordinates": np.array([70, 151])},
    14: {"name": "Route 3", "coordinates": np.array([100, 179])},
    15: {"name": "Route 4", "coordinates": np.array([150, 197])},
    33: {"name": "Route 22", "coordinates": np.array([20, 71])},
    37: {"name": "Red house first", "coordinates": np.array([61, 9])},
    38: {"name": "Red house second", "coordinates": np.array([61, 0])},
    39: {"name": "Blues house", "coordinates": np.array([91, 9])},
    40: {"name": "oaks lab", "coordinates": np.array([91, 1])},
    41: {"name": "Pokémon Center (Viridian City)", "coordinates": np.array([100, 54])},
    42: {"name": "Poké Mart (Viridian City)", "coordinates": np.array([100, 62])},
    43: {"name": "School (Viridian City)", "coordinates": np.array([100, 79])},
    44: {"name": "House 1 (Viridian City)", "coordinates": np.array([100, 71])},
    47: {"name": "Gate (Viridian City/Pewter City) (Route 2)", "coordinates": np.array([91,143])},
    49: {"name": "Gate (Route 2)", "coordinates": np.array([91,115])},
    50: {"name": "Gate (Route 2/Viridian Forest) (Route 2)", "coordinates": np.array([91,115])},
    51: {"name": "viridian forest", "coordinates": np.array([35, 144])},
    52: {"name": "Pewter Museum (floor 1)", "coordinates": np.array([60, 196])},
    53: {"name": "Pewter Museum (floor 2)", "coordinates": np.array([60, 205])},
    54: {"name": "Pokémon Gym (Pewter City)", "coordinates": np.array([49, 176])},
    55: {"name": "House with disobedient Nidoran♂ (Pewter City)", "coordinates": np.array([51, 184])},
    56: {"name": "Poké Mart (Pewter City)", "coordinates": np.array([40, 170])},
    57: {"name": "House with two Trainers (Pewter City)", "coordinates": np.array([51, 184])},
    58: {"name": "Pokémon Center (Pewter City)", "coordinates": np.array([45, 161])},
    59: {"name": "Mt. Moon (Route 3 entrance)", "coordinates": np.array([153, 234])},
    60: {"name": "Mt. Moon Corridors", "coordinates": np.array([168, 253])},
    61: {"name": "Mt. Moon Level 2", "coordinates": np.array([197, 253])},
    68: {"name": "Pokémon Center (Route 3)", "coordinates": np.array([135, 197])},
    193: {"name": "Badges check gate (Route 22)", "coordinates": np.array([0, 87])}, # TODO this coord is guessed, needs to be updated
    230: {"name": "Badge Man House (Cerulean City)", "coordinates": np.array([290, 137])}
}

def local_to_global(x, y, map_n):
    map_x, map_y = MAP_COORDS[map_n]["coordinates"]
    return x + map_x, y + (375 - map_y)

