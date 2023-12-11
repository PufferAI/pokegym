# addresses from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map
# https://github.com/pret/pokered/blob/91dc3c9f9c8fd529bb6e8307b58b96efa0bec67e/constants/event_constants.asm
HP_ADDR =  [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248]
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
EVENT_FLAGS_END_ADDR = 0xD761
MUSEUM_TICKET_ADDR = 0xD754
MONEY_ADDR_1 = 0xD347
MONEY_ADDR_100 = 0xD348
MONEY_ADDR_10000 = 0xD349



#Trainer Moves/PP counter if 00 then no move is present
P1MOVES = [0xD173, 0xD174, 0xD175, 0xD176]
P2MOVES = [0xD19F, 0xD1A0, 0xD1A1, 0xD1A2]
P3MOVES = [0xD1CB, 0xD1CC, 0xD1CD, 0xD1CE]
P4MOVES = [0xD1F7, 0xD1F8, 0xD1F9, 0xD1FA]
P5MOVES = [0xD223, 0xD224, 0xD225, 0xD226]
P6MOVES = [0xD24F, 0xD250, 0xD251, 0xD252]

P1MOVEPP = [0xD188, 0xD189, 0xD18A, 0xD18B]
P2MOVEPP = [0xD1B4, 0xD1B5, 0xD1B6, 0xD1B7]
P3MOVEPP = [0xD1E0, 0xD1E1, 0xD1E2, 0xD1E3]
P4MOVEPP = [0xD20C, 0xD20D, 0xD20E, 0xD20F]
P5MOVEPP = [0xD238, 0xD239, 0xD23A, 0xD23B]
P6MOVEPP = [0xD264, 0xD265, 0xD266, 0xD267]

POKE = [0xD16B, 0xD197, 0xD1C3, 0xD1EF, 0xD21B, 0xD247] # - Pokémon (Again)
STATUS = [0xD16F, 0xD19B, 0xD1C7, 0xD1F3, 0xD21F, 0xD24B] # - Status (Poisoned, Paralyzed, etc.)
TYPE1 = [0xD170, 0xD19C, 0xD1C8, 0xD1F4, 0xD220, 0xD24C] # - Type 1
TYPE2 = [0xD171, 0xD19D, 0xD1C9, 0xD1F5, 0xD221, 0xD24D] # - Type 2
LEVEL = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268] # - Level (actual level)
MAXHP = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269] # - Max HP if = 01 + 256 to MAXHP2 value
CHP = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248] # - Current HP if = 01 + 256



STATUSDICT = {
    0x03: 'Poison',
    0x04: 'Burn',
    0x05: 'Frozen',
    0x06: 'Paralyze',
    0x00: 'None'
}

def bcd(num):
    return 10 * ((num >> 4) & 0x0f) + (num & 0x0f)

def bit_count(bits):
    return bin(bits).count('1')

def read_bit(game, addr, bit) -> bool:
    # add padding so zero will read '0b100000000' instead of '0b0'
    return bin(256 + game.get_memory_value(addr))[-bit-1] == '1'

def read_uint16(game, start_addr):
    '''Read 2 bytes'''
    val_256 = game.get_memory_value(start_addr)
    val_1 = game.get_memory_value(start_addr + 1)
    return 256*val_256 + val_1

def position(game):
    r_pos = game.get_memory_value(Y_POS_ADDR)
    c_pos = game.get_memory_value(X_POS_ADDR)
    map_n = game.get_memory_value(MAP_N_ADDR)
    return r_pos, c_pos, map_n

#start new functions

def pokemon(game):
    poke = [game.get_memory_value(a) for a in POKE]
    stat = [game.get_memory_value(a) for a in STATUS]
    # status = STATUSDICT.get(stat, 'Unknown')
    type1 = [game.get_memory_value(a) for a in TYPE1]
    type2 = [game.get_memory_value(a) for a in TYPE2]
    level = [game.get_memory_value(a) for a in LEVEL]
    mhp = [read_uint16(game, a) for a in MAXHP]
    chp = [read_uint16(game, a) for a in CHP]
    hp = []
    # moves = [game.get_memory_value(addr) for addr in P1MOVES]
    # movepp = [game.get_memory_value(addr) for addr in P1MOVEPP]
    assert len(mhp) == len(chp)
    for h, i in zip(mhp, chp):
        if h == 0:
            j = 1
        else:
            j = i / h
        hp.append(j)
    return poke, type1, type2, level, hp #, status

