# addresses from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map
# https://github.com/pret/pokered/blob/91dc3c9f9c8fd529bb6e8307b58b96efa0bec67e/constants/event_constants.asm
from pokegym import data


HP_ADDR = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248]
MAX_HP_ADDR = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269]
PARTY_SIZE_ADDR = 0xD163
PARTY_ADDR = [0xD164, 0xD165, 0xD166, 0xD167, 0xD168, 0xD169]
PARTY_LEVEL_ADDR = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]
POKE_XP_ADDR = [0xD179, 0xD1A5, 0xD1D1, 0xD1FD, 0xD229, 0xD255]
CAUGHT_POKE_ADDR = range(0xD2F7, 0xD309)
SEEN_POKE_ADDR = range(0xD30A, 0xD31D)
OPPONENT_LEVEL_ADDR = [0xD8C5, 0xD8F1, 0xD91D, 0xD949, 0xD975, 0xD9A1]
X_POS_ADDR = 0xD362
Y_POS_ADDR = 0xD361
MAP_N_ADDR = 0xD35E
BADGE_1_ADDR = 0xD356
OAK_PARCEL_ADDR = 0xD74E
OAK_POKEDEX_ADDR = 0xD74B
OPPONENT_LEVEL = 0xCFF3
ENEMY_POKE_COUNT = 0xD89C
EVENT_FLAGS_START_ADDR = 0xD747
EVENT_FLAGS_END_ADDR = 0xD886 # 0xD761
MUSEUM_TICKET_ADDR = 0xD754
USED_CELL_SEPARATOR_ADDR = 0xD7F2
MONEY_ADDR_1 = 0xD347
MONEY_ADDR_100 = 0xD348
MONEY_ADDR_10000 = 0xD349
# MAP_TEXT_POINTER_TABLE_NPC = 0xD36C - 0xD36D 
TEXT_BOX_ARROW_BLINK = 0xC4F2
BATTLE_FLAG = 0xD057
SS_ANNE = 0xD803
IF_FONT_IS_LOADED = 0xCFC4 # text box is up
# get information for player
PLAYER_DIRECTION = 0xC109
PLAYER_Y = 0xC104
PLAYER_X = 0xC106
WNUMSPRITES = 0xD4E1
WNUMSIGNS = 0xD4B0

# Moves 1-4 for Poke1, Poke2, Poke3, Poke4, Poke5, Poke6
MOVE1 = [0xD173, 0xD19F, 0xD1CB, 0xD1F7, 0xD223, 0xD24F]
MOVE2 = [0xD174, 0xD1A0, 0xD1CC, 0xD1F8, 0xD224, 0xD250]
MOVE3 = [0xD175, 0xD1A1, 0xD1CD, 0xD1F9, 0xD225, 0xD251]
MOVE4 = [0xD176, 0xD1A2, 0xD1CE, 0xD1FA, 0xD226, 0xD252]
POKE = [0xD16B, 0xD197, 0xD1C3, 0xD1EF, 0xD21B, 0xD247] # - Pokémon (Again)
STATUS = [0xD16F, 0xD19B, 0xD1C7, 0xD1F3, 0xD21F, 0xD24B] # - Status (Poisoned, Paralyzed, etc.)
TYPE1 = [0xD170, 0xD19C, 0xD1C8, 0xD1F4, 0xD220, 0xD24C] # - Type 1
TYPE2 = [0xD171, 0xD19D, 0xD1C9, 0xD1F5, 0xD221, 0xD24D] # - Type 2
LEVEL = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268] # - Level (actual level)
MAXHP = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269] # - Max HP if = 01 + 256 to MAXHP2 value
CHP = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248] # - Current HP if = 01 + 256


def bcd(num):
    return 10 * ((num >> 4) & 0x0F) + (num & 0x0F)

def bit_count(bits):
    return bin(bits).count("1")

def read_bit(game, addr, bit) -> bool:
    # add padding so zero will read '0b100000000' instead of '0b0'
    return bin(256 + game.get_memory_value(addr))[-bit - 1] == "1"

def mem_val(game, addr):
    mem = game.get_memory_value(addr)
    return mem

def read_uint16(game, start_addr):
    """Read 2 bytes"""
    val_256 = game.get_memory_value(start_addr)
    val_1 = game.get_memory_value(start_addr + 1)
    return 256 * val_256 + val_1

def pokemon(game):
    # Get memory values from the list POKE and LEVEL
    memory_values = [game.get_memory_value(a) for a in POKE]
    levels = [game.get_memory_value(a) for a in LEVEL]

    # Use memory values to get corresponding names from pokemon_data
    names = [entry['name'] for entry in data.pokemon_data if entry.get('decimal') and int(entry['decimal']) in memory_values]

    # Create an initial dictionary with names as keys and levels as values
    party_dict = dict(zip(names, levels))

    return party_dict

def update_pokemon_level(pokemon_dict, pokemon_name, new_level):
    if pokemon_name in pokemon_dict:
        # Update the level for the specified Pokémon
        pokemon_dict[pokemon_name] = new_level
    else:
        # Add a new entry for the Pokémon
        pokemon_dict[pokemon_name] = new_level