# def p1(game):
#     p1chp = read_uint16(game, P1CHP)
#     p1mhp = read_uint16(game, P1MHP)
#     p1moves = [game.get_memory_value(addr) for addr in P1MOVES]
#     p1movepp = [game.get_memory_value(addr) for addr in P1MOVEPP]
#     p1lvl = game.get_memory_value(P1LVL)
#     p1stat = game.get_memory_value(P1STAT)
#     p1status = STATUSDICT.get(p1stat, 'Unknown')
#     p1t1 = game.get_memory_value(P1T1)
#     p1t2 = game.get_memory_value(P1T2)
#     if p1mhp == 0:
#         p1hp = 1
#     else:
#         p1hp = p1chp / p1mhp
#     return p1moves, p1movepp, p1lvl, p1status, p1t1, p1t2, p1hp

# def p2(game):
#     p2chp = read_uint16(game, P2CHP)
#     p2mhp = read_uint16(game, P2MHP)
#     p2moves = [game.get_memory_value(addr) for addr in P2MOVES]
#     p2movepp = [game.get_memory_value(addr) for addr in P2MOVEPP]
#     p2lvl = game.get_memory_value(P2LVL)
#     p2stat = game.get_memory_value(P2STAT)
#     p2status = STATUSDICT.get(p2stat, 'Unknown')
#     p2t1 = game.get_memory_value(P2T1)
#     p2t2 = game.get_memory_value(P2T2)
#     if p2mhp == 0:
#         p2hp = 1
#     else:
#         p2hp = p2chp / p2mhp
#     return p2moves, p2movepp, p2lvl, p2status, p2t1, p2t2, p2hp

# def p3(game):
#     p3chp = read_uint16(game, P3CHP)
#     p3mhp = read_uint16(game, P3MHP)
#     p3moves = [game.get_memory_value(addr) for addr in P3MOVES]
#     p3movepp = [game.get_memory_value(addr) for addr in P3MOVEPP]
#     p3lvl = game.get_memory_value(P3LVL)
#     p3stat = game.get_memory_value(P3STAT)
#     p3status = STATUSDICT.get(p3stat, 'Unknown')
#     p3t1 = game.get_memory_value(P3T1)
#     p3t2 = game.get_memory_value(P3T2)
#     if p3mhp == 0:
#         p3hp = 1
#     else:
#         p3hp = p3chp / p3mhp
#     return p3moves, p3movepp, p3lvl, p3status, p3t1, p3t2, p3hp

# def p4(game):
#     p4chp = read_uint16(game, P4CHP)
#     p4mhp = read_uint16(game, P4MHP)
#     p4moves = [game.get_memory_value(addr) for addr in P4MOVES]
#     p4movepp = [game.get_memory_value(addr) for addr in P4MOVEPP]
#     p4lvl = game.get_memory_value(P4LVL)
#     p4stat = game.get_memory_value(P4STAT)
#     p4status = STATUSDICT.get(p4stat, 'Unknown')
#     p4t1 = game.get_memory_value(P4T1)
#     p4t2 = game.get_memory_value(P4T2)
#     if p4mhp == 0:
#         p4hp = 1
#     else:
#         p4hp = p4chp / p4mhp
#     return p4moves, p4movepp, p4lvl, p4status, p4t1, p4t2, p4hp

# def p5(game):
#     p5chp = read_uint16(game, P5CHP)
#     p5mhp = read_uint16(game, P5MHP)
#     p5moves = [game.get_memory_value(addr) for addr in P5MOVES]
#     p5movepp = [game.get_memory_value(addr) for addr in P5MOVEPP]
#     p5lvl = game.get_memory_value(P5LVL)
#     p5stat = game.get_memory_value(P5STAT)
#     p5status = STATUSDICT.get(p5stat, 'Unknown')
#     p5t1 = game.get_memory_value(P5T1)
#     p5t2 = game.get_memory_value(P5T2)
#     if p5mhp == 0:
#         p5hp = 1
#     else:
#         p5hp = p5chp / p5mhp
#     return p5moves, p5movepp, p5lvl, p5status, p5t1, p5t2, p5hp

# def p6(game):
#     p6chp = read_uint16(game, P6CHP)
#     p6mhp = read_uint16(game, P6MHP)
#     p6moves = [game.get_memory_value(addr) for addr in P6MOVES]
#     p6movepp = [game.get_memory_value(addr) for addr in P6MOVEPP]
#     p6lvl = game.get_memory_value(P6LVL)
#     p6stat = game.get_memory_value(P6STAT)
#     p6status = STATUSDICT.get(p6stat, 'Unknown')
#     p6t1 = game.get_memory_value(P6T1)
#     p6t2 = game.get_memory_value(P6T2)
#     if p6mhp == 0:
#         p6hp = 1
#     else:
#         p6hp = p6chp / p6mhp
#     return p6moves, p6movepp, p6lvl, p6status, p6t1, p6t2, p6hp