def get_hm_count(game):
    hm_ids = [0xC4, 0xC5, 0xC6, 0xC7, 0xC8]
    items = get_items_in_bag()
    total_hm_cnt = 0
    for hm_id in hm_ids:
        if hm_id in items:
            total_hm_cnt += 1
    return total_hm_cnt

def get_items_in_bag(game, one_indexed=0):
    first_item = 0xD31E
    item_names = []
    for i in range(0, 20, 2):
        item_id = game.get_memory_value(first_item + i)
        if item_id == 0 or item_id == 0xff:
            break
        item_id_key = item_id + one_indexed
        item_name = data.items_dict.get(item_id_key, {}).get('Item', f'Unknown Item {item_id_key}')
        item_names.append(item_name)
    return item_names

def position(game):
    r_pos = game.get_memory_value(Y_POS_ADDR)
    c_pos = game.get_memory_value(X_POS_ADDR)
    map_n = game.get_memory_value(MAP_N_ADDR)
    if r_pos >= 443:
        r_pos = 444
    if r_pos <= 0:
        r_pos = 0
    if c_pos >= 443:
        c_pos = 444
    if c_pos <= 0:
        c_pos = 0
    if map_n > 247:
        map_n = 247
    if map_n < -1:
        map_n = -1
    return r_pos, c_pos, map_n

def party(game):
    # party = [game.get_memory_value(addr) for addr in PARTY_ADDR]
    party_size = game.get_memory_value(PARTY_SIZE_ADDR)
    party_levels = [x for x in [game.get_memory_value(addr) for addr in PARTY_LEVEL_ADDR] if x > 0]
    return party_size, party_levels # [x for x in party_levels if x > 0]

def opponent(game):
    return [game.get_memory_value(addr) for addr in OPPONENT_LEVEL_ADDR]

def oak_parcel(game):
    return read_bit(game, OAK_PARCEL_ADDR, 1)

def pokedex_obtained(game):
    return read_bit(game, OAK_POKEDEX_ADDR, 5)

def pokemon_seen(game):
    seen_bytes = [game.get_memory_value(addr) for addr in SEEN_POKE_ADDR]
    return sum([bit_count(b) for b in seen_bytes])

def pokemon_caught(game):
    caught_bytes = [game.get_memory_value(addr) for addr in CAUGHT_POKE_ADDR]
    return sum([bit_count(b) for b in caught_bytes])

def hp(game):
    """Percentage of total party HP"""
    party_hp = [read_uint16(game, addr) for addr in HP_ADDR]
    party_max_hp = [read_uint16(game, addr) for addr in MAX_HP_ADDR]
    # Avoid division by zero if no pokemon
    sum_max_hp = sum(party_max_hp)
    if sum_max_hp == 0:
        return 1
    return sum(party_hp) / sum_max_hp

def money(game):
    return (
        100 * 100 * bcd(game.get_memory_value(MONEY_ADDR_1))
        + 100 * bcd(game.get_memory_value(MONEY_ADDR_100))
        + bcd(game.get_memory_value(MONEY_ADDR_10000))
    )

def badges(game):
    badges = game.get_memory_value(BADGE_1_ADDR)
    return bit_count(badges)

def saved_bill(game):
    """Restored Bill from his experiment"""
    return int(read_bit(game, USED_CELL_SEPARATOR_ADDR, 3))

def ss_anne_appeared(game):
    """
    D803 - True is SS Anne is here
    """
    return game.get_memory_value(SS_ANNE)

def events(game):
    """Adds up all event flags, exclude museum ticket"""
    num_events = sum(
        bit_count(game.get_memory_value(i))
        for i in range(EVENT_FLAGS_START_ADDR, EVENT_FLAGS_END_ADDR)
    )
    museum_ticket = int(read_bit(game, MUSEUM_TICKET_ADDR, 0))

    # Omit 13 events by default
    return max(num_events - 13 - museum_ticket, 0)

def talk_to_npc(game):
    """
    Talk to NPC
    238 is text box arrow blink on
    127 is no text box arrow
    """
    return game.get_memory_value(TEXT_BOX_ARROW_BLINK)

def is_in_battle(game):
    # D057
    # 0 not in battle
    # 1 wild battle
    # 2 trainer battle
    # -1 lost battle
    bflag = game.get_memory_value(BATTLE_FLAG)
    if bflag > 0:
        return True
    else:
        return False
    
def if_font_is_loaded(game):
    return game.get_memory_value(IF_FONT_IS_LOADED)

def player_direction(game):
    return game.get_memory_value(PLAYER_DIRECTION)

def player_y(game):
    return game.get_memory_value(PLAYER_Y)

def player_x(game):
    return game.get_memory_value(PLAYER_X)

def map_n(game):
    return game.get_memory_value(MAP_N_ADDR)

def npc_y(game, npc_id, npc_bank):
    npc_id = npc_id * 0x10
    npc_bank = (npc_bank + 1) *  0x100
    return game.get_memory_value(0xC004 + npc_id + npc_bank)

def npc_x(game, npc_id, npc_bank):
    npc_id = npc_id * 0x10
    npc_bank = (npc_bank + 1) *  0x100
    return game.get_memory_value(0xC006 + npc_id + npc_bank)

def sprites(game):
    return game.get_memory_value(WNUMSPRITES)

def signs(game):
    return game.get_memory_value(WNUMSIGNS)