# # def move_check(game):
    

#end new functions

def party(game):
    party = [game.get_memory_value(addr) for addr in PARTY_ADDR]
    party_size = game.get_memory_value(PARTY_SIZE_ADDR)
    party_levels = [game.get_memory_value(addr) for addr in PARTY_LEVEL_ADDR]
    return party, party_size, party_levels

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
    '''Percentage of total party HP'''
    party_hp = [read_uint16(game, addr) for addr in HP_ADDR]
    party_max_hp = [read_uint16(game, addr) for addr in MAX_HP_ADDR]

    # Avoid division by zero if no pokemon
    sum_max_hp = sum(party_max_hp)
    if sum_max_hp == 0:
        return 1

    return sum(party_hp) / sum_max_hp

def money(game):
    return (100 * 100 * bcd(game.get_memory_value(MONEY_ADDR_1))
        + 100 * bcd(game.get_memory_value(MONEY_ADDR_100))
        + bcd(game.get_memory_value(MONEY_ADDR_10000)))

def badges(game):
    badges = game.get_memory_value(BADGE_1_ADDR)
    return bit_count(badges)

def events(game):
    '''Adds up all event flags, exclude museum ticket'''
    num_events = sum(bit_count(game.get_memory_value(i))
        for i in range(EVENT_FLAGS_START_ADDR, EVENT_FLAGS_END_ADDR))
    museum_ticket = int(read_bit(game, MUSEUM_TICKET_ADDR, 0))

    # Omit 13 events by default
    return max(num_events - 13 - museum_ticket, 0)



# Menu Data

# Coordinates of the position of the cursor for the top menu item (id 0)
# CC24 : Y position
# CC25 : X position

# CC26 - Currently selected menu item (topmost is 0)
# CC27 - Tile "hidden" by the menu cursor
# CC28 - ID of the last menu item
# CC29 - bitmask applied to the key port for the current menu
# CC2A - ID of the previously selected menu item
# CC2B - Last position of the cursor on the party / Bill's PC screen
# CC2C - Last position of the cursor on the item screen
# CC2D - Last position of the cursor on the START / battle menu
# CC2F - Index (in party) of the Pokémon currently sent out
# CC30~CC31 - Pointer to cursor tile in C3A0 buffer
# CC36 - ID of the first displayed menu item
# CC35 - Item highlighted with Select (01 = first item, 00 = no item, etc.)
# CC3A and CC3B are unused 


# Pokémon Mart

# JPN addr. 	INT addr. 	Description
# CF62 	    CF7B 	    Total Items
# CF63 	    CF7C 	    Item 1
# CF64 	    CF7D 	    Item 2
# CF65 	    CF7E 	    Item 3
# CF66 	    CF7F 	    Item 4
# CF67 	    CF80 	    Item 5
# CF68 	    CF81 	    Item 6
# CF69 	    CF82 	    Item 7
# CF70 	    CF83 	    Item 8
# CF71 	    CF84 	    Item 9
# CF72 	    CF85 	    Item 10 


# Event Flags

# D5A6 to D5C5 : Missable Objects Flags (flags for every (dis)appearing sprites, like the guard in Cerulean City or the Pokéballs in Oak's Lab)
# D5AB - Starters Back?
# D5C0(bit 1) - 0=Mewtwo appears, 1=Doesn't (See D85F)
# D5F3 - Have Town map?
# D60D - Have Oak's Parcel?
# D700 - Bike Speed
# D70B - Fly Anywhere Byte 1
# D70C - Fly Anywhere Byte 2
# D70D - Safari Zone Time Byte 1
# D70E - Safari Zone Time Byte 2
# D710 - Fossilized Pokémon?
# D714 - Position in Air
# D72E - Did you get Lapras Yet?
# D732 - Debug New Game
# D751 - Fought Giovanni Yet?
# D755 - Fought Brock Yet?
# D75E - Fought Misty Yet?
# D773 - Fought Lt. Surge Yet?
# D77C - Fought Erika Yet?
# D782 - Fought Articuno Yet?
# D790 - If bit 7 is set, Safari Game over
# D792 - Fought Koga Yet?
# D79A - Fought Blaine Yet?
# D7B3 - Fought Sabrina Yet?
# D7D4 - Fought Zapdos Yet?
# D7D8 - Fought Snorlax Yet (Vermilion)
# D7E0 - Fought Snorlax Yet? (Celadon)
# D7EE - Fought Moltres Yet?
# D803 - Is SS Anne here?
# D85F - Mewtwo can be caught if bit 2 clear - Needs D5C0 bit 1 clear, too 