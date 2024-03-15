import random
from pokegym import data

# addresses from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map
# https://github.com/pret/pokered/blob/91dc3c9f9c8fd529bb6e8307b58b96efa0bec67e/constants/event_constants.asm
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
WCUTTILE = 0xCD4D # $3d = tree tile; $52 = grass tile

# #Trainer Moves/PP counter if 00 then no move is present
# P1MOVES = [0xD173, 0xD174, 0xD175, 0xD176]
# P2MOVES = [0xD19F, 0xD1A0, 0xD1A1, 0xD1A2]
# P3MOVES = [0xD1CB, 0xD1CC, 0xD1CD, 0xD1CE]
# P4MOVES = [0xD1F7, 0xD1F8, 0xD1F9, 0xD1FA]
# P5MOVES = [0xD223, 0xD224, 0xD225, 0xD226]
# P6MOVES = [0xD24F, 0xD250, 0xD251, 0xD252]

# Moves 1-4 for Poke1, Poke2, Poke3, Poke4, Poke5, Poke6
MOVE1 = [0xD173, 0xD19F, 0xD1CB, 0xD1F7, 0xD223, 0xD24F]
MOVE2 = [0xD174, 0xD1A0, 0xD1CC, 0xD1F8, 0xD224, 0xD250]
MOVE3 = [0xD175, 0xD1A1, 0xD1CD, 0xD1F9, 0xD225, 0xD251]
MOVE4 = [0xD176, 0xD1A2, 0xD1CE, 0xD1FA, 0xD226, 0xD252]


items_dict = {
    1: {'decimal': 1, 'hex': '0x01', 'Item': 'Master Ball'},
    2: {'decimal': 2, 'hex': '0x02', 'Item': 'Ultra Ball'},
    3: {'decimal': 3, 'hex': '0x03', 'Item': 'Great Ball'},
    4: {'decimal': 4, 'hex': '0x04', 'Item': 'Poké Ball'},
    5: {'decimal': 5, 'hex': '0x05', 'Item': 'Town Map'},
    6: {'decimal': 6, 'hex': '0x06', 'Item': 'Bicycle'},
    7: {'decimal': 7, 'hex': '0x07', 'Item': '?????'},
    8: {'decimal': 8, 'hex': '0x08', 'Item': 'Safari Ball'},
    9: {'decimal': 9, 'hex': '0x09', 'Item': 'Pokédex'},
    10: {'decimal': 10, 'hex': '0x0A', 'Item': 'Moon Stone'},
    11: {'decimal': 11, 'hex': '0x0B', 'Item': 'Antidote'},
    12: {'decimal': 12, 'hex': '0x0C', 'Item': 'Burn Heal'},
    13: {'decimal': 13, 'hex': '0x0D', 'Item': 'Ice Heal'},
    14: {'decimal': 14, 'hex': '0x0E', 'Item': 'Awakening'},
    15: {'decimal': 15, 'hex': '0x0F', 'Item': 'Parlyz Heal'},
    16: {'decimal': 16, 'hex': '0x10', 'Item': 'Full Restore'},
    17: {'decimal': 17, 'hex': '0x11', 'Item': 'Max Potion'},
    18: {'decimal': 18, 'hex': '0x12', 'Item': 'Hyper Potion'},
    19: {'decimal': 19, 'hex': '0x13', 'Item': 'Super Potion'},
    20: {'decimal': 20, 'hex': '0x14', 'Item': 'Potion'},
    21: {'decimal': 21, 'hex': '0x15', 'Item': 'BoulderBadge'},
    22: {'decimal': 22, 'hex': '0x16', 'Item': 'CascadeBadge'},
    23: {'decimal': 23, 'hex': '0x17', 'Item': 'ThunderBadge'},
    24: {'decimal': 24, 'hex': '0x18', 'Item': 'RainbowBadge'},
    25: {'decimal': 25, 'hex': '0x19', 'Item': 'SoulBadge'},
    26: {'decimal': 26, 'hex': '0x1A', 'Item': 'MarshBadge'},
    27: {'decimal': 27, 'hex': '0x1B', 'Item': 'VolcanoBadge'},
    28: {'decimal': 28, 'hex': '0x1C', 'Item': 'EarthBadge'},
    29: {'decimal': 29, 'hex': '0x1D', 'Item': 'Escape Rope'},
    30: {'decimal': 30, 'hex': '0x1E', 'Item': 'Repel'},
    31: {'decimal': 31, 'hex': '0x1F', 'Item': 'Old Amber'},
    32: {'decimal': 32, 'hex': '0x20', 'Item': 'Fire Stone'},
    33: {'decimal': 33, 'hex': '0x21', 'Item': 'Thunderstone'},
    34: {'decimal': 34, 'hex': '0x22', 'Item': 'Water Stone'},
    35: {'decimal': 35, 'hex': '0x23', 'Item': 'HP Up'},
    36: {'decimal': 36, 'hex': '0x24', 'Item': 'Protein'},
    37: {'decimal': 37, 'hex': '0x25', 'Item': 'Iron'},
    38: {'decimal': 38, 'hex': '0x26', 'Item': 'Carbos'},
    39: {'decimal': 39, 'hex': '0x27', 'Item': 'Calcium'},
    40: {'decimal': 40, 'hex': '0x28', 'Item': 'Rare Candy'},
    41: {'decimal': 41, 'hex': '0x29', 'Item': 'Dome Fossil'},
    42: {'decimal': 42, 'hex': '0x2A', 'Item': 'Helix Fossil'},
    43: {'decimal': 43, 'hex': '0x2B', 'Item': 'Secret Key'},
    44: {'decimal': 44, 'hex': '0x2C', 'Item': '?????'},
    45: {'decimal': 45, 'hex': '0x2D', 'Item': 'Bike Voucher'},
    46: {'decimal': 46, 'hex': '0x2E', 'Item': 'X Accuracy'},
    47: {'decimal': 47, 'hex': '0x2F', 'Item': 'Leaf Stone'},
    48: {'decimal': 48, 'hex': '0x30', 'Item': 'Card Key'},
    49: {'decimal': 49, 'hex': '0x31', 'Item': 'Nugget'},
    50: {'decimal': 50, 'hex': '0x32', 'Item': 'PP Up*'},
    51: {'decimal': 51, 'hex': '0x33', 'Item': 'Poké Doll'},
    52: {'decimal': 52, 'hex': '0x34', 'Item': 'Full Heal'},
    53: {'decimal': 53, 'hex': '0x35', 'Item': 'Revive'},
    54: {'decimal': 54, 'hex': '0x36', 'Item': 'Max Revive'},
    55: {'decimal': 55, 'hex': '0x37', 'Item': 'Guard Spec.'},
    56: {'decimal': 56, 'hex': '0x38', 'Item': 'Super Repel'},
    57: {'decimal': 57, 'hex': '0x39', 'Item': 'Max Repel'},
    58: {'decimal': 58, 'hex': '0x3A', 'Item': 'Dire Hit'},
    59: {'decimal': 59, 'hex': '0x3B', 'Item': 'Coin'},
    60: {'decimal': 60, 'hex': '0x3C', 'Item': 'Fresh Water'},
    61: {'decimal': 61, 'hex': '0x3D', 'Item': 'Soda Pop'},
    62: {'decimal': 62, 'hex': '0x3E', 'Item': 'Lemonade'},
    63: {'decimal': 63, 'hex': '0x3F', 'Item': 'S.S. Ticket'},
    64: {'decimal': 64, 'hex': '0x40', 'Item': 'Gold Teeth'},
    65: {'decimal': 65, 'hex': '0x41', 'Item': 'X Attack'},
    66: {'decimal': 66, 'hex': '0x42', 'Item': 'X Defend'},
    67: {'decimal': 67, 'hex': '0x43', 'Item': 'X Speed'},
    68: {'decimal': 68, 'hex': '0x44', 'Item': 'X Special'},
    69: {'decimal': 69, 'hex': '0x45', 'Item': 'Coin Case'},
    70: {'decimal': 70, 'hex': '0x46', 'Item': "Oak's Parcel"},
    71: {'decimal': 71, 'hex': '0x47', 'Item': 'Itemfinder'},
    72: {'decimal': 72, 'hex': '0x48', 'Item': 'Silph Scope'},
    73: {'decimal': 73, 'hex': '0x49', 'Item': 'Poké Flute'},
    74: {'decimal': 74, 'hex': '0x4A', 'Item': 'Lift Key'},
    75: {'decimal': 75, 'hex': '0x4B', 'Item': 'Exp. All'},
    76: {'decimal': 76, 'hex': '0x4C', 'Item': 'Old Rod'},
    77: {'decimal': 77, 'hex': '0x4D', 'Item': 'Good Rod'},
    78: {'decimal': 78, 'hex': '0x4E', 'Item': 'Super Rod'},
    79: {'decimal': 79, 'hex': '0x4F', 'Item': 'PP Up'},
    80: {'decimal': 80, 'hex': '0x50', 'Item': 'Ether'},
    81: {'decimal': 81, 'hex': '0x51', 'Item': 'Max Ether'},
    82: {'decimal': 82, 'hex': '0x52', 'Item': 'Elixer'},
    83: {'decimal': 83, 'hex': '0x53', 'Item': 'Max Elixer'},
    196: {'decimal': 196, 'hex': '0xC4', 'Item': 'HM01'},
    197: {'decimal': 197, 'hex': '0xC5', 'Item': 'HM02'},
    198: {'decimal': 198, 'hex': '0xC6', 'Item': 'HM03'},
    199: {'decimal': 199, 'hex': '0xC7', 'Item': 'HM04'},
    200: {'decimal': 200, 'hex': '0xC8', 'Item': 'HM05'},
    201: {'decimal': 201, 'hex': '0xC9', 'Item': 'TM01'},
    202: {'decimal': 202, 'hex': '0xCA', 'Item': 'TM02'},
    203: {'decimal': 203, 'hex': '0xCB', 'Item': 'TM03'},
    204: {'decimal': 204, 'hex': '0xCC', 'Item': 'TM04'},
    205: {'decimal': 205, 'hex': '0xCD', 'Item': 'TM05'},
    206: {'decimal': 206, 'hex': '0xCE', 'Item': 'TM06'},
    207: {'decimal': 207, 'hex': '0xCF', 'Item': 'TM07'},
    208: {'decimal': 208, 'hex': '0xD0', 'Item': 'TM08'},
    209: {'decimal': 209, 'hex': '0xD1', 'Item': 'TM09'},
    210: {'decimal': 210, 'hex': '0xD2', 'Item': 'TM10'},
    211: {'decimal': 211, 'hex': '0xD3', 'Item': 'TM11'},
    212: {'decimal': 212, 'hex': '0xD4', 'Item': 'TM12'},
    213: {'decimal': 213, 'hex': '0xD5', 'Item': 'TM13'},
    214: {'decimal': 214, 'hex': '0xD6', 'Item': 'TM14'},
    215: {'decimal': 215, 'hex': '0xD7', 'Item': 'TM15'},
    216: {'decimal': 216, 'hex': '0xD8', 'Item': 'TM16'},
    217: {'decimal': 217, 'hex': '0xD9', 'Item': 'TM17'},
    218: {'decimal': 218, 'hex': '0xDA', 'Item': 'TM18'},
    219: {'decimal': 219, 'hex': '0xDB', 'Item': 'TM19'},
    220: {'decimal': 220, 'hex': '0xDC', 'Item': 'TM20'},
    221: {'decimal': 221, 'hex': '0xDD', 'Item': 'TM21'},
    222: {'decimal': 222, 'hex': '0xDE', 'Item': 'TM22'},
    223: {'decimal': 223, 'hex': '0xDF', 'Item': 'TM23'},
    224: {'decimal': 224, 'hex': '0xE0', 'Item': 'TM24'},
    225: {'decimal': 225, 'hex': '0xE1', 'Item': 'TM25'},
    226: {'decimal': 226, 'hex': '0xE2', 'Item': 'TM26'},
    227: {'decimal': 227, 'hex': '0xE3', 'Item': 'TM27'},
    228: {'decimal': 228, 'hex': '0xE4', 'Item': 'TM28'},
    229: {'decimal': 229, 'hex': '0xE5', 'Item': 'TM29'},
    230: {'decimal': 230, 'hex': '0xE6', 'Item': 'TM30'},
    231: {'decimal': 231, 'hex': '0xE7', 'Item': 'TM31'},
    232: {'decimal': 232, 'hex': '0xE8', 'Item': 'TM32'},
    233: {'decimal': 233, 'hex': '0xE9', 'Item': 'TM33'},
    234: {'decimal': 234, 'hex': '0xEA', 'Item': 'TM34'},
    235: {'decimal': 235, 'hex': '0xEB', 'Item': 'TM35'},
    236: {'decimal': 236, 'hex': '0xEC', 'Item': 'TM36'},
    237: {'decimal': 237, 'hex': '0xED', 'Item': 'TM37'},
    238: {'decimal': 238, 'hex': '0xEE', 'Item': 'TM38'},
    239: {'decimal': 239, 'hex': '0xEF', 'Item': 'TM39'},
    240: {'decimal': 240, 'hex': '0xF0', 'Item': 'TM40'},
    241: {'decimal': 241, 'hex': '0xF1', 'Item': 'TM41'},
    242: {'decimal': 242, 'hex': '0xF2', 'Item': 'TM42'},
    243: {'decimal': 243, 'hex': '0xF3', 'Item': 'TM43'},
    244: {'decimal': 244, 'hex': '0xF4', 'Item': 'TM44'},
    245: {'decimal': 245, 'hex': '0xF5', 'Item': 'TM45'},
    246: {'decimal': 246, 'hex': '0xF6', 'Item': 'TM46'},
    247: {'decimal': 247, 'hex': '0xF7', 'Item': 'TM47'},
    248: {'decimal': 248, 'hex': '0xF8', 'Item': 'TM48'},
    249: {'decimal': 249, 'hex': '0xF9', 'Item': 'TM49'},
    250: {'decimal': 250, 'hex': '0xFA', 'Item': 'TM50'},
    251: {'decimal': 251, 'hex': '0xFB', 'Item': 'TM51'},
    252: {'decimal': 252, 'hex': '0xFC', 'Item': 'TM52'},
    253: {'decimal': 253, 'hex': '0xFD', 'Item': 'TM53'},
    254: {'decimal': 254, 'hex': '0xFE', 'Item': 'TM54'},
    255: {'decimal': 255, 'hex': '0xFF', 'Item': 'TM55'},
}


poke_dict = {
   3: {'hex': '3', 'decimal': '3', 'name': 'Nidoran♂'},
   4: {'hex': '4', 'decimal': '4', 'name': 'Clefairy'},
   5: {'hex': '5', 'decimal': '5', 'name': 'Spearow'},
   9: {'hex': '9', 'decimal': '9', 'name': 'Ivysaur'},
   15: {'hex': 'F', 'decimal': '15', 'name': 'Nidoran♀'},
   16: {'hex': '10', 'decimal': '16', 'name': 'Nidoqueen'},
   28: {'hex': '1C', 'decimal': '28', 'name': 'Blastoise'},
   35: {'hex': '23', 'decimal': '35', 'name': 'Fearow'},
   36: {'hex': '24', 'decimal': '36', 'name': 'Pidgey'},
   38: {'hex': '26', 'decimal': '38', 'name': 'Kadabra'},
   39: {'hex': '27', 'decimal': '39', 'name': 'Graveler'},
   46: {'hex': '2E', 'decimal': '46', 'name': 'Parasect', 'type': 'Bug'},
   48: {'hex': '30', 'decimal': '48', 'name': 'Drowzee'},
   49: {'hex': '31', 'decimal': '49', 'name': 'Golem'},
   57: {'hex': '39', 'decimal': '57', 'name': 'Mankey'},
   59: {'hex': '3B', 'decimal': '59', 'name': 'Diglett'},
   70: {'hex': '46', 'decimal': '70', 'name': 'Doduo'},
   84: {'hex': '54', 'decimal': '84', 'name': 'Pikachu', 'type': 'Electric'},
   85: {'hex': '55', 'decimal': '85', 'name': 'Raichu', 'type': 'Electric'},
   100: {'hex': '64', 'decimal': '100', 'name': 'Jigglypuff'},
   101: {'hex': '65', 'decimal': '101', 'name': 'Wigglytuff'},
   107: {'hex': '6B', 'decimal': '107', 'name': 'Zubat'},
   108: {'hex': '6C', 'decimal': '108', 'name': 'Ekans'},
   109: {'hex': '6D', 'decimal': '109', 'name': 'Paras', 'type': 'Bug'},
   112: {'hex': '70', 'decimal': '112', 'name': 'Weedle', 'type': 'Bug'},
   113: {'hex': '71', 'decimal': '113', 'name': 'Kakuna', 'type': 'Bug'},
   114: {'hex': '72', 'decimal': '114', 'name': 'Beedrill', 'type': 'Bug'},
   116: {'hex': '74', 'decimal': '116', 'name': 'Dodrio'},
   117: {'hex': '75', 'decimal': '117', 'name': 'Primeape'},
   118: {'hex': '76', 'decimal': '118', 'name': 'Dugtrio'},
   123: {'hex': '7B', 'decimal': '123', 'name': 'Caterpie', 'type': 'Bug'},
   124: {'hex': '7C', 'decimal': '124', 'name': 'Metapod', 'type': 'Bug'},
   125: {'hex': '7D', 'decimal': '125', 'name': 'Butterfree', 'type': 'Bug'},
   129: {'hex': '81', 'decimal': '129', 'name': 'Hypno'},
   130: {'hex': '82', 'decimal': '130', 'name': 'Golbat'},
   133: {'hex': '85', 'decimal': '133', 'name': 'Magikarp'},
   142: {'hex': '8E', 'decimal': '142', 'name': 'Clefable'},
   148: {'hex': '94', 'decimal': '148', 'name': 'Abra'},
   149: {'hex': '95', 'decimal': '149', 'name': 'Alakazam'},
   150: {'hex': '96', 'decimal': '150', 'name': 'Pidgeotto'},
   151: {'hex': '97', 'decimal': '151', 'name': 'Pidgeot'},
   153: {'hex': '99', 'decimal': '153', 'name': 'Bulbasaur'},
   154: {'hex': '9A', 'decimal': '154', 'name': 'Venusaur'},
   165: {'hex': 'A5', 'decimal': '165', 'name': 'Rattata'},
   166: {'hex': 'A6', 'decimal': '166', 'name': 'Raticate'},
   167: {'hex': 'A7', 'decimal': '167', 'name': 'Nidorino'},
   168: {'hex': 'A8', 'decimal': '168', 'name': 'Nidorina'},
   169: {'hex': 'A9', 'decimal': '169', 'name': 'Geodude'},
   176: {'hex': 'B0', 'decimal': '176', 'name': 'Charmander'},
   177: {'hex': 'B1', 'decimal': '177', 'name': 'Squirtle'},
   178: {'hex': 'B2', 'decimal': '178', 'name': 'Charmeleon'},
   179: {'hex': 'B3', 'decimal': '179', 'name': 'Wartortle'},
   180: {'hex': 'B4', 'decimal': '180', 'name': 'Charizard'},
   185: {'hex': 'B9', 'decimal': '185', 'name': 'Oddish'},
   186: {'hex': 'BA', 'decimal': '186', 'name': 'Gloom'},
   187: {'hex': 'BB', 'decimal': '187', 'name': 'Vileplume'}
}


wUnusedC000 = 0xc000
wSoundID = 0xc001
wMuteAudioAndPauseMusic = 0xc002
wDisableChannelOutputWhenSfxEnds = 0xc003
wStereoPanning = 0xc004
wSavedVolume = 0xc005
wChannelCommandPointers = 0xc006
wChannelReturnAddresses = 0xc016
wChannelSoundIDs = 0xc026
wChannelFlags1 = 0xc02e
wChannelFlags2 = 0xc036
wChannelDuties = 0xc03e
wChannelDutyCycles = 0xc046
wChannelVibratoDelayCounters = 0xc04e
wChannelVibratoExtents = 0xc056
wChannelVibratoRates = 0xc05e
wChannelFrequencyLowBytes = 0xc066
wChannelVibratoDelayCounterReloadValues = 0xc06e
wChannelPitchBendLengthModifiers = 0xc076
wChannelPitchBendFrequencySteps = 0xc07e
wChannelPitchBendFrequencyStepsFractionalPart = 0xc086
wChannelPitchBendCurrentFrequencyFractionalPart = 0xc08e
wChannelPitchBendCurrentFrequencyHighBytes = 0xc096
wChannelPitchBendCurrentFrequencyLowBytes = 0xc09e
wChannelPitchBendTargetFrequencyHighBytes = 0xc0a6
wChannelPitchBendTargetFrequencyLowBytes = 0xc0ae
wChannelNoteDelayCounters = 0xc0b6
wChannelLoopCounters = 0xc0be
wChannelNoteSpeeds = 0xc0c6
wChannelNoteDelayCountersFractionalPart = 0xc0ce
wChannelOctaves = 0xc0d6
wChannelVolumes = 0xc0de
wMusicTempo = 0xc0e8
wSfxTempo = 0xc0ea
wSfxHeaderPointer = 0xc0ec
wNewSoundID = 0xc0ee
wAudioROMBank = 0xc0ef
wAudioSavedROMBank = 0xc0f0
wFrequencyModifier = 0xc0f1
wTempoModifier = 0xc0f2
wSpriteStateData1 = 0xc100
wSpriteStateData2 = 0xc200
wOAMBuffer = 0xc300
wTileMap = 0xc3a0
wSerialPartyMonsPatchList = 0xc508
wTileMapBackup = 0xc508
wSerialEnemyMonsPatchList = 0xc5d0
wOverworldMap = 0xc6e8
wRedrawRowOrColumnSrcTiles = 0xcbfc
wTopMenuItemY = 0xcc24
wTopMenuItemX = 0xcc25
wCurrentMenuItem = 0xcc26
wTileBehindCursor = 0xcc27
wMaxMenuItem = 0xcc28
wMenuWatchedKeys = 0xcc29
wLastMenuItem = 0xcc2a
wPartyAndBillsPCSavedMenuItem = 0xcc2b
wBagSavedMenuItem = 0xcc2c
wBattleAndStartSavedMenuItem = 0xcc2d
wPlayerMoveListIndex = 0xcc2e
wPlayerMonNumber = 0xcc2f
wMenuCursorLocation = 0xcc30
wMenuJoypadPollCount = 0xcc34
wMenuItemToSwap = 0xcc35
wListScrollOffset = 0xcc36
wMenuWatchMovingOutOfBounds = 0xcc37
wTradeCenterPointerTableIndex = 0xcc38
wTextDest = 0xcc3a
wDoNotWaitForButtonPressAfterDisplayingText = 0xcc3c
wSerialSyncAndExchangeNybbleReceiveData = 0xcc3d
wSerialExchangeNybbleTempReceiveData = 0xcc3d
wLinkMenuSelectionReceiveBuffer = 0xcc3d
wSerialExchangeNybbleReceiveData = 0xcc3e
wSerialExchangeNybbleSendData = 0xcc42
wLinkMenuSelectionSendBuffer = 0xcc42
wLinkTimeoutCounter = 0xcc47
wUnknownSerialCounter = 0xcc47
wEnteringCableClub = 0xcc47
wWhichTradeMonSelectionMenu = 0xcc49
wMonDataLocation = 0xcc49
wMenuWrappingEnabled = 0xcc4a
wCheckFor180DegreeTurn = 0xcc4b
wMissableObjectIndex = 0xcc4d
wPredefID = 0xcc4e
wPredefRegisters = 0xcc4f
wTrainerHeaderFlagBit = 0xcc55
wNPCMovementScriptPointerTableNum = 0xcc57
wNPCMovementScriptBank = 0xcc58
wUnusedCC5B = 0xcc5b
wVermilionDockTileMapBuffer = 0xcc5b
wOaksAideRewardItemName = 0xcc5b
wDexRatingNumMonsSeen = 0xcc5b
wFilteredBagItems = 0xcc5b
wElevatorWarpMaps = 0xcc5b
wMonPartySpritesSavedOAM = 0xcc5b
wTrainerCardBlkPacket = 0xcc5b
wSlotMachineSevenAndBarModeChance = 0xcc5b
wHallOfFame = 0xcc5b
wBoostExpByExpAll = 0xcc5b
wAnimationType = 0xcc5b
wNPCMovementDirections = 0xcc5b
wDexRatingNumMonsOwned = 0xcc5c
wDexRatingText = 0xcc5d
wSlotMachineSavedROMBank = 0xcc5e
wAnimPalette = 0xcc79
wNPCMovementDirections2 = 0xcc97
wSwitchPartyMonTempBuffer = 0xcc97
wNumStepsToTake = 0xcca1
wRLEByteCount = 0xccd2
wAddedToParty = 0xccd3
wSimulatedJoypadStatesEnd = 0xccd3
wParentMenuItem = 0xccd3
wCanEvolveFlags = 0xccd3
wForceEvolution = 0xccd4
wAILayer2Encouragement = 0xccd5
wPlayerSubstituteHP = 0xccd7
wEnemySubstituteHP = 0xccd8
wTestBattlePlayerSelectedMove = 0xccd9
wMoveMenuType = 0xccdb
wPlayerSelectedMove = 0xccdc
wEnemySelectedMove = 0xccdd
wLinkBattleRandomNumberListIndex = 0xccde
wAICount = 0xccdf
wEnemyMoveListIndex = 0xcce2
wLastSwitchInEnemyMonHP = 0xcce3
wTotalPayDayMoney = 0xcce5
wSafariEscapeFactor = 0xcce8
wSafariBaitFactor = 0xcce9
wTransformedEnemyMonOriginalDVs = 0xcceb
wInHandlePlayerMonFainted = 0xccf0
wPartyFoughtCurrentEnemyFlags = 0xccf5
wLowHealthAlarmDisabled = 0xccf6
wPlayerMonMinimized = 0xccf7
wLuckySlotHiddenObjectIndex = 0xcd05
wEnemyNumHits = 0xcd05
wEnemyBideAccumulatedDamage = 0xcd05
wInGameTradeGiveMonSpecies = 0xcd0f
wPlayerMonUnmodifiedLevel = 0xcd0f
wInGameTradeTextPointerTablePointer = 0xcd10
wPlayerMonUnmodifiedMaxHP = 0xcd10
wInGameTradeTextPointerTableIndex = 0xcd12
wPlayerMonUnmodifiedAttack = 0xcd12
wInGameTradeGiveMonName = 0xcd13
wPlayerMonUnmodifiedDefense = 0xcd14
wPlayerMonUnmodifiedSpeed = 0xcd16
wPlayerMonUnmodifiedSpecial = 0xcd18
wPlayerMonAttackMod = 0xcd1a
wPlayerMonDefenseMod = 0xcd1b
wPlayerMonSpeedMod = 0xcd1c
wPlayerMonSpecialMod = 0xcd1d
wInGameTradeReceiveMonName = 0xcd1e
wPlayerMonAccuracyMod = 0xcd1e
wPlayerMonEvasionMod = 0xcd1f
wEnemyMonUnmodifiedLevel = 0xcd23
wEnemyMonUnmodifiedMaxHP = 0xcd24
wEnemyMonUnmodifiedAttack = 0xcd26
wEnemyMonUnmodifiedDefense = 0xcd28
wInGameTradeMonNick = 0xcd29
wEnemyMonUnmodifiedSpeed = 0xcd2a
wEnemyMonUnmodifiedSpecial = 0xcd2c
wEngagedTrainerClass = 0xcd2d
wEngagedTrainerSet = 0xcd2e
wEnemyMonAttackMod = 0xcd2e
wEnemyMonDefenseMod = 0xcd2f
wEnemyMonSpeedMod = 0xcd30
wEnemyMonSpecialMod = 0xcd31
wEnemyMonAccuracyMod = 0xcd32
wEnemyMonEvasionMod = 0xcd33
wNPCMovementDirections2Index = 0xcd37
wUnusedCD37 = 0xcd37
wFilteredBagItemsCount = 0xcd37
wSimulatedJoypadStatesIndex = 0xcd38
wWastedByteCD39 = 0xcd39
wWastedByteCD3A = 0xcd3a
wOverrideSimulatedJoypadStatesMask = 0xcd3b
wFallingObjectsMovementData = 0xcd3d
wSavedY = 0xcd3d
wTempSCX = 0xcd3d
wBattleTransitionCircleScreenQuadrantY = 0xcd3d
wBattleTransitionCopyTilesOffset = 0xcd3d
wInwardSpiralUpdateScreenCounter = 0xcd3d
wHoFTeamIndex = 0xcd3d
wSSAnneSmokeDriftAmount = 0xcd3d
wRivalStarterTemp = 0xcd3d
wBoxMonCounts = 0xcd3d
wDexMaxSeenMon = 0xcd3d
wPPRestoreItem = 0xcd3d
wWereAnyMonsAsleep = 0xcd3d
wCanPlaySlots = 0xcd3d
wNumShakes = 0xcd3d
wDayCareStartLevel = 0xcd3d
wWhichBadge = 0xcd3d
wPriceTemp = 0xcd3d
wTitleMonSpecies = 0xcd3d
wPlayerCharacterOAMTile = 0xcd3d
wMoveDownSmallStarsOAMCount = 0xcd3d
wChargeMoveNum = 0xcd3d
wCoordIndex = 0xcd3d
wOptionsTextSpeedCursorX = 0xcd3d
wBoxNumString = 0xcd3d
wTrainerInfoTextBoxWidthPlus1 = 0xcd3d
wSwappedMenuItem = 0xcd3d
wHoFMonSpecies = 0xcd3d
wFieldMoves = 0xcd3d
wBadgeNumberTile = 0xcd3d
wRodResponse = 0xcd3d
wWhichTownMapLocation = 0xcd3d
wStoppingWhichSlotMachineWheel = 0xcd3d
wTradedPlayerMonSpecies = 0xcd3d
wTradingWhichPlayerMon = 0xcd3d
wChangeBoxSavedMapTextPointer = 0xcd3d
wFlyAnimUsingCoordList = 0xcd3d
wPlayerSpinInPlaceAnimFrameDelay = 0xcd3d
wPlayerSpinWhileMovingUpOrDownAnimDeltaY = 0xcd3d
wHiddenObjectFunctionArgument = 0xcd3d
wWhichTrade = 0xcd3d
wTrainerSpriteOffset = 0xcd3d
wUnusedCD3D = 0xcd3d
wHUDPokeballGfxOffsetX = 0xcd3e
wBattleTransitionCircleScreenQuadrantX = 0xcd3e
wSSAnneSmokeX = 0xcd3e
wRivalStarterBallSpriteIndex = 0xcd3e
wDayCareNumLevelsGrown = 0xcd3e
wOptionsBattleAnimCursorX = 0xcd3e
wTrainerInfoTextBoxWidth = 0xcd3e
wHoFPartyMonIndex = 0xcd3e
wNumCreditsMonsDisplayed = 0xcd3e
wBadgeNameTile = 0xcd3e
wFlyLocationsList = 0xcd3e
wSlotMachineWheel1Offset = 0xcd3e
wTradedEnemyMonSpecies = 0xcd3e
wTradingWhichEnemyMon = 0xcd3e
wFlyAnimCounter = 0xcd3e
wPlayerSpinInPlaceAnimFrameDelayDelta = 0xcd3e
wPlayerSpinWhileMovingUpOrDownAnimMaxY = 0xcd3e
wHiddenObjectFunctionRomBank = 0xcd3e
wTrainerEngageDistance = 0xcd3e
wHUDGraphicsTiles = 0xcd3f
wDayCareTotalCost = 0xcd3f
wJigglypuffFacingDirections = 0xcd3f
wOptionsBattleStyleCursorX = 0xcd3f
wTrainerInfoTextBoxNextRowOffset = 0xcd3f
wHoFMonLevel = 0xcd3f
wBadgeOrFaceTiles = 0xcd3f
wSlotMachineWheel2Offset = 0xcd3f
wNameOfPlayerMonToBeTraded = 0xcd3f
wFlyAnimBirdSpriteImageIndex = 0xcd3f
wPlayerSpinInPlaceAnimFrameDelayEndValue = 0xcd3f
wPlayerSpinWhileMovingUpOrDownAnimFrameDelay = 0xcd3f
wHiddenObjectIndex = 0xcd3f
wTrainerFacingDirection = 0xcd3f
wHoFMonOrPlayer = 0xcd40
wSlotMachineWheel3Offset = 0xcd40
wPlayerSpinInPlaceAnimSoundID = 0xcd40
wHiddenObjectY = 0xcd40
wTrainerScreenY = 0xcd40
wUnusedCD40 = 0xcd40
wDayCarePerLevelCost = 0xcd41
wHoFTeamIndex2 = 0xcd41
wHiddenItemOrCoinsIndex = 0xcd41
wTradedPlayerMonOT = 0xcd41
wHiddenObjectX = 0xcd41
wSlotMachineWinningSymbol = 0xcd41
wNumFieldMoves = 0xcd41
wSlotMachineWheel1BottomTile = 0xcd41
wTrainerScreenX = 0xcd41
wHoFTeamNo = 0xcd42
wSlotMachineWheel1MiddleTile = 0xcd42
wFieldMovesLeftmostXCoord = 0xcd42
wLastFieldMoveID = 0xcd43
wSlotMachineWheel1TopTile = 0xcd43
wSlotMachineWheel2BottomTile = 0xcd44
wSlotMachineWheel2MiddleTile = 0xcd45
wTempCoins1 = 0xcd46
wSlotMachineWheel2TopTile = 0xcd46
wBattleTransitionSpiralDirection = 0xcd47
wSlotMachineWheel3BottomTile = 0xcd47
wSlotMachineWheel3MiddleTile = 0xcd48
wFacingDirectionList = 0xcd48
wSlotMachineWheel3TopTile = 0xcd49
wTempCoins2 = 0xcd4a
wPayoutCoins = 0xcd4a
wTradedPlayerMonOTID = 0xcd4c
wSlotMachineFlags = 0xcd4c
wSlotMachineWheel1SlipCounter = 0xcd4d
wCutTile = 0xcd4d
wSlotMachineWheel2SlipCounter = 0xcd4e
wTradedEnemyMonOT = 0xcd4e
wSavedPlayerScreenY = 0xcd4f
wSlotMachineRerollCounter = 0xcd4f
wEmotionBubbleSpriteIndex = 0xcd4f
wWhichEmotionBubble = 0xcd50
wSlotMachineBet = 0xcd50
wSavedPlayerFacingDirection = 0xcd50
wWhichAnimationOffsets = 0xcd50
wTradedEnemyMonOTID = 0xcd59
wStandingOnWarpPadOrHole = 0xcd5b
wOAMBaseTile = 0xcd5b
wGymTrashCanIndex = 0xcd5b
wSymmetricSpriteOAMAttributes = 0xcd5c
wMonPartySpriteSpecies = 0xcd5d
wLeftGBMonSpecies = 0xcd5e
wRightGBMonSpecies = 0xcd5f
wFlags_0xcd60 = 0xcd60
wActionResultOrTookBattleTurn = 0xcd6a
wJoyIgnore = 0xcd6b
wDownscaledMonSize = 0xcd6c
wNumMovesMinusOne = 0xcd6c
wStatusScreenCurrentPP = 0xcd71
wNormalMaxPPList = 0xcd78
wSerialOtherGameboyRandomNumberListBlock = 0xcd81
wTileMapBackup2 = 0xcd81
wNamingScreenNameLength = 0xcee9
wEvoOldSpecies = 0xcee9
wBuffer = 0xcee9
wTownMapCoords = 0xcee9
wLearningMovesFromDayCare = 0xcee9
wChangeMonPicEnemyTurnSpecies = 0xcee9
wHPBarMaxHP = 0xcee9
wNamingScreenSubmitName = 0xceea
wChangeMonPicPlayerTurnSpecies = 0xceea
wEvoNewSpecies = 0xceea
wAlphabetCase = 0xceeb
wEvoMonTileOffset = 0xceeb
wHPBarOldHP = 0xceeb
wEvoCancelled = 0xceec
wNamingScreenLetter = 0xceed
wHPBarNewHP = 0xceed
wHPBarDelta = 0xceef
wHPBarTempHP = 0xcef0
wHPBarHPDifference = 0xcefd
wAIItem = 0xcf05
wUsedItemOnWhichPokemon = 0xcf05
wAnimSoundID = 0xcf07
wBankswitchHomeSavedROMBank = 0xcf08
wBankswitchHomeTemp = 0xcf09
wBoughtOrSoldItemInMart = 0xcf0a
wBattleResult = 0xcf0b
wAutoTextBoxDrawingControl = 0xcf0c
wTilePlayerStandingOn = 0xcf0e
wNPCMovementScriptFunctionNum = 0xcf10
wTextPredefFlag = 0xcf11
wPredefParentBank = 0xcf12
wCurSpriteMovement2 = 0xcf14
wNPCMovementScriptSpriteOffset = 0xcf17
wScriptedNPCWalkCounter = 0xcf18
wGBC = 0xcf1a
wOnSGB = 0xcf1b
wDefaultPaletteCommand = 0xcf1c
wPlayerHPBarColor = 0xcf1d
wWholeScreenPaletteMonSpecies = 0xcf1d
wEnemyHPBarColor = 0xcf1e
wPartyMenuHPBarColors = 0xcf1f
wStatusScreenHPBarColor = 0xcf25
wCopyingSGBTileData = 0xcf2d
wWhichPartyMenuHPBar = 0xcf2d
wPalPacket = 0xcf2d
wPartyMenuBlkPacket = 0xcf2e
wExpAmountGained = 0xcf4b
wGainBoostedExp = 0xcf4d
wGymCityName = 0xcf5f
wGymLeaderName = 0xcf70
wItemList = 0xcf7b
wListPointer = 0xcf8b
wUnusedCF8D = 0xcf8d
wItemPrices = 0xcf8f
wWhichPokemon = 0xcf92
wPrintItemPrices = 0xcf93
wHPBarType = 0xcf94
wListMenuID = 0xcf94
wRemoveMonFromBox = 0xcf95
wMoveMonType = 0xcf95
wItemQuantity = 0xcf96
wMaxItemQuantity = 0xcf97
wFontLoaded = 0xcfc4
wWalkCounter = 0xcfc5
wTileInFrontOfPlayer = 0xcfc6
wAudioFadeOutControl = 0xcfc7
wAudioFadeOutCounterReloadValue = 0xcfc8
wAudioFadeOutCounter = 0xcfc9
wLastMusicSoundID = 0xcfca
wUpdateSpritesEnabled = 0xcfcb
wEnemyMoveNum = 0xcfcc
wEnemyMoveEffect = 0xcfcd
wEnemyMovePower = 0xcfce
wEnemyMoveType = 0xcfcf
wEnemyMoveAccuracy = 0xcfd0
wEnemyMoveMaxPP = 0xcfd1
wPlayerMoveNum = 0xcfd2
wPlayerMoveEffect = 0xcfd3
wPlayerMovePower = 0xcfd4
wPlayerMoveType = 0xcfd5
wPlayerMoveAccuracy = 0xcfd6
wPlayerMoveMaxPP = 0xcfd7
wEnemyMonSpecies2 = 0xcfd8
wBattleMonSpecies2 = 0xcfd9
wTrainerClass = 0xd031
wTrainerPicPointer = 0xd033
wTempMoveNameBuffer = 0xd036
wLearnMoveMonName = 0xd036
wTrainerBaseMoney = 0xd046
wMissableObjectCounter = 0xd048
wTrainerName = 0xd04a
wIsInBattle = 0xd057
wPartyGainExpFlags = 0xd058
wCurOpponent = 0xd059
wBattleType = 0xd05a
wDamageMultipliers = 0xd05b
wLoneAttackNo = 0xd05c
wGymLeaderNo = 0xd05c
wTrainerNo = 0xd05d
wCriticalHitOrOHKO = 0xd05e
wMoveMissed = 0xd05f
wPlayerStatsToDouble = 0xd060
wPlayerStatsToHalve = 0xd061
wPlayerBattleStatus1 = 0xd062
wPlayerBattleStatus2 = 0xd063
wPlayerBattleStatus3 = 0xd064
wEnemyStatsToDouble = 0xd065
wEnemyStatsToHalve = 0xd066
wEnemyBattleStatus1 = 0xd067
wEnemyBattleStatus2 = 0xd068
wEnemyBattleStatus3 = 0xd069
wPlayerConfusedCounter = 0xd06b
wPlayerToxicCounter = 0xd06c
wPlayerDisabledMove = 0xd06d
wEnemyNumAttacksLeft = 0xd06f
wEnemyConfusedCounter = 0xd070
wEnemyToxicCounter = 0xd071
wEnemyDisabledMove = 0xd072
wPlayerNumHits = 0xd074
wPlayerBideAccumulatedDamage = 0xd074
wUnknownSerialCounter2 = 0xd075
wAmountMoneyWon = 0xd079
wObjectToHide = 0xd079
wObjectToShow = 0xd07a
wDefaultMap = 0xd07c
wMenuItemOffset = 0xd07c
wAnimationID = 0xd07c
wNamingScreenType = 0xd07d
wPartyMenuTypeOrMessageID = 0xd07d
wTempTilesetNumTiles = 0xd07d
wSavedListScrollOffset = 0xd07e
wBaseCoordX = 0xd081
wBaseCoordY = 0xd082
wFBTileCounter = 0xd084
wMovingBGTilesCounter2 = 0xd085
wSubAnimFrameDelay = 0xd086
wSubAnimCounter = 0xd087
wSaveFileStatus = 0xd088
wNumFBTiles = 0xd089
wFlashScreenLongCounter = 0xd08a
wSpiralBallsBaseY = 0xd08a
wFallingObjectMovementByte = 0xd08a
wNumShootingBalls = 0xd08a
wTradedMonMovingRight = 0xd08a
wOptionsInitialized = 0xd08a
wNewSlotMachineBallTile = 0xd08a
wCoordAdjustmentAmount = 0xd08a
wUnusedD08A = 0xd08a
wSpiralBallsBaseX = 0xd08b
wNumFallingObjects = 0xd08b
wSlideMonDelay = 0xd08b
wAnimCounter = 0xd08b
wSubAnimTransform = 0xd08b
wEndBattleWinTextPointer = 0xd08c
wEndBattleLoseTextPointer = 0xd08e
wEndBattleTextRomBank = 0xd092
wSubAnimAddrPtr = 0xd094
wSlotMachineAllowMatchesCounter = 0xd096
wSubAnimSubEntryAddr = 0xd096
wOutwardSpiralTileMapPointer = 0xd09a
wPartyMenuAnimMonEnabled = 0xd09b
wTownMapSpriteBlinkingEnabled = 0xd09b
wUnusedD09B = 0xd09b
wFBDestAddr = 0xd09c
wFBMode = 0xd09e
wLinkCableAnimBulgeToggle = 0xd09f
wIntroNidorinoBaseTile = 0xd09f
wOutwardSpiralCurrentDirection = 0xd09f
wDropletTile = 0xd09f
wNewTileBlockID = 0xd09f
wWhichBattleAnimTileset = 0xd09f
wSquishMonCurrentDirection = 0xd09f
wSlideMonUpBottomRowLeftTile = 0xd09f
wSpriteCurPosX = 0xd0a1
wSpriteCurPosY = 0xd0a2
wSpriteWidth = 0xd0a3
wSpriteHeight = 0xd0a4
wSpriteInputCurByte = 0xd0a5
wSpriteInputBitCounter = 0xd0a6
wSpriteOutputBitOffset = 0xd0a7
wSpriteLoadFlags = 0xd0a8
wSpriteUnpackMode = 0xd0a9
wSpriteFlipped = 0xd0aa
wSpriteInputPtr = 0xd0ab
wSpriteOutputPtr = 0xd0ad
wSpriteOutputPtrCached = 0xd0af
wSpriteDecodeTable0Ptr = 0xd0b1
wSpriteDecodeTable1Ptr = 0xd0b3
wNameListType = 0xd0b6
wPredefBank = 0xd0b7
wMonHeader = 0xd0b8
wMonHIndex = 0xd0b8
wMonHBaseStats = 0xd0b9
wMonHBaseHP = 0xd0b9
wMonHBaseAttack = 0xd0ba
wMonHBaseDefense = 0xd0bb
wMonHBaseSpeed = 0xd0bc
wMonHBaseSpecial = 0xd0bd
wMonHTypes = 0xd0be
wMonHType1 = 0xd0be
wMonHType2 = 0xd0bf
wMonHCatchRate = 0xd0c0
wMonHBaseEXP = 0xd0c1
wMonHSpriteDim = 0xd0c2
wMonHFrontSprite = 0xd0c3
wMonHBackSprite = 0xd0c5
wMonHMoves = 0xd0c7
wMonHGrowthRate = 0xd0cb
wMonHLearnset = 0xd0cc
wSavedTilesetType = 0xd0d4
wDamage = 0xd0d7
wRepelRemainingSteps = 0xd0db
wMoves = 0xd0dc
wMoveNum = 0xd0e0
wMovesString = 0xd0e1
wUnusedD119 = 0xd119
wWalkBikeSurfStateCopy = 0xd11a
wInitListType = 0xd11b
wCapturedMonSpecies = 0xd11c
wFirstMonsNotOutYet = 0xd11d
wPokeBallCaptureCalcTemp = 0xd11e
wPokeBallAnimData = 0xd11e
wUsingPPUp = 0xd11e
wMaxPP = 0xd11e
wCalculateWhoseStats = 0xd11e
wTypeEffectiveness = 0xd11e
wMoveType = 0xd11e
wNumSetBits = 0xd11e
wForcePlayerToChooseMon = 0xd11f
wEvolutionOccurred = 0xd121
wVBlankSavedROMBank = 0xd122
wIsKeyItem = 0xd124
wTextBoxID = 0xd125
wCurEnemyLVL = 0xd127
wItemListPointer = 0xd128
wLinkState = 0xd12b
wTwoOptionMenuID = 0xd12c
wChosenMenuItem = 0xd12d
wOutOfBattleBlackout = 0xd12d
wMenuExitMethod = 0xd12e
wDungeonWarpDataEntrySize = 0xd12f
wWhichPewterGuy = 0xd12f
wWhichPrizeWindow = 0xd12f
wGymGateTileBlock = 0xd12f
wSavedSpriteScreenY = 0xd130
wSavedSpriteScreenX = 0xd131
wSavedSpriteMapY = 0xd132
wSavedSpriteMapX = 0xd133
wWhichPrize = 0xd139
wIgnoreInputCounter = 0xd13a
wStepCounter = 0xd13b
wNumberOfNoRandomBattleStepsLeft = 0xd13c
wPrize1 = 0xd13d
wPrize2 = 0xd13e
wPrize3 = 0xd13f
wSerialRandomNumberListBlock = 0xd141
wPrize1Price = 0xd141
wPrize2Price = 0xd143
wPrize3Price = 0xd145
wLinkBattleRandomNumberList = 0xd148
wSerialPlayerDataBlock = 0xd152
wPseudoItemID = 0xd152
wUnusedD153 = 0xd153
wEvoStoneItemID = 0xd156
wSavedNPCMovementDirections2Index = 0xd157
wPlayerName = 0xd158
wPokedexOwned = 0xd2f7
wPokedexSeen = 0xd30a
wNumBagItems = 0xd31d
wBagItems = 0xd31e
wPlayerMoney = 0xd347
wRivalName = 0xd34a
wOptions = 0xd355
wObtainedBadges = 0xd356
wLetterPrintingDelayFlags = 0xd358
wPlayerID = 0xd359
wMapMusicSoundID = 0xd35b
wMapMusicROMBank = 0xd35c
wMapPalOffset = 0xd35d
wCurMap = 0xd35e
wCurrentTileBlockMapViewPointer = 0xd35f
wYCoord = 0xd361
wXCoord = 0xd362
wYBlockCoord = 0xd363
wXBlockCoord = 0xd364
wLastMap = 0xd365
wUnusedD366 = 0xd366
wCurMapTileset = 0xd367
wCurMapHeight = 0xd368
wCurMapWidth = 0xd369
wMapDataPtr = 0xd36a
wMapTextPtr = 0xd36c
wMapScriptPtr = 0xd36e
wMapConnections = 0xd370
wMapConn1Ptr = 0xd371
wNorthConnectionStripSrc = 0xd372
wNorthConnectionStripDest = 0xd374
wNorthConnectionStripWidth = 0xd376
wNorthConnectedMapWidth = 0xd377
wNorthConnectedMapYAlignment = 0xd378
wNorthConnectedMapXAlignment = 0xd379
wNorthConnectedMapViewPointer = 0xd37a
wMapConn2Ptr = 0xd37c
wSouthConnectionStripSrc = 0xd37d
wSouthConnectionStripDest = 0xd37f
wSouthConnectionStripWidth = 0xd381
wSouthConnectedMapWidth = 0xd382
wSouthConnectedMapYAlignment = 0xd383
wSouthConnectedMapXAlignment = 0xd384
wSouthConnectedMapViewPointer = 0xd385
wMapConn3Ptr = 0xd387
wWestConnectionStripSrc = 0xd388
wWestConnectionStripDest = 0xd38a
wWestConnectionStripHeight = 0xd38c
wWestConnectedMapWidth = 0xd38d
wWestConnectedMapYAlignment = 0xd38e
wWestConnectedMapXAlignment = 0xd38f
wWestConnectedMapViewPointer = 0xd390
wMapConn4Ptr = 0xd392
wEastConnectionStripSrc = 0xd393
wEastConnectionStripDest = 0xd395
wEastConnectionStripHeight = 0xd397
wEastConnectedMapWidth = 0xd398
wEastConnectedMapYAlignment = 0xd399
wEastConnectedMapXAlignment = 0xd39a
wEastConnectedMapViewPointer = 0xd39b
wSpriteSet = 0xd39d
wSpriteSetID = 0xd3a8
wObjectDataPointerTemp = 0xd3a9
wMapBackgroundTile = 0xd3ad
wNumberOfWarps = 0xd3ae
wWarpEntries = 0xd3af
wDestinationWarpID = 0xd42f
wNumSigns = 0xd4b0
wSignCoords = 0xd4b1
wSignTextIDs = 0xd4d1
wNumSprites = 0xd4e1
wYOffsetSinceLastSpecialWarp = 0xd4e2
wXOffsetSinceLastSpecialWarp = 0xd4e3
wMapSpriteData = 0xd4e4
wMapSpriteExtraData = 0xd504
wCurrentMapHeight2 = 0xd524
wCurrentMapWidth2 = 0xd525
wMapViewVRAMPointer = 0xd526
wPlayerMovingDirection = 0xd528
wPlayerLastStopDirection = 0xd529
wPlayerDirection = 0xd52a
wTilesetBank = 0xd52b
wTilesetBlocksPtr = 0xd52c
wTilesetGfxPtr = 0xd52e
wTilesetCollisionPtr = 0xd530
wTilesetTalkingOverTiles = 0xd532
wGrassTile = 0xd535
wNumBoxItems = 0xd53a
wBoxItems = 0xd53b
wCurrentBoxNum = 0xd5a0
wNumHoFTeams = 0xd5a2
wUnusedD5A3 = 0xd5a3
wPlayerCoins = 0xd5a4
wMissableObjectFlags = 0xd5a6
wMissableObjectList = 0xd5ce
wGameProgressFlags = 0xd5f0
wOaksLabCurScript = 0xd5f0
wPalletTownCurScript = 0xd5f1
wBluesHouseCurScript = 0xd5f3
wViridianCityCurScript = 0xd5f4
wPewterCityCurScript = 0xd5f7
wRoute3CurScript = 0xd5f8
wRoute4CurScript = 0xd5f9
wViridianGymCurScript = 0xd5fb
wPewterGymCurScript = 0xd5fc
wCeruleanGymCurScript = 0xd5fd
wVermilionGymCurScript = 0xd5fe
wCeladonGymCurScript = 0xd5ff
wRoute6CurScript = 0xd600
wRoute8CurScript = 0xd601
wRoute24CurScript = 0xd602
wRoute25CurScript = 0xd603
wRoute9CurScript = 0xd604
wRoute10CurScript = 0xd605
wMtMoon1CurScript = 0xd606
wMtMoon3CurScript = 0xd607
wSSAnne8CurScript = 0xd608
wSSAnne9CurScript = 0xd609
wRoute22CurScript = 0xd60a
wRedsHouse2CurScript = 0xd60c
wViridianMarketCurScript = 0xd60d
wRoute22GateCurScript = 0xd60e
wCeruleanCityCurScript = 0xd60f
wSSAnne5CurScript = 0xd617
wViridianForestCurScript = 0xd618
wMuseum1fCurScript = 0xd619
wRoute13CurScript = 0xd61a
wRoute14CurScript = 0xd61b
wRoute17CurScript = 0xd61c
wRoute19CurScript = 0xd61d
wRoute21CurScript = 0xd61e
wSafariZoneEntranceCurScript = 0xd61f
wRockTunnel2CurScript = 0xd620
wRockTunnel1CurScript = 0xd621
wRoute11CurScript = 0xd623
wRoute12CurScript = 0xd624
wRoute15CurScript = 0xd625
wRoute16CurScript = 0xd626
wRoute18CurScript = 0xd627
wRoute20CurScript = 0xd628
wSSAnne10CurScript = 0xd629
wVermilionCityCurScript = 0xd62a
wPokemonTower2CurScript = 0xd62b
wPokemonTower3CurScript = 0xd62c
wPokemonTower4CurScript = 0xd62d
wPokemonTower5CurScript = 0xd62e
wPokemonTower6CurScript = 0xd62f
wPokemonTower7CurScript = 0xd630
wRocketHideout1CurScript = 0xd631
wRocketHideout2CurScript = 0xd632
wRocketHideout3CurScript = 0xd633
wRocketHideout4CurScript = 0xd634
wRoute6GateCurScript = 0xd636
wRoute8GateCurScript = 0xd637
wCinnabarIslandCurScript = 0xd639
wMansion1CurScript = 0xd63a
wMansion2CurScript = 0xd63c
wMansion3CurScript = 0xd63d
wMansion4CurScript = 0xd63e
wVictoryRoad2CurScript = 0xd63f
wVictoryRoad3CurScript = 0xd640
wFightingDojoCurScript = 0xd642
wSilphCo2CurScript = 0xd643
wSilphCo3CurScript = 0xd644
wSilphCo4CurScript = 0xd645
wSilphCo5CurScript = 0xd646
wSilphCo6CurScript = 0xd647
wSilphCo7CurScript = 0xd648
wSilphCo8CurScript = 0xd649
wSilphCo9CurScript = 0xd64a
wHallOfFameRoomCurScript = 0xd64b
wGaryCurScript = 0xd64c
wLoreleiCurScript = 0xd64d
wBrunoCurScript = 0xd64e
wAgathaCurScript = 0xd64f
wUnknownDungeon3CurScript = 0xd650
wVictoryRoad1CurScript = 0xd651
wLanceCurScript = 0xd653
wSilphCo10CurScript = 0xd658
wSilphCo11CurScript = 0xd659
wFuchsiaGymCurScript = 0xd65b
wSaffronGymCurScript = 0xd65c
wCinnabarGymCurScript = 0xd65e
wCeladonGameCornerCurScript = 0xd65f
wRoute16GateCurScript = 0xd660
wBillsHouseCurScript = 0xd661
wRoute5GateCurScript = 0xd662
wPowerPlantCurScript = 0xd663
wRoute7GateCurScript = 0xd663
wSSAnne2CurScript = 0xd665
wSeafoamIslands4CurScript = 0xd666
wRoute23CurScript = 0xd667
wSeafoamIslands5CurScript = 0xd668
wRoute18GateCurScript = 0xd669
wWalkBikeSurfState = 0xd700
wTownVisitedFlag = 0xd70b
wSafariSteps = 0xd70d
wFossilItem = 0xd70f
wFossilMon = 0xd710
wEnemyMonOrTrainerClass = 0xd713
wPlayerJumpingYScreenCoordsIndex = 0xd714
wRivalStarter = 0xd715
wPlayerStarter = 0xd717
wBoulderSpriteIndex = 0xd718
wLastBlackoutMap = 0xd719
wDestinationMap = 0xd71a
wUnusedD71B = 0xd71b
wTileInFrontOfBoulderAndBoulderCollisionResult = 0xd71c
wDungeonWarpDestinationMap = 0xd71d
wWhichDungeonWarp = 0xd71e
wUnusedD71F = 0xd71f
wd728 = 0xd728
wBeatGymFlags = 0xd72a
wd72c = 0xd72c
wd72d = 0xd72d
wd72e = 0xd72e
wd730 = 0xd730
wd732 = 0xd732
wFlags_D733 = 0xd733
wBeatLorelei = 0xd734
wd736 = 0xd736
wCompletedInGameTradeFlags = 0xd737
wWarpedFromWhichWarp = 0xd73b
wWarpedFromWhichMap = 0xd73c
wCardKeyDoorY = 0xd73f
wCardKeyDoorX = 0xd740
wFirstLockTrashCanIndex = 0xd743
wSecondLockTrashCanIndex = 0xd744
wEventFlags = 0xd747
wLinkEnemyTrainerName = 0xd887
wGrassRate = 0xd887
wGrassMons = 0xd888
wSerialEnemyDataBlock = 0xd893
wEnemyMons = 0xd8a4
wTrainerHeaderPtr = 0xda30
wOpponentAfterWrongAnswer = 0xda38
wUnusedDA38 = 0xda38
wCurMapScript = 0xda39
wPlayTimeHours = 0xda41
wPlayTimeMaxed = 0xda42
wPlayTimeMinutes = 0xda43
wPlayTimeSeconds = 0xda44
wPlayTimeFrames = 0xda45
wSafariZoneGameOver = 0xda46
wNumSafariBalls = 0xda47
wDayCareInUse = 0xda48
wBoxMonNicksEnd = 0xdee2
wStack = 0xdfff


items_dict = {
    1: {'decimal': 1, 'hex': '0x01', 'Item': 'Master Ball'},
    2: {'decimal': 2, 'hex': '0x02', 'Item': 'Ultra Ball'},
    3: {'decimal': 3, 'hex': '0x03', 'Item': 'Great Ball'},
    4: {'decimal': 4, 'hex': '0x04', 'Item': 'Poké Ball'},
    5: {'decimal': 5, 'hex': '0x05', 'Item': 'Town Map'},
    6: {'decimal': 6, 'hex': '0x06', 'Item': 'Bicycle'},
    7: {'decimal': 7, 'hex': '0x07', 'Item': '?????'},
    8: {'decimal': 8, 'hex': '0x08', 'Item': 'Safari Ball'},
    9: {'decimal': 9, 'hex': '0x09', 'Item': 'Pokédex'},
    10: {'decimal': 10, 'hex': '0x0A', 'Item': 'Moon Stone'},
    11: {'decimal': 11, 'hex': '0x0B', 'Item': 'Antidote'},
    12: {'decimal': 12, 'hex': '0x0C', 'Item': 'Burn Heal'},
    13: {'decimal': 13, 'hex': '0x0D', 'Item': 'Ice Heal'},
    14: {'decimal': 14, 'hex': '0x0E', 'Item': 'Awakening'},
    15: {'decimal': 15, 'hex': '0x0F', 'Item': 'Parlyz Heal'},
    16: {'decimal': 16, 'hex': '0x10', 'Item': 'Full Restore'},
    17: {'decimal': 17, 'hex': '0x11', 'Item': 'Max Potion'},
    18: {'decimal': 18, 'hex': '0x12', 'Item': 'Hyper Potion'},
    19: {'decimal': 19, 'hex': '0x13', 'Item': 'Super Potion'},
    20: {'decimal': 20, 'hex': '0x14', 'Item': 'Potion'},
    21: {'decimal': 21, 'hex': '0x15', 'Item': 'BoulderBadge'},
    22: {'decimal': 22, 'hex': '0x16', 'Item': 'CascadeBadge'},
    23: {'decimal': 23, 'hex': '0x17', 'Item': 'ThunderBadge'},
    24: {'decimal': 24, 'hex': '0x18', 'Item': 'RainbowBadge'},
    25: {'decimal': 25, 'hex': '0x19', 'Item': 'SoulBadge'},
    26: {'decimal': 26, 'hex': '0x1A', 'Item': 'MarshBadge'},
    27: {'decimal': 27, 'hex': '0x1B', 'Item': 'VolcanoBadge'},
    28: {'decimal': 28, 'hex': '0x1C', 'Item': 'EarthBadge'},
    29: {'decimal': 29, 'hex': '0x1D', 'Item': 'Escape Rope'},
    30: {'decimal': 30, 'hex': '0x1E', 'Item': 'Repel'},
    31: {'decimal': 31, 'hex': '0x1F', 'Item': 'Old Amber'},
    32: {'decimal': 32, 'hex': '0x20', 'Item': 'Fire Stone'},
    33: {'decimal': 33, 'hex': '0x21', 'Item': 'Thunderstone'},
    34: {'decimal': 34, 'hex': '0x22', 'Item': 'Water Stone'},
    35: {'decimal': 35, 'hex': '0x23', 'Item': 'HP Up'},
    36: {'decimal': 36, 'hex': '0x24', 'Item': 'Protein'},
    37: {'decimal': 37, 'hex': '0x25', 'Item': 'Iron'},
    38: {'decimal': 38, 'hex': '0x26', 'Item': 'Carbos'},
    39: {'decimal': 39, 'hex': '0x27', 'Item': 'Calcium'},
    40: {'decimal': 40, 'hex': '0x28', 'Item': 'Rare Candy'},
    41: {'decimal': 41, 'hex': '0x29', 'Item': 'Dome Fossil'},
    42: {'decimal': 42, 'hex': '0x2A', 'Item': 'Helix Fossil'},
    43: {'decimal': 43, 'hex': '0x2B', 'Item': 'Secret Key'},
    44: {'decimal': 44, 'hex': '0x2C', 'Item': '?????'},
    45: {'decimal': 45, 'hex': '0x2D', 'Item': 'Bike Voucher'},
    46: {'decimal': 46, 'hex': '0x2E', 'Item': 'X Accuracy'},
    47: {'decimal': 47, 'hex': '0x2F', 'Item': 'Leaf Stone'},
    48: {'decimal': 48, 'hex': '0x30', 'Item': 'Card Key'},
    49: {'decimal': 49, 'hex': '0x31', 'Item': 'Nugget'},
    50: {'decimal': 50, 'hex': '0x32', 'Item': 'PP Up*'},
    51: {'decimal': 51, 'hex': '0x33', 'Item': 'Poké Doll'},
    52: {'decimal': 52, 'hex': '0x34', 'Item': 'Full Heal'},
    53: {'decimal': 53, 'hex': '0x35', 'Item': 'Revive'},
    54: {'decimal': 54, 'hex': '0x36', 'Item': 'Max Revive'},
    55: {'decimal': 55, 'hex': '0x37', 'Item': 'Guard Spec.'},
    56: {'decimal': 56, 'hex': '0x38', 'Item': 'Super Repel'},
    57: {'decimal': 57, 'hex': '0x39', 'Item': 'Max Repel'},
    58: {'decimal': 58, 'hex': '0x3A', 'Item': 'Dire Hit'},
    59: {'decimal': 59, 'hex': '0x3B', 'Item': 'Coin'},
    60: {'decimal': 60, 'hex': '0x3C', 'Item': 'Fresh Water'},
    61: {'decimal': 61, 'hex': '0x3D', 'Item': 'Soda Pop'},
    62: {'decimal': 62, 'hex': '0x3E', 'Item': 'Lemonade'},
    63: {'decimal': 63, 'hex': '0x3F', 'Item': 'S.S. Ticket'},
    64: {'decimal': 64, 'hex': '0x40', 'Item': 'Gold Teeth'},
    65: {'decimal': 65, 'hex': '0x41', 'Item': 'X Attack'},
    66: {'decimal': 66, 'hex': '0x42', 'Item': 'X Defend'},
    67: {'decimal': 67, 'hex': '0x43', 'Item': 'X Speed'},
    68: {'decimal': 68, 'hex': '0x44', 'Item': 'X Special'},
    69: {'decimal': 69, 'hex': '0x45', 'Item': 'Coin Case'},
    70: {'decimal': 70, 'hex': '0x46', 'Item': "Oak's Parcel"},
    71: {'decimal': 71, 'hex': '0x47', 'Item': 'Itemfinder'},
    72: {'decimal': 72, 'hex': '0x48', 'Item': 'Silph Scope'},
    73: {'decimal': 73, 'hex': '0x49', 'Item': 'Poké Flute'},
    74: {'decimal': 74, 'hex': '0x4A', 'Item': 'Lift Key'},
    75: {'decimal': 75, 'hex': '0x4B', 'Item': 'Exp. All'},
    76: {'decimal': 76, 'hex': '0x4C', 'Item': 'Old Rod'},
    77: {'decimal': 77, 'hex': '0x4D', 'Item': 'Good Rod'},
    78: {'decimal': 78, 'hex': '0x4E', 'Item': 'Super Rod'},
    79: {'decimal': 79, 'hex': '0x4F', 'Item': 'PP Up'},
    80: {'decimal': 80, 'hex': '0x50', 'Item': 'Ether'},
    81: {'decimal': 81, 'hex': '0x51', 'Item': 'Max Ether'},
    82: {'decimal': 82, 'hex': '0x52', 'Item': 'Elixer'},
    83: {'decimal': 83, 'hex': '0x53', 'Item': 'Max Elixer'},
    196: {'decimal': 196, 'hex': '0xC4', 'Item': 'HM01'},
    197: {'decimal': 197, 'hex': '0xC5', 'Item': 'HM02'},
    198: {'decimal': 198, 'hex': '0xC6', 'Item': 'HM03'},
    199: {'decimal': 199, 'hex': '0xC7', 'Item': 'HM04'},
    200: {'decimal': 200, 'hex': '0xC8', 'Item': 'HM05'},
    201: {'decimal': 201, 'hex': '0xC9', 'Item': 'TM01'},
    202: {'decimal': 202, 'hex': '0xCA', 'Item': 'TM02'},
    203: {'decimal': 203, 'hex': '0xCB', 'Item': 'TM03'},
    204: {'decimal': 204, 'hex': '0xCC', 'Item': 'TM04'},
    205: {'decimal': 205, 'hex': '0xCD', 'Item': 'TM05'},
    206: {'decimal': 206, 'hex': '0xCE', 'Item': 'TM06'},
    207: {'decimal': 207, 'hex': '0xCF', 'Item': 'TM07'},
    208: {'decimal': 208, 'hex': '0xD0', 'Item': 'TM08'},
    209: {'decimal': 209, 'hex': '0xD1', 'Item': 'TM09'},
    210: {'decimal': 210, 'hex': '0xD2', 'Item': 'TM10'},
    211: {'decimal': 211, 'hex': '0xD3', 'Item': 'TM11'},
    212: {'decimal': 212, 'hex': '0xD4', 'Item': 'TM12'},
    213: {'decimal': 213, 'hex': '0xD5', 'Item': 'TM13'},
    214: {'decimal': 214, 'hex': '0xD6', 'Item': 'TM14'},
    215: {'decimal': 215, 'hex': '0xD7', 'Item': 'TM15'},
    216: {'decimal': 216, 'hex': '0xD8', 'Item': 'TM16'},
    217: {'decimal': 217, 'hex': '0xD9', 'Item': 'TM17'},
    218: {'decimal': 218, 'hex': '0xDA', 'Item': 'TM18'},
    219: {'decimal': 219, 'hex': '0xDB', 'Item': 'TM19'},
    220: {'decimal': 220, 'hex': '0xDC', 'Item': 'TM20'},
    221: {'decimal': 221, 'hex': '0xDD', 'Item': 'TM21'},
    222: {'decimal': 222, 'hex': '0xDE', 'Item': 'TM22'},
    223: {'decimal': 223, 'hex': '0xDF', 'Item': 'TM23'},
    224: {'decimal': 224, 'hex': '0xE0', 'Item': 'TM24'},
    225: {'decimal': 225, 'hex': '0xE1', 'Item': 'TM25'},
    226: {'decimal': 226, 'hex': '0xE2', 'Item': 'TM26'},
    227: {'decimal': 227, 'hex': '0xE3', 'Item': 'TM27'},
    228: {'decimal': 228, 'hex': '0xE4', 'Item': 'TM28'},
    229: {'decimal': 229, 'hex': '0xE5', 'Item': 'TM29'},
    230: {'decimal': 230, 'hex': '0xE6', 'Item': 'TM30'},
    231: {'decimal': 231, 'hex': '0xE7', 'Item': 'TM31'},
    232: {'decimal': 232, 'hex': '0xE8', 'Item': 'TM32'},
    233: {'decimal': 233, 'hex': '0xE9', 'Item': 'TM33'},
    234: {'decimal': 234, 'hex': '0xEA', 'Item': 'TM34'},
    235: {'decimal': 235, 'hex': '0xEB', 'Item': 'TM35'},
    236: {'decimal': 236, 'hex': '0xEC', 'Item': 'TM36'},
    237: {'decimal': 237, 'hex': '0xED', 'Item': 'TM37'},
    238: {'decimal': 238, 'hex': '0xEE', 'Item': 'TM38'},
    239: {'decimal': 239, 'hex': '0xEF', 'Item': 'TM39'},
    240: {'decimal': 240, 'hex': '0xF0', 'Item': 'TM40'},
    241: {'decimal': 241, 'hex': '0xF1', 'Item': 'TM41'},
    242: {'decimal': 242, 'hex': '0xF2', 'Item': 'TM42'},
    243: {'decimal': 243, 'hex': '0xF3', 'Item': 'TM43'},
    244: {'decimal': 244, 'hex': '0xF4', 'Item': 'TM44'},
    245: {'decimal': 245, 'hex': '0xF5', 'Item': 'TM45'},
    246: {'decimal': 246, 'hex': '0xF6', 'Item': 'TM46'},
    247: {'decimal': 247, 'hex': '0xF7', 'Item': 'TM47'},
    248: {'decimal': 248, 'hex': '0xF8', 'Item': 'TM48'},
    249: {'decimal': 249, 'hex': '0xF9', 'Item': 'TM49'},
    250: {'decimal': 250, 'hex': '0xFA', 'Item': 'TM50'},
    251: {'decimal': 251, 'hex': '0xFB', 'Item': 'TM51'},
    252: {'decimal': 252, 'hex': '0xFC', 'Item': 'TM52'},
    253: {'decimal': 253, 'hex': '0xFD', 'Item': 'TM53'},
    254: {'decimal': 254, 'hex': '0xFE', 'Item': 'TM54'},
    255: {'decimal': 255, 'hex': '0xFF', 'Item': 'TM55'},
}

pokemon_data = [
    {'hex': '1', 'decimal': '1', 'name': 'Rhydon'},
    {'hex': '2', 'decimal': '2', 'name': 'Kangaskhan'},
    {'hex': '3', 'decimal': '3', 'name': 'Nidoran♂'},
    {'hex': '4', 'decimal': '4', 'name': 'Clefairy'},
    {'hex': '5', 'decimal': '5', 'name': 'Spearow'},
    {'hex': '6', 'decimal': '6', 'name': 'Voltorb', 'type': 'Electric'},
    {'hex': '7', 'decimal': '7', 'name': 'Nidoking'},
    {'hex': '8', 'decimal': '8', 'name': 'Slowbro'},
    {'hex': '9', 'decimal': '9', 'name': 'Ivysaur'},
    {'hex': 'A', 'decimal': '10', 'name': 'Exeggutor'},
    {'hex': 'B', 'decimal': '11', 'name': 'Lickitung'},
    {'hex': 'C', 'decimal': '12', 'name': 'Exeggcute'},
    {'hex': 'D', 'decimal': '13', 'name': 'Grimer'},
    {'hex': 'E', 'decimal': '14', 'name': 'Gengar', 'type': 'Ghost'},
    {'hex': 'F', 'decimal': '15', 'name': 'Nidoran♀'},
    {'hex': '10', 'decimal': '16', 'name': 'Nidoqueen'},
    {'hex': '11', 'decimal': '17', 'name': 'Cubone'},
    {'hex': '12', 'decimal': '18', 'name': 'Rhyhorn'},
    {'hex': '13', 'decimal': '19', 'name': 'Lapras', 'type': 'Ice'},
    {'hex': '14', 'decimal': '20', 'name': 'Arcanine'},
    {'hex': '15', 'decimal': '21', 'name': 'Mew'},
    {'hex': '16', 'decimal': '22', 'name': 'Gyarados'},
    {'hex': '17', 'decimal': '23', 'name': 'Shellder'},
    {'hex': '18', 'decimal': '24', 'name': 'Tentacool'},
    {'hex': '19', 'decimal': '25', 'name': 'Gastly', 'type': 'Ghost'},
    {'hex': '1A', 'decimal': '26', 'name': 'Scyther', 'type': 'Bug'},
    {'hex': '1B', 'decimal': '27', 'name': 'Staryu'},
    {'hex': '1C', 'decimal': '28', 'name': 'Blastoise'},
    {'hex': '1D', 'decimal': '29', 'name': 'Pinsir', 'type': 'Bug'},
    {'hex': '1E', 'decimal': '30', 'name': 'Tangela'},
    {'hex': '1F', 'decimal': '31', 'name': 'MissingNo. (Scizor)'},
    {'hex': '20', 'decimal': '32', 'name': 'MissingNo. (Shuckle)'},
    {'hex': '21', 'decimal': '33', 'name': 'Growlithe'},
    {'hex': '22', 'decimal': '34', 'name': 'Onix'},
    {'hex': '23', 'decimal': '35', 'name': 'Fearow'},
    {'hex': '24', 'decimal': '36', 'name': 'Pidgey'},
    {'hex': '25', 'decimal': '37', 'name': 'Slowpoke'},
    {'hex': '26', 'decimal': '38', 'name': 'Kadabra'},
    {'hex': '27', 'decimal': '39', 'name': 'Graveler'},
    {'hex': '28', 'decimal': '40', 'name': 'Chansey'},
    {'hex': '29', 'decimal': '41', 'name': 'Machoke'},
    {'hex': '2A', 'decimal': '42', 'name': 'Mr. Mime'},
    {'hex': '2B', 'decimal': '43', 'name': 'Hitmonlee'},
    {'hex': '2C', 'decimal': '44', 'name': 'Hitmonchan'},
    {'hex': '2D', 'decimal': '45', 'name': 'Arbok'},
    {'hex': '2E', 'decimal': '46', 'name': 'Parasect', 'type': 'Bug'},
    {'hex': '2F', 'decimal': '47', 'name': 'Psyduck'},
    {'hex': '30', 'decimal': '48', 'name': 'Drowzee'},
    {'hex': '31', 'decimal': '49', 'name': 'Golem'},
    {'hex': '32', 'decimal': '50', 'name': 'MissingNo. (Heracross)'},
    {'hex': '33', 'decimal': '51', 'name': 'Magmar'},
    {'hex': '34', 'decimal': '52', 'name': 'MissingNo. (Ho-Oh)'},
    {'hex': '35', 'decimal': '53', 'name': 'Electabuzz', 'type': 'Electric'},
    {'hex': '36', 'decimal': '54', 'name': 'Magneton', 'type': 'Electric'},
    {'hex': '37', 'decimal': '55', 'name': 'Koffing'},
    {'hex': '38', 'decimal': '56', 'name': 'MissingNo. (Sneasel)'},
    {'hex': '39', 'decimal': '57', 'name': 'Mankey'},
    {'hex': '3A', 'decimal': '58', 'name': 'Seel'},
    {'hex': '3B', 'decimal': '59', 'name': 'Diglett'},
    {'hex': '3C', 'decimal': '60', 'name': 'Tauros'},
    {'hex': '3D', 'decimal': '61', 'name': 'MissingNo. (Teddiursa)'},
    {'hex': '3E', 'decimal': '62', 'name': 'MissingNo. (Ursaring)'},
    {'hex': '3F', 'decimal': '63', 'name': 'MissingNo. (Slugma)'},
    {'hex': '40', 'decimal': '64', 'name': 'Farfetch\'d'},
    {'hex': '41', 'decimal': '65', 'name': 'Venonat', 'type': 'Bug'},
    {'hex': '42', 'decimal': '66', 'name': 'Dragonite', 'type': 'Dragon'},
    {'hex': '43', 'decimal': '67', 'name': 'MissingNo. (Magcargo)'},
    {'hex': '44', 'decimal': '68', 'name': 'MissingNo. (Swinub)'},
    {'hex': '45', 'decimal': '69', 'name': 'MissingNo. (Piloswine)'},
    {'hex': '46', 'decimal': '70', 'name': 'Doduo'},
    {'hex': '47', 'decimal': '71', 'name': 'Poliwag'},
    {'hex': '48', 'decimal': '72', 'name': 'Jynx', 'type': 'Ice'},
    {'hex': '49', 'decimal': '73', 'name': 'Moltres'},
    {'hex': '4A', 'decimal': '74', 'name': 'Articuno', 'type': 'Ice'},
    {'hex': '4B', 'decimal': '75', 'name': 'Zapdos', 'type': 'Electric'},
    {'hex': '4C', 'decimal': '76', 'name': 'Ditto'},
    {'hex': '4D', 'decimal': '77', 'name': 'Meowth'},
    {'hex': '4E', 'decimal': '78', 'name': 'Krabby'},
    {'hex': '4F', 'decimal': '79', 'name': 'MissingNo. (Corsola)'},
    {'hex': '50', 'decimal': '80', 'name': 'MissingNo. (Remoraid)'},
    {'hex': '51', 'decimal': '81', 'name': 'MissingNo. (Octillery)'},
    {'hex': '52', 'decimal': '82', 'name': 'Vulpix'},
    {'hex': '53', 'decimal': '83', 'name': 'Ninetales'},
    {'hex': '54', 'decimal': '84', 'name': 'Pikachu', 'type': 'Electric'},
    {'hex': '55', 'decimal': '85', 'name': 'Raichu', 'type': 'Electric'},
    {'hex': '56', 'decimal': '86', 'name': 'MissingNo. (Deli)'},
    {'hex': '57', 'decimal': '87', 'name': 'MissingNo. (Mantine)'},
    {'hex': '58', 'decimal': '88', 'name': 'Dratini', 'type': 'Dragon'},
    {'hex': '59', 'decimal': '89', 'name': 'Dragonair', 'type': 'Dragon'},
    {'hex': '5A', 'decimal': '90', 'name': 'Kabuto'},
    {'hex': '5B', 'decimal': '91', 'name': 'Kabutops'},
    {'hex': '5C', 'decimal': '92', 'name': 'Horsea'},
    {'hex': '5D', 'decimal': '93', 'name': 'Seadra'},
    {'hex': '5E', 'decimal': '94', 'name': 'MissingNo. (Skarmory)'},
    {'hex': '5F', 'decimal': '95', 'name': 'MissingNo. (Houndour)'},
    {'hex': '60', 'decimal': '96', 'name': 'Sandshrew'},
    {'hex': '61', 'decimal': '97', 'name': 'Sandslash'},
    {'hex': '62', 'decimal': '98', 'name': 'Omanyte'},
    {'hex': '63', 'decimal': '99', 'name': 'Omastar'},
    {'hex': '64', 'decimal': '100', 'name': 'Jigglypuff'},
    {'hex': '65', 'decimal': '101', 'name': 'Wigglytuff'},
    {'hex': '66', 'decimal': '102', 'name': 'Eevee'},
    {'hex': '67', 'decimal': '103', 'name': 'Flareon'},
    {'hex': '68', 'decimal': '104', 'name': 'Jolteon', 'type': 'Electric'},
    {'hex': '69', 'decimal': '105', 'name': 'Vaporeon'},
    {'hex': '6A', 'decimal': '106', 'name': 'Machop'},
    {'hex': '6B', 'decimal': '107', 'name': 'Zubat'},
    {'hex': '6C', 'decimal': '108', 'name': 'Ekans'},
    {'hex': '6D', 'decimal': '109', 'name': 'Paras', 'type': 'Bug'},
    {'hex': '6E', 'decimal': '110', 'name': 'Poliwhirl'},
    {'hex': '6F', 'decimal': '111', 'name': 'Poliwrath'},
    {'hex': '70', 'decimal': '112', 'name': 'Weedle', 'type': 'Bug'},
    {'hex': '71', 'decimal': '113', 'name': 'Kakuna', 'type': 'Bug'},
    {'hex': '72', 'decimal': '114', 'name': 'Beedrill', 'type': 'Bug'},
    {'hex': '73', 'decimal': '115', 'name': 'MissingNo. (Houndoom)'},
    {'hex': '74', 'decimal': '116', 'name': 'Dodrio'},
    {'hex': '75', 'decimal': '117', 'name': 'Primeape'},
    {'hex': '76', 'decimal': '118', 'name': 'Dugtrio'},
    {'hex': '77', 'decimal': '119', 'name': 'Venomoth', 'type': 'Bug'},
    {'hex': '78', 'decimal': '120', 'name': 'Dewgong', 'type': 'Ice'},
    {'hex': '79', 'decimal': '121', 'name': 'MissingNo. (Kingdra)'},
    {'hex': '7A', 'decimal': '122', 'name': 'MissingNo. (Phanpy)'},
    {'hex': '7B', 'decimal': '123', 'name': 'Caterpie', 'type': 'Bug'},
    {'hex': '7C', 'decimal': '124', 'name': 'Metapod', 'type': 'Bug'},
    {'hex': '7D', 'decimal': '125', 'name': 'Butterfree', 'type': 'Bug'},
    {'hex': '7E', 'decimal': '126', 'name': 'Machamp'},
    {'hex': '7F', 'decimal': '127', 'name': 'MissingNo. (Donphan)'},
    {'hex': '80', 'decimal': '128', 'name': 'Golduck'},
    {'hex': '81', 'decimal': '129', 'name': 'Hypno'},
    {'hex': '82', 'decimal': '130', 'name': 'Golbat'},
    {'hex': '83', 'decimal': '131', 'name': 'Mewtwo'},
    {'hex': '84', 'decimal': '132', 'name': 'Snorlax'},
    {'hex': '85', 'decimal': '133', 'name': 'Magikarp'},
    {'hex': '86', 'decimal': '134', 'name': 'MissingNo. (Porygon2)'},
    {'hex': '87', 'decimal': '135', 'name': 'MissingNo. (Stantler)'},
    {'hex': '88', 'decimal': '136', 'name': 'Muk'},
    {'hex': '89', 'decimal': '137', 'name': 'MissingNo. (Smeargle)'},
    {'hex': '8A', 'decimal': '138', 'name': 'Kingler'},
    {'hex': '8B', 'decimal': '139', 'name': 'Cloyster'},
    {'hex': '8D', 'decimal': '141', 'name': 'Electrode'},
    {'hex': '8E', 'decimal': '142', 'name': 'Clefable'},
    {'hex': '8F', 'decimal': '143', 'name': 'Weezing'},
    {'hex': '90', 'decimal': '144', 'name': 'Persian'},
    {'hex': '91', 'decimal': '145', 'name': 'Marowak'},
    {'hex': '93', 'decimal': '147', 'name': 'Haunter'},
    {'hex': '94', 'decimal': '148', 'name': 'Abra'},
    {'hex': '95', 'decimal': '149', 'name': 'Alakazam'},
    {'hex': '96', 'decimal': '150', 'name': 'Pidgeotto'},
    {'hex': '97', 'decimal': '151', 'name': 'Pidgeot'},
    {'hex': '98', 'decimal': '152', 'name': 'Starmie'},
    {'hex': '99', 'decimal': '153', 'name': 'Bulbasaur'},
    {'hex': '9A', 'decimal': '154', 'name': 'Venusaur'},
    {'hex': '9B', 'decimal': '155', 'name': 'Tentacruel'},
    {'hex': '9D', 'decimal': '157', 'name': 'Goldeen'},
    {'hex': '9E', 'decimal': '158', 'name': 'Seaking'},
    {'hex': 'A3', 'decimal': '163', 'name': 'Ponyta'},
    {'hex': 'A4', 'decimal': '164', 'name': 'Rapidash'},
    {'hex': 'A5', 'decimal': '165', 'name': 'Rattata'},
    {'hex': 'A6', 'decimal': '166', 'name': 'Raticate'},
    {'hex': 'A7', 'decimal': '167', 'name': 'Nidorino'},
    {'hex': 'A8', 'decimal': '168', 'name': 'Nidorina'},
    {'hex': 'A9', 'decimal': '169', 'name': 'Geodude'},
    {'hex': 'AA', 'decimal': '170', 'name': 'Porygon'},
    {'hex': 'AB', 'decimal': '171', 'name': 'Aerodactyl'},
    {'hex': 'AD', 'decimal': '173', 'name': 'Magnemite'},
    {'hex': 'B0', 'decimal': '176', 'name': 'Charmander'},
    {'hex': 'B1', 'decimal': '177', 'name': 'Squirtle'},
    {'hex': 'B2', 'decimal': '178', 'name': 'Charmeleon'},
    {'hex': 'B3', 'decimal': '179', 'name': 'Wartortle'},
    {'hex': 'B4', 'decimal': '180', 'name': 'Charizard'},
    {'hex': 'B9', 'decimal': '185', 'name': 'Oddish'},
    {'hex': 'BA', 'decimal': '186', 'name': 'Gloom'},
    {'hex': 'BB', 'decimal': '187', 'name': 'Vileplume'},
    {'hex': 'BC', 'decimal': '188', 'name': 'Bellsprout'},
    {'hex': 'BD', 'decimal': '189', 'name': 'Weepinbell'},
    {'hex': 'BE', 'decimal': '190', 'name': 'Victreebel'}
]


items_dict = {
    1: {'decimal': 1, 'hex': '0x01', 'Item': 'Master Ball'},
    2: {'decimal': 2, 'hex': '0x02', 'Item': 'Ultra Ball'},
    3: {'decimal': 3, 'hex': '0x03', 'Item': 'Great Ball'},
    4: {'decimal': 4, 'hex': '0x04', 'Item': 'Poké Ball'},
    5: {'decimal': 5, 'hex': '0x05', 'Item': 'Town Map'},
    6: {'decimal': 6, 'hex': '0x06', 'Item': 'Bicycle'},
    7: {'decimal': 7, 'hex': '0x07', 'Item': '?????'},
    8: {'decimal': 8, 'hex': '0x08', 'Item': 'Safari Ball'},
    9: {'decimal': 9, 'hex': '0x09', 'Item': 'Pokédex'},
    10: {'decimal': 10, 'hex': '0x0A', 'Item': 'Moon Stone'},
    11: {'decimal': 11, 'hex': '0x0B', 'Item': 'Antidote'},
    12: {'decimal': 12, 'hex': '0x0C', 'Item': 'Burn Heal'},
    13: {'decimal': 13, 'hex': '0x0D', 'Item': 'Ice Heal'},
    14: {'decimal': 14, 'hex': '0x0E', 'Item': 'Awakening'},
    15: {'decimal': 15, 'hex': '0x0F', 'Item': 'Parlyz Heal'},
    16: {'decimal': 16, 'hex': '0x10', 'Item': 'Full Restore'},
    17: {'decimal': 17, 'hex': '0x11', 'Item': 'Max Potion'},
    18: {'decimal': 18, 'hex': '0x12', 'Item': 'Hyper Potion'},
    19: {'decimal': 19, 'hex': '0x13', 'Item': 'Super Potion'},
    20: {'decimal': 20, 'hex': '0x14', 'Item': 'Potion'},
    21: {'decimal': 21, 'hex': '0x15', 'Item': 'BoulderBadge'},
    22: {'decimal': 22, 'hex': '0x16', 'Item': 'CascadeBadge'},
    23: {'decimal': 23, 'hex': '0x17', 'Item': 'ThunderBadge'},
    24: {'decimal': 24, 'hex': '0x18', 'Item': 'RainbowBadge'},
    25: {'decimal': 25, 'hex': '0x19', 'Item': 'SoulBadge'},
    26: {'decimal': 26, 'hex': '0x1A', 'Item': 'MarshBadge'},
    27: {'decimal': 27, 'hex': '0x1B', 'Item': 'VolcanoBadge'},
    28: {'decimal': 28, 'hex': '0x1C', 'Item': 'EarthBadge'},
    29: {'decimal': 29, 'hex': '0x1D', 'Item': 'Escape Rope'},
    30: {'decimal': 30, 'hex': '0x1E', 'Item': 'Repel'},
    31: {'decimal': 31, 'hex': '0x1F', 'Item': 'Old Amber'},
    32: {'decimal': 32, 'hex': '0x20', 'Item': 'Fire Stone'},
    33: {'decimal': 33, 'hex': '0x21', 'Item': 'Thunderstone'},
    34: {'decimal': 34, 'hex': '0x22', 'Item': 'Water Stone'},
    35: {'decimal': 35, 'hex': '0x23', 'Item': 'HP Up'},
    36: {'decimal': 36, 'hex': '0x24', 'Item': 'Protein'},
    37: {'decimal': 37, 'hex': '0x25', 'Item': 'Iron'},
    38: {'decimal': 38, 'hex': '0x26', 'Item': 'Carbos'},
    39: {'decimal': 39, 'hex': '0x27', 'Item': 'Calcium'},
    40: {'decimal': 40, 'hex': '0x28', 'Item': 'Rare Candy'},
    41: {'decimal': 41, 'hex': '0x29', 'Item': 'Dome Fossil'},
    42: {'decimal': 42, 'hex': '0x2A', 'Item': 'Helix Fossil'},
    43: {'decimal': 43, 'hex': '0x2B', 'Item': 'Secret Key'},
    44: {'decimal': 44, 'hex': '0x2C', 'Item': '?????'},
    45: {'decimal': 45, 'hex': '0x2D', 'Item': 'Bike Voucher'},
    46: {'decimal': 46, 'hex': '0x2E', 'Item': 'X Accuracy'},
    47: {'decimal': 47, 'hex': '0x2F', 'Item': 'Leaf Stone'},
    48: {'decimal': 48, 'hex': '0x30', 'Item': 'Card Key'},
    49: {'decimal': 49, 'hex': '0x31', 'Item': 'Nugget'},
    50: {'decimal': 50, 'hex': '0x32', 'Item': 'PP Up*'},
    51: {'decimal': 51, 'hex': '0x33', 'Item': 'Poké Doll'},
    52: {'decimal': 52, 'hex': '0x34', 'Item': 'Full Heal'},
    53: {'decimal': 53, 'hex': '0x35', 'Item': 'Revive'},
    54: {'decimal': 54, 'hex': '0x36', 'Item': 'Max Revive'},
    55: {'decimal': 55, 'hex': '0x37', 'Item': 'Guard Spec.'},
    56: {'decimal': 56, 'hex': '0x38', 'Item': 'Super Repel'},
    57: {'decimal': 57, 'hex': '0x39', 'Item': 'Max Repel'},
    58: {'decimal': 58, 'hex': '0x3A', 'Item': 'Dire Hit'},
    59: {'decimal': 59, 'hex': '0x3B', 'Item': 'Coin'},
    60: {'decimal': 60, 'hex': '0x3C', 'Item': 'Fresh Water'},
    61: {'decimal': 61, 'hex': '0x3D', 'Item': 'Soda Pop'},
    62: {'decimal': 62, 'hex': '0x3E', 'Item': 'Lemonade'},
    63: {'decimal': 63, 'hex': '0x3F', 'Item': 'S.S. Ticket'},
    64: {'decimal': 64, 'hex': '0x40', 'Item': 'Gold Teeth'},
    65: {'decimal': 65, 'hex': '0x41', 'Item': 'X Attack'},
    66: {'decimal': 66, 'hex': '0x42', 'Item': 'X Defend'},
    67: {'decimal': 67, 'hex': '0x43', 'Item': 'X Speed'},
    68: {'decimal': 68, 'hex': '0x44', 'Item': 'X Special'},
    69: {'decimal': 69, 'hex': '0x45', 'Item': 'Coin Case'},
    70: {'decimal': 70, 'hex': '0x46', 'Item': "Oak's Parcel"},
    71: {'decimal': 71, 'hex': '0x47', 'Item': 'Itemfinder'},
    72: {'decimal': 72, 'hex': '0x48', 'Item': 'Silph Scope'},
    73: {'decimal': 73, 'hex': '0x49', 'Item': 'Poké Flute'},
    74: {'decimal': 74, 'hex': '0x4A', 'Item': 'Lift Key'},
    75: {'decimal': 75, 'hex': '0x4B', 'Item': 'Exp. All'},
    76: {'decimal': 76, 'hex': '0x4C', 'Item': 'Old Rod'},
    77: {'decimal': 77, 'hex': '0x4D', 'Item': 'Good Rod'},
    78: {'decimal': 78, 'hex': '0x4E', 'Item': 'Super Rod'},
    79: {'decimal': 79, 'hex': '0x4F', 'Item': 'PP Up'},
    80: {'decimal': 80, 'hex': '0x50', 'Item': 'Ether'},
    81: {'decimal': 81, 'hex': '0x51', 'Item': 'Max Ether'},
    82: {'decimal': 82, 'hex': '0x52', 'Item': 'Elixer'},
    83: {'decimal': 83, 'hex': '0x53', 'Item': 'Max Elixer'},
    196: {'decimal': 196, 'hex': '0xC4', 'Item': 'HM01'},
    197: {'decimal': 197, 'hex': '0xC5', 'Item': 'HM02'},
    198: {'decimal': 198, 'hex': '0xC6', 'Item': 'HM03'},
    199: {'decimal': 199, 'hex': '0xC7', 'Item': 'HM04'},
    200: {'decimal': 200, 'hex': '0xC8', 'Item': 'HM05'},
    201: {'decimal': 201, 'hex': '0xC9', 'Item': 'TM01'},
    202: {'decimal': 202, 'hex': '0xCA', 'Item': 'TM02'},
    203: {'decimal': 203, 'hex': '0xCB', 'Item': 'TM03'},
    204: {'decimal': 204, 'hex': '0xCC', 'Item': 'TM04'},
    205: {'decimal': 205, 'hex': '0xCD', 'Item': 'TM05'},
    206: {'decimal': 206, 'hex': '0xCE', 'Item': 'TM06'},
    207: {'decimal': 207, 'hex': '0xCF', 'Item': 'TM07'},
    208: {'decimal': 208, 'hex': '0xD0', 'Item': 'TM08'},
    209: {'decimal': 209, 'hex': '0xD1', 'Item': 'TM09'},
    210: {'decimal': 210, 'hex': '0xD2', 'Item': 'TM10'},
    211: {'decimal': 211, 'hex': '0xD3', 'Item': 'TM11'},
    212: {'decimal': 212, 'hex': '0xD4', 'Item': 'TM12'},
    213: {'decimal': 213, 'hex': '0xD5', 'Item': 'TM13'},
    214: {'decimal': 214, 'hex': '0xD6', 'Item': 'TM14'},
    215: {'decimal': 215, 'hex': '0xD7', 'Item': 'TM15'},
    216: {'decimal': 216, 'hex': '0xD8', 'Item': 'TM16'},
    217: {'decimal': 217, 'hex': '0xD9', 'Item': 'TM17'},
    218: {'decimal': 218, 'hex': '0xDA', 'Item': 'TM18'},
    219: {'decimal': 219, 'hex': '0xDB', 'Item': 'TM19'},
    220: {'decimal': 220, 'hex': '0xDC', 'Item': 'TM20'},
    221: {'decimal': 221, 'hex': '0xDD', 'Item': 'TM21'},
    222: {'decimal': 222, 'hex': '0xDE', 'Item': 'TM22'},
    223: {'decimal': 223, 'hex': '0xDF', 'Item': 'TM23'},
    224: {'decimal': 224, 'hex': '0xE0', 'Item': 'TM24'},
    225: {'decimal': 225, 'hex': '0xE1', 'Item': 'TM25'},
    226: {'decimal': 226, 'hex': '0xE2', 'Item': 'TM26'},
    227: {'decimal': 227, 'hex': '0xE3', 'Item': 'TM27'},
    228: {'decimal': 228, 'hex': '0xE4', 'Item': 'TM28'},
    229: {'decimal': 229, 'hex': '0xE5', 'Item': 'TM29'},
    230: {'decimal': 230, 'hex': '0xE6', 'Item': 'TM30'},
    231: {'decimal': 231, 'hex': '0xE7', 'Item': 'TM31'},
    232: {'decimal': 232, 'hex': '0xE8', 'Item': 'TM32'},
    233: {'decimal': 233, 'hex': '0xE9', 'Item': 'TM33'},
    234: {'decimal': 234, 'hex': '0xEA', 'Item': 'TM34'},
    235: {'decimal': 235, 'hex': '0xEB', 'Item': 'TM35'},
    236: {'decimal': 236, 'hex': '0xEC', 'Item': 'TM36'},
    237: {'decimal': 237, 'hex': '0xED', 'Item': 'TM37'},
    238: {'decimal': 238, 'hex': '0xEE', 'Item': 'TM38'},
    239: {'decimal': 239, 'hex': '0xEF', 'Item': 'TM39'},
    240: {'decimal': 240, 'hex': '0xF0', 'Item': 'TM40'},
    241: {'decimal': 241, 'hex': '0xF1', 'Item': 'TM41'},
    242: {'decimal': 242, 'hex': '0xF2', 'Item': 'TM42'},
    243: {'decimal': 243, 'hex': '0xF3', 'Item': 'TM43'},
    244: {'decimal': 244, 'hex': '0xF4', 'Item': 'TM44'},
    245: {'decimal': 245, 'hex': '0xF5', 'Item': 'TM45'},
    246: {'decimal': 246, 'hex': '0xF6', 'Item': 'TM46'},
    247: {'decimal': 247, 'hex': '0xF7', 'Item': 'TM47'},
    248: {'decimal': 248, 'hex': '0xF8', 'Item': 'TM48'},
    249: {'decimal': 249, 'hex': '0xF9', 'Item': 'TM49'},
    250: {'decimal': 250, 'hex': '0xFA', 'Item': 'TM50'},
    251: {'decimal': 251, 'hex': '0xFB', 'Item': 'TM51'},
    252: {'decimal': 252, 'hex': '0xFC', 'Item': 'TM52'},
    253: {'decimal': 253, 'hex': '0xFD', 'Item': 'TM53'},
    254: {'decimal': 254, 'hex': '0xFE', 'Item': 'TM54'},
    255: {'decimal': 255, 'hex': '0xFF', 'Item': 'TM55'},
}

moves_dict = {
    1: {"Move": "Pound", "Type": "Normal", "Phy/Spec": "Physical", "PP": 35, "Power": 40, "Acc": "100%"},
    2: {"Move": "Karate Chop", "Type": "Fighting", "Phy/Spec": "Physical", "PP": 25, "Power": 50, "Acc": "100%"},
    3: {"Move": "Double Slap", "Type": "Normal", "Phy/Spec": "Physical", "PP": 10, "Power": 15, "Acc": "85%"},
    4: {"Move": "Comet Punch", "Type": "Normal", "Phy/Spec": "Physical", "PP": 15, "Power": 18, "Acc": "85%"},
    5: {"Move": "Mega Punch", "Type": "Normal", "Phy/Spec": "Physical", "PP": 20, "Power": 80, "Acc": "85%"},
    6: {"Move": "Pay Day", "Type": "Normal", "Phy/Spec": "Physical", "PP": 20, "Power": 40, "Acc": "100%"},
    7: {"Move": "Fire Punch", "Type": "Fire", "Phy/Spec": "Physical", "PP": 15, "Power": 75, "Acc": "100%"},
    8: {"Move": "Ice Punch", "Type": "Ice", "Phy/Spec": "Physical", "PP": 15, "Power": 75, "Acc": "100%"},
    9: {"Move": "Thunder Punch", "Type": "Electric", "Phy/Spec": "Physical", "PP": 15, "Power": 75, "Acc": "100%"},
    10: {"Move": "Scratch", "Type": "Normal", "Phy/Spec": "Physical", "PP": 35, "Power": 40, "Acc": "100%"},
    11: {"Move": "Vise Grip", "Type": "Normal", "Phy/Spec": "Physical", "PP": 30, "Power": 55, "Acc": "100%"},
    12: {"Move": "Guillotine", "Type": "Normal", "Phy/Spec": "Physical", "PP": 5, "Power": "—", "Acc": "30%"},
    13: {"Move": "Razor Wind", "Type": "Normal", "Phy/Spec": "Special", "PP": 10, "Power": 80, "Acc": "100%"},
    14: {"Move": "Swords Dance", "Type": "Normal", "Phy/Spec": "Status", "PP": 20, "Power": "—", "Acc": "—%"},
    15: {"Move": "Cut", "Type": "Normal", "Phy/Spec": "Physical", "PP": 30, "Power": 50, "Acc": "95%"},
    16: {"Move": "Gust", "Type": "Flying", "Phy/Spec": "Special", "PP": 35, "Power": 40, "Acc": "100%"},
    17: {"Move": "Wing Attack", "Type": "Flying", "Phy/Spec": "Physical", "PP": 35, "Power": 60, "Acc": "100%"},
    18: {"Move": "Whirlwind", "Type": "Normal", "Phy/Spec": "Status", "PP": 20, "Power": "—", "Acc": "—%"},
    19: {"Move": "Fly", "Type": "Flying", "Phy/Spec": "Physical", "PP": 15, "Power": 90, "Acc": "95%"},
    20: {"Move": "Bind", "Type": "Normal", "Phy/Spec": "Physical", "PP": 20, "Power": 15, "Acc": "85%"},
    21: {"Move": "Slam", "Type": "Normal", "Phy/Spec": "Physical", "PP": 20, "Power": 80, "Acc": "75%"},
    22: {"Move": "Vine Whip", "Type": "Grass", "Phy/Spec": "Physical", "PP": 25, "Power": 45, "Acc": "100%"},
    23: {"Move": "Stomp", "Type": "Normal", "Phy/Spec": "Physical", "PP": 20, "Power": 65, "Acc": "100%"},
    24: {"Move": "Double Kick", "Type": "Fighting", "Phy/Spec": "Physical", "PP": 30, "Power": 30, "Acc": "100%"},
    25: {"Move": "Mega Kick", "Type": "Normal", "Phy/Spec": "Physical", "PP": 5, "Power": 120, "Acc": "75%"},
    26: {"Move": "Jump Kick", "Type": "Fighting", "Phy/Spec": "Physical", "PP": 10, "Power": 100, "Acc": "95%"},
    27: {"Move": "Rolling Kick", "Type": "Fighting", "Phy/Spec": "Physical", "PP": 15, "Power": 60, "Acc": "85%"},
    28: {"Move": "Sand Attack", "Type": "Ground", "Phy/Spec": "Status", "PP": 15, "Power": "—", "Acc": "100%"},
    29: {"Move": "Headbutt", "Type": "Normal", "Phy/Spec": "Physical", "PP": 15, "Power": 70, "Acc": "100%"},
    30: {"Move": "Horn Attack", "Type": "Normal", "Phy/Spec": "Physical", "PP": 25, "Power": 65, "Acc": "100%"},
    31: {"Move": "Fury Attack", "Type": "Normal", "Phy/Spec": "Physical", "PP": 20, "Power": 15, "Acc": "85%"},
    32: {"Move": "Horn Drill", "Type": "Normal", "Phy/Spec": "Physical", "PP": 5, "Power": "—", "Acc": "30%"},
    33: {"Move": "Tackle", "Type": "Normal", "Phy/Spec": "Physical", "PP": 35, "Power": 40, "Acc": "100%"},
    34: {"Move": "Body Slam", "Type": "Normal", "Phy/Spec": "Physical", "PP": 15, "Power": 85, "Acc": "100%"},
    35: {"Move": "Wrap", "Type": "Normal", "Phy/Spec": "Physical", "PP": 20, "Power": 15, "Acc": "90%"},
    36: {"Move": "Take Down", "Type": "Normal", "Phy/Spec": "Physical", "PP": 20, "Power": 90, "Acc": "85%"},
    37: {"Move": "Thrash", "Type": "Normal", "Phy/Spec": "Physical", "PP": 10, "Power": 120, "Acc": "100%"},
    38: {"Move": "Double-Edge", "Type": "Normal", "Phy/Spec": "Physical", "PP": 15, "Power": 120, "Acc": "100%"},
    39: {"Move": "Tail Whip", "Type": "Normal", "Phy/Spec": "Status", "PP": 30, "Power": "—", "Acc": "100%"},
    40: {"Move": "Poison Sting", "Type": "Poison", "Phy/Spec": "Physical", "PP": 35, "Power": 15, "Acc": "100%"},
    41: {"Move": "Twineedle", "Type": "Bug", "Phy/Spec": "Physical", "PP": 20, "Power": 25, "Acc": "100%"},
    42: {"Move": "Pin Missile", "Type": "Bug", "Phy/Spec": "Physical", "PP": 20, "Power": 25, "Acc": "95%"},
    43: {"Move": "Leer", "Type": "Normal", "Phy/Spec": "Status", "PP": 30, "Power": "—", "Acc": "100%"},
    44: {"Move": "Bite", "Type": "Dark", "Phy/Spec": "Physical", "PP": 25, "Power": 60, "Acc": "100%"},
    45: {"Move": "Growl", "Type": "Normal", "Phy/Spec": "Status", "PP": 40, "Power": "—", "Acc": "100%"},
    46: {"Move": "Roar", "Type": "Normal", "Phy/Spec": "Status", "PP": 20, "Power": "—", "Acc": "—%"},
    47: {"Move": "Sing", "Type": "Normal", "Phy/Spec": "Status", "PP": 15, "Power": "—", "Acc": "55%"},
    48: {"Move": "Supersonic", "Type": "Normal", "Phy/Spec": "Status", "PP": 20, "Power": "—", "Acc": "55%"},
    49: {"Move": "Sonic Boom", "Type": "Normal", "Phy/Spec": "Special", "PP": 20, "Power": "—", "Acc": "90%"},
    50: {"Move": "Disable", "Type": "Normal", "Phy/Spec": "Status", "PP": 20, "Power": "—", "Acc": "100%"},
    51: {"Move": "Acid", "Type": "Poison", "Phy/Spec": "Special", "PP": 30, "Power": 40, "Acc": "100%"},
    52: {"Move": "Ember", "Type": "Fire", "Phy/Spec": "Special", "PP": 25, "Power": 40, "Acc": "100%"},
    53: {"Move": "Flamethrower", "Type": "Fire", "Phy/Spec": "Special", "PP": 15, "Power": 90, "Acc": "100%"},
    54: {"Move": "Mist", "Type": "Ice", "Phy/Spec": "Status", "PP": 30, "Power": "—", "Acc": "—%"},
    55: {"Move": "Water Gun", "Type": "Water", "Phy/Spec": "Special", "PP": 25, "Power": 40, "Acc": "100%"},
    56: {"Move": "Hydro Pump", "Type": "Water", "Phy/Spec": "Special", "PP": 5, "Power": 110, "Acc": "80%"},
    57: {"Move": "Surf", "Type": "Water", "Phy/Spec": "Special", "PP": 15, "Power": 90, "Acc": "100%"},
    58: {"Move": "Ice Beam", "Type": "Ice", "Phy/Spec": "Special", "PP": 10, "Power": 90, "Acc": "100%"},
    59: {"Move": "Blizzard", "Type": "Ice", "Phy/Spec": "Special", "PP": 5, "Power": 110, "Acc": "70%"},
    60: {"Move": "Psybeam", "Type": "Psychic", "Phy/Spec": "Special", "PP": 20, "Power": 65, "Acc": "100%"},
    61: {"Move": "Bubble Beam", "Type": "Water", "Phy/Spec": "Special", "PP": 20, "Power": 65, "Acc": "100%"},
    62: {"Move": "Aurora Beam", "Type": "Ice", "Phy/Spec": "Special", "PP": 20, "Power": 65, "Acc": "100%"},
    63: {"Move": "Hyper Beam", "Type": "Normal", "Phy/Spec": "Special", "PP": 5, "Power": 150, "Acc": "90%"},
    64: {"Move": "Peck", "Type": "Flying", "Phy/Spec": "Physical", "PP": 35, "Power": 35, "Acc": "100%"},
    65: {"Move": "Drill Peck", "Type": "Flying", "Phy/Spec": "Physical", "PP": 20, "Power": 80, "Acc": "100%"},
    66: {"Move": "Submission", "Type": "Fighting", "Phy/Spec": "Physical", "PP": 20, "Power": 80, "Acc": "80%"},
    67: {"Move": "Low Kick", "Type": "Fighting", "Phy/Spec": "Physical", "PP": 20, "Power": "—", "Acc": "100%"},
    68: {"Move": 'Counter', 'Type': 'Fighting', 'Category': 'Physical', 'PP': 20, 'Power': '—', 'Accuracy': '100%'},
    69: {"Move": 'Seismic Toss', 'Type': 'Fighting', 'Category': 'Physical', 'PP': 20, 'Power': '—', 'Accuracy': '100%'},
    70: {"Move": 'Strength', 'Type': 'Normal', 'Category': 'Physical', 'PP': 15, 'Power': 80, 'Accuracy': '100%'},
    71: {"Move": 'Absorb', 'Type': 'Grass', 'Category': 'Special', 'PP': 25, 'Power': 20, 'Accuracy': '100%'},
    72: {"Move": 'Mega Drain', 'Type': 'Grass', 'Category': 'Special', 'PP': 15, 'Power': 40, 'Accuracy': '100%'},
    73: {"Move": 'Leech Seed', 'Type': 'Grass', 'Category': 'Status', 'PP': 10, 'Power': '—', 'Accuracy': '90%'},
    74: {"Move": 'Growth', 'Type': 'Normal', 'Category': 'Status', 'PP': 20, 'Power': '—', 'Accuracy': '—%'},
    75: {"Move": 'Razor Leaf', 'Type': 'Grass', 'Category': 'Physical', 'PP': 25, 'Power': 55, 'Accuracy': '95%'},
    76: {"Move": 'Solar Beam', 'Type': 'Grass', 'Category': 'Special', 'PP': 10, 'Power': 120, 'Accuracy': '100%'},
    77: {"Move": 'Poison Powder', 'Type': 'Poison', 'Category': 'Status', 'PP': 35, 'Power': '—', 'Accuracy': '75%'},
    78: {"Move": 'Stun Spore', 'Type': 'Grass', 'Category': 'Status', 'PP': 30, 'Power': '—', 'Accuracy': '75%'},
    79: {"Move": 'Sleep Powder', 'Type': 'Grass', 'Category': 'Status', 'PP': 15, 'Power': '—', 'Accuracy': '75%'},
    80: {"Move": 'Petal Dance', 'Type': 'Grass', 'Category': 'Special', 'PP': 10, 'Power': 120, 'Accuracy': '100%'},
    81: {"Move": 'String Shot', 'Type': 'Bug', 'Category': 'Status', 'PP': 40, 'Power': '—', 'Accuracy': '95%'},
    82: {"Move": 'Dragon Rage', 'Type': 'Dragon', 'Category': 'Special', 'PP': 10, 'Power': '—', 'Accuracy': '100%'},
    83: {"Move": 'Fire Spin', 'Type': 'Fire', 'Category': 'Special', 'PP': 15, 'Power': 35, 'Accuracy': '85%'},
    84: {"Move": 'Thunder Shock', 'Type': 'Electric', 'Category': 'Special', 'PP': 30, 'Power': 40, 'Accuracy': '100%'},
    85: {"Move": 'Thunderbolt', 'Type': 'Electric', 'Category': 'Special', 'PP': 15, 'Power': 90, 'Accuracy': '100%'},
    86: {"Move": 'Thunder Wave', 'Type': 'Electric', 'Category': 'Status', 'PP': 20, 'Power': '—', 'Accuracy': '90%'},
    87: {"Move": 'Thunder', 'Type': 'Electric', 'Category': 'Special', 'PP': 10, 'Power': 110, 'Accuracy': '70%'},
    88: {"Move": 'Rock Throw', 'Type': 'Rock', 'Category': 'Physical', 'PP': 15, 'Power': 50, 'Accuracy': '90%'},
    89: {"Move": 'Earthquake', 'Type': 'Ground', 'Category': 'Physical', 'PP': 10, 'Power': 100, 'Accuracy': '100%'},
    90: {"Move": 'Fissure', 'Type': 'Ground', 'Category': 'Physical', 'PP': 5, 'Power': '—', 'Accuracy': '30%'},
    91: {"Move": 'Dig', 'Type': 'Ground', 'Category': 'Physical', 'PP': 10, 'Power': 80, 'Accuracy': '100%'},
    92: {"Move": 'Toxic', 'Type': 'Poison', 'Category': 'Status', 'PP': 10, 'Power': '—', 'Accuracy': '90%'},
    93: {"Move": 'Confusion', 'Type': 'Psychic', 'Category': 'Special', 'PP': 25, 'Power': 50, 'Accuracy': '100%'},
    94: {"Move": 'Psychic', 'Type': 'Psychic', 'Category': 'Special', 'PP': 10, 'Power': 90, 'Accuracy': '100%'},
    95: {"Move": 'Hypnosis', 'Type': 'Psychic', 'Category': 'Status', 'PP': 20, 'Power': '—', 'Accuracy': '60%'},
    96: {"Move": 'Meditate', 'Type': 'Psychic', 'Category': 'Status', 'PP': 40, 'Power': '—', 'Accuracy': '—%'},
    97: {"Move": 'Agility', 'Type': 'Psychic', 'Category': 'Status', 'PP': 30, 'Power': '—', 'Accuracy': '—%'},
    98: {"Move": 'Quick Attack', 'Type': 'Normal', 'Category': 'Physical', 'PP': 30, 'Power': 40, 'Accuracy': '100%'},
    99: {"Move": 'Rage', 'Type': 'Normal', 'Category': 'Physical', 'PP': 20, 'Power': 20, 'Accuracy': '100%'},
    100: {"Move": 'Teleport', 'Type': 'Psychic', 'Category': 'Status', 'PP': 20, 'Power': '—', 'Accuracy': '—%'},
    101: {"Move": 'Night Shade', 'Type': 'Ghost', 'Category': 'Special', 'PP': 15, 'Power': '—', 'Accuracy': '100%'},
    102: {"Move": 'Mimic', 'Type': 'Normal', 'Category': 'Status', 'PP': 10, 'Power': '—', 'Accuracy': '—%'},
    103: {"Move": 'Screech', 'Type': 'Normal', 'Category': 'Status', 'PP': 40, 'Power': '—', 'Accuracy': '85%'},
    104: {"Move": 'Double Team', 'Type': 'Normal', 'Category': 'Status', 'PP': 15, 'Power': '—', 'Accuracy': '—%'},
    105: {"Move": 'Recover', 'Type': 'Normal', 'Category': 'Status', 'PP': 5, 'Power': '—', 'Accuracy': '—%'},
    106: {"Move": 'Harden', 'Type': 'Normal', 'Category': 'Status', 'PP': 30, 'Power': '—', 'Accuracy': '—%'},
    107: {"Move": 'Minimize', 'Type': 'Normal', 'Category': 'Status', 'PP': 10, 'Power': '—', 'Accuracy': '—%'},
    108: {"Move": 'Smokescreen', 'Type': 'Normal', 'Category': 'Status', 'PP': 20, 'Power': '—', 'Accuracy': '100%'},
    109: {"Move": 'Confuse Ray', 'Type': 'Ghost', 'Category': 'Status', 'PP': 10, 'Power': '—', 'Accuracy': '100%'},
    110: {"Move": 'Withdraw', 'Type': 'Water', 'Category': 'Status', 'PP': 40, 'Power': '—', 'Accuracy': '—%'},
    111: {"Move": 'Defense Curl', 'Type': 'Normal', 'Category': 'Status', 'PP': 40, 'Power': '—', 'Accuracy': '—%'},
    112: {"Move": 'Barrier', 'Type': 'Psychic', 'Category': 'Status', 'PP': 20, 'Power': '—', 'Accuracy': '—%'},
    113: {"Move": 'Light Screen', 'Type': 'Psychic', 'Category': 'Status', 'PP': 30, 'Power': '—', 'Accuracy': '—%'},
    114: {"Move": 'Haze', 'Type': 'Ice', 'Category': 'Status', 'PP': 30, 'Power': '—', 'Accuracy': '—%'},
    115: {"Move": 'Reflect', 'Type': 'Psychic', 'Category': 'Status', 'PP': 20, 'Power': '—', 'Accuracy': '—%'},
    116: {"Move": 'Focus Energy', 'Type': 'Normal', 'Category': 'Status', 'PP': 30, 'Power': '—', 'Accuracy': '—%'},
    117: {"Move": 'Bide', 'Type': 'Normal', 'Category': 'Physical', 'PP': 10, 'Power': '—', 'Accuracy': '—%'},
    118: {"Move": 'Metronome', 'Type': 'Normal', 'Category': 'Status', 'PP': 10, 'Power': '—', 'Accuracy': '—%'},
    119: {"Move": 'Mirror Move', 'Type': 'Flying', 'Category': 'Status', 'PP': 20, 'Power': '—', 'Accuracy': '—%'},
    120: {"Move": 'Self-Destruct', 'Type': 'Normal', 'Category': 'Physical', 'PP': 5, 'Power': 200, 'Accuracy': '100%'},
    121: {"Move": 'Egg Bomb', 'Type': 'Normal', 'Category': 'Physical', 'PP': 10, 'Power': 100, 'Accuracy': '75%'},
    122: {"Move": 'Lick', 'Type': 'Ghost', 'Category': 'Physical', 'PP': 30, 'Power': 30, 'Accuracy': '100%'},
    123: {"Move": 'Smog', 'Type': 'Poison', 'Category': 'Special', 'PP': 20, 'Power': 30, 'Accuracy': '70%'},
    124: {"Move": 'Sludge', 'Type': 'Poison', 'Category': 'Special', 'PP': 20, 'Power': 65, 'Accuracy': '100%'},
    125: {"Move": 'Bone Club', 'Type': 'Ground', 'Category': 'Physical', 'PP': 20, 'Power': 65, 'Accuracy': '85%'},
    126: {"Move": 'Fire Blast', 'Type': 'Fire', 'Category': 'Special', 'PP': 5, 'Power': 110, 'Accuracy': '85%'},
    127: {"Move": 'Waterfall', 'Type': 'Water', 'Category': 'Physical', 'PP': 15, 'Power': 80, 'Accuracy': '100%'},
    128: {"Move": 'Clamp', 'Type': 'Water', 'Category': 'Physical', 'PP': 15, 'Power': 35, 'Accuracy': '85%'},
    129: {"Move": 'Swift', 'Type': 'Normal', 'Category': 'Special', 'PP': 20, 'Power': 60, 'Accuracy': '—%'},
    130: {"Move": 'Skull Bash', 'Type': 'Normal', 'Category': 'Physical', 'PP': 10, 'Power': 130, 'Accuracy': '100%'},
    131: {"Move": 'Spike Cannon', 'Type': 'Normal', 'Category': 'Physical', 'PP': 15, 'Power': 20, 'Accuracy': '100%'},
    132: {"Move": 'Constrict', 'Type': 'Normal', 'Category': 'Physical', 'PP': 35, 'Power': 10, 'Accuracy': '100%'},
    133: {"Move": 'Amnesia', 'Type': 'Psychic', 'Category': 'Status', 'PP': 20, 'Power': '—', 'Accuracy': '—%'},
    134: {"Move": 'Kinesis', 'Type': 'Psychic', 'Category': 'Status', 'PP': 15, 'Power': '—', 'Accuracy': '80%'},
    135: {"Move": 'Soft-Boiled', 'Type': 'Normal', 'Category': 'Status', 'PP': 5, 'Power': '—', 'Accuracy': '—%'},
    136: {"Move": 'High Jump Kick', 'Type': 'Fighting', 'Category': 'Physical', 'PP': 10, 'Power': 130, 'Accuracy': '90%'},
    137: {"Move": 'Glare', 'Type': 'Normal', 'Category': 'Status', 'PP': 30, 'Power': '—', 'Accuracy': '100%'},
    138: {"Move": 'Dream Eater', 'Type': 'Psychic', 'Category': 'Special', 'PP': 15, 'Power': 100, 'Accuracy': '100%'},
    139: {"Move": 'Poison Gas', 'Type': 'Poison', 'Category': 'Status', 'Power': 40, 'Accuracy': 90},
    140: {"Move": 'Barrage', 'Type': 'Normal', 'Category': 'Physical', 'Power': 20, 'PP': 15, 'Accuracy': 85},
    141: {"Move": 'Leech Life', 'Type': 'Bug', 'Category': 'Physical', 'Power': 10, 'PP': 80, 'Accuracy': 100},
    142: {"Move": 'Lovely Kiss', 'Type': 'Normal', 'Category': 'Status', 'Power': 10, 'Accuracy': 75},
    143: {"Move": 'Sky Attack', 'Type': 'Flying', 'Category': 'Physical', 'Power': 5, 'PP': 140, 'Accuracy': 90},
    144: {"Move": 'Transform', 'Type': 'Normal', 'Category': 'Status', 'Power': 10},
    145: {"Move": 'Bubble', 'Type': 'Water', 'Category': 'Special', 'Power': 30, 'PP': 40, 'Accuracy': 100},
    146: {"Move": 'Dizzy Punch', 'Type': 'Normal', 'Category': 'Physical', 'Power': 10, 'PP': 70, 'Accuracy': 100},
    147: {"Move": 'Spore', 'Type': 'Grass', 'Category': 'Status', 'Power': 15, 'Accuracy': 100},
    148: {"Move": 'Flash', 'Type': 'Normal', 'Category': 'Status', 'Power': 20, 'Accuracy': 100},
    149: {"Move": 'Psywave', 'Type': 'Psychic', 'Category': 'Special', 'Power': 15, 'Accuracy': 100},
    150: {"Move": 'Splash', 'Type': 'Normal', 'Category': 'Status', 'Power': 40},
    151: {"Move": 'Acid Armor', 'Type': 'Poison', 'Category': 'Status', 'Power': 20},
    152: {"Move": 'Crabhammer', 'Type': 'Water', 'Category': 'Physical', 'Power': 10, 'PP': 100, 'Accuracy': 90},
    153: {"Move": 'Explosion', 'Type': 'Normal', 'Category': 'Physical', 'Power': 5, 'PP': 250, 'Accuracy': 100},
    154: {"Move": 'Fury Swipes', 'Type': 'Normal', 'Category': 'Physical', 'Power': 15, 'PP': 18, 'Accuracy': 80},
    155: {"Move": 'Bonemerang', 'Type': 'Ground', 'Category': 'Physical', 'Power': 10, 'PP': 50, 'Accuracy': 90},
    156: {"Move": 'Rest', 'Type': 'Psychic', 'Category': 'Status', 'Power': 5},
    157: {"Move": 'Rock Slide', 'Type': 'Rock', 'Category': 'Physical', 'Power': 10, 'PP': 75, 'Accuracy': 90},
    158: {"Move": 'Hyper Fang', 'Type': 'Normal', 'Category': 'Physical', 'Power': 15, 'PP': 80, 'Accuracy': 90},
    159: {"Move": 'Sharpen', 'Type': 'Normal', 'Category': 'Status', 'Power': 30},
    160: {"Move": 'Conversion', 'Type': 'Normal', 'Category': 'Status', 'Power': 30},
    161: {"Move": 'Tri Attack', 'Type': 'Normal', 'Category': 'Special', 'Power': 10, 'PP': 80, 'Accuracy': 100},
    162: {"Move": 'Super Fang', 'Type': 'Normal', 'Category': 'Physical', 'Power': 10, 'Accuracy': 90},
    163: {"Move": 'Slash', 'Type': 'Normal', 'Category': 'Physical', 'Power': 20, 'PP': 70, 'Accuracy': 100},
    164: {"Move": 'Substitute', 'Type': 'Normal', 'Category': 'Status', 'Power': 10},
    165: {"Move": 'Struggle', 'Type': 'Normal', 'Category': 'Physical', 'Power': 1, 'PP': 50}
}

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

STATUSDICT = {
    0x08: 'Poison',
    # 0x04: 'Burn',
    # 0x05: 'Frozen',
    # 0x06: 'Paralyze',
    0x00: 'None',
}   
POKE = [0xD16B, 0xD197, 0xD1C3, 0xD1EF, 0xD21B, 0xD247] # - Pokémon (Again)
STATUS = [0xD16F, 0xD19B, 0xD1C7, 0xD1F3, 0xD21F, 0xD24B] # - Status (Poisoned, Paralyzed, etc.)
TYPE1 = [0xD170, 0xD19C, 0xD1C8, 0xD1F4, 0xD220, 0xD24C] # - Type 1
TYPE2 = [0xD171, 0xD19D, 0xD1C9, 0xD1F5, 0xD221, 0xD24D] # - Type 2
LEVEL = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268] # - Level (actual level)
MAXHP = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269] # - Max HP if = 01 + 256 to MAXHP2 value
CHP = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248] # - Current HP if = 01 + 256

def pokemon(game):
    # Get memory values from the list POKE and LEVEL
    memory_values = [game.get_memory_value(a) for a in POKE]
    levels = [game.get_memory_value(a) for a in LEVEL]

    # Use memory values to get corresponding names from pokemon_data
    names = [entry['name'] for entry in pokemon_data if entry.get('decimal') and int(entry['decimal']) in memory_values]

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

# Returns dict of party pokemons' names, levels, and moves for printing to text file:
def pokemon_l(game):
    # Initialize a list of dictionaries for all 6 slots
    pokemon_info = [{"slot": str(i + 1), "name": "", "level": "0", "moves": []} for i in range(6)]
    # Iterate over each Pokémon slot
    for i in range(6):
        # Get the Pokémon and level for the current slot
        p, l = game.get_memory_value(POKE[i]), game.get_memory_value(LEVEL[i])
        # Convert the Pokémon's decimal value to hex and remove the '0x' prefix
        hex_value = hex(int(p))[2:].upper()
        # Check if the hex value is in pokemon_data
        matching_pokemon = next((entry for entry in pokemon_data if entry.get('hex') == hex_value), None)
        if matching_pokemon:
            # Update the Pokémon's name and level
            pokemon_info[i]["name"] = matching_pokemon["name"]
            pokemon_info[i]["level"] = str(l)
            # Get the moves for the current Pokémon
            moves_addresses = [MOVE1[i], MOVE2[i], MOVE3[i], MOVE4[i]]
            pokemon_info[i]["moves"] = []  # Clear the moves for the current Pokémon
            for moves_address in moves_addresses:
                # Check each of the 4 possible moves
                move_value = game.get_memory_value(moves_address)
                if move_value != 0x00:
                    # Get the move information and add the move name to the Pokémon's moves
                    move_info = moves_dict.get(move_value, {})
                    move_name = move_info.get("Move", "")
                    pokemon_info[i]["moves"].append(move_name)
    return pokemon_info

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

    # get information for player
def player_direction(game):
    return game.get_memory_value(PLAYER_DIRECTION)

def player_y(game):
    return game.get_memory_value(PLAYER_Y)

def player_x(game):
    return game.get_memory_value(PLAYER_X)

def map_n(game):
    return game.get_memory_value(MAP_N_ADDR)

def npc_y(game, npc_id):
    npc_id = npc_id * 0x10
    return game.get_memory_value(0xC104 + npc_id)

def npc_x(game, npc_id):
    npc_id = npc_id * 0x10
    return game.get_memory_value(0xC106 + npc_id)

def sprites(game):
    return game.get_memory_value(WNUMSPRITES)

def signs(game):
    return game.get_memory_value(WNUMSIGNS)

def tree_tile(game):
    return game.get_memory_value(WCUTTILE)

def rewardable_coords(glob_c, glob_r):
            include_conditions = [
        (80 >= glob_c >= 72) and (294 < glob_r <= 320),
        (69 < glob_c < 74) and (313 >= glob_r >= 295),
        (73 >= glob_c >= 72) and (220 <= glob_r <= 330),
        (75 >= glob_c >= 74) and (310 >= glob_r <= 319),
        # (glob_c >= 75 and glob_r <= 310),
        (81 >= glob_c >= 73) and (294 < glob_r <= 313),
        (73 <= glob_c <= 81) and (294 < glob_r <= 308),
        (80 >= glob_c >= 74) and (330 >= glob_r >= 284),
        (90 >= glob_c >= 89) and (336 >= glob_r >= 328),
        # New below
        # Viridian Pokemon Center
        (282 >= glob_r >= 277) and glob_c == 98,
        # Pewter Pokemon Center
        (173 <= glob_r <= 178) and glob_c == 42,
        # Route 4 Pokemon Center
        (131 <= glob_r <= 136) and glob_c == 132,
        (75 <= glob_c <= 76) and (271 < glob_r < 273),
        (82 >= glob_c >= 74) and (284 <= glob_r <= 302),
        (74 <= glob_c <= 76) and (284 >= glob_r >= 277),
        (76 >= glob_c >= 70) and (266 <= glob_r <= 277),
        (76 <= glob_c <= 78) and (274 >= glob_r >= 272),
        (74 >= glob_c >= 71) and (218 <= glob_r <= 266),
        (71 >= glob_c >= 67) and (218 <= glob_r <= 235),
        (106 >= glob_c >= 103) and (228 <= glob_r <= 244),
        (116 >= glob_c >= 106) and (228 <= glob_r <= 232),
        (116 >= glob_c >= 113) and (196 <= glob_r <= 232),
        (113 >= glob_c >= 89) and (208 >= glob_r >= 196),
        (97 >= glob_c >= 89) and (188 <= glob_r <= 214),
        (102 >= glob_c >= 97) and (189 <= glob_r <= 196),
        (89 <= glob_c <= 91) and (188 >= glob_r >= 181),
        (74 >= glob_c >= 67) and (164 <= glob_r <= 184),
        (68 >= glob_c >= 67) and (186 >= glob_r >= 184),
        (64 <= glob_c <= 71) and (151 <= glob_r <= 159),
        (71 <= glob_c <= 73) and (151 <= glob_r <= 156),
        (73 <= glob_c <= 74) and (151 <= glob_r <= 164),
        (103 <= glob_c <= 74) and (157 <= glob_r <= 156),
        (80 <= glob_c <= 111) and (155 <= glob_r <= 156),
        (111 <= glob_c <= 99) and (155 <= glob_r <= 150),
        (111 <= glob_c <= 154) and (150 <= glob_r <= 153),
        (138 <= glob_c <= 154) and (153 <= glob_r <= 160),
        (153 <= glob_c <= 154) and (153 <= glob_r <= 154),
        (143 <= glob_c <= 144) and (153 <= glob_r <= 154),
        (154 <= glob_c <= 158) and (134 <= glob_r <= 145),
        (152 <= glob_c <= 156) and (145 <= glob_r <= 150),
        (42 <= glob_c <= 43) and (173 <= glob_r <= 178),
        (158 <= glob_c <= 163) and (134 <= glob_r <= 135),
        (161 <= glob_c <= 163) and (114 <= glob_r <= 128),
        (163 <= glob_c <= 169) and (114 <= glob_r <= 115),
        (114 <= glob_c <= 169) and (167 <= glob_r <= 102),
        (169 <= glob_c <= 179) and (102 <= glob_r <= 103),
        (178 <= glob_c <= 179) and (102 <= glob_r <= 95),
        (178 <= glob_c <= 163) and (95 <= glob_r <= 96),
        (164 <= glob_c <= 163) and (110 <= glob_r <= 96),
        (163 <= glob_c <= 151) and (110 <= glob_r <= 109),
        (151 <= glob_c <= 154) and (101 <= glob_r <= 109),
        (151 <= glob_c <= 152) and (101 <= glob_r <= 97),
        (153 <= glob_c <= 154) and (97 <= glob_r <= 101),
        (151 <= glob_c <= 154) and (97 <= glob_r <= 98),
        (152 <= glob_c <= 155) and (69 <= glob_r <= 81),
        (155 <= glob_c <= 169) and (80 <= glob_r <= 81),
        (168 <= glob_c <= 184) and (39 <= glob_r <= 43),
        (183 <= glob_c <= 178) and (43 <= glob_r <= 51),
        (179 <= glob_c <= 183) and (48 <= glob_r <= 59),
        (179 <= glob_c <= 158) and (59 <= glob_r <= 57),
        (158 <= glob_c <= 161) and (57 <= glob_r <= 30),
        (158 <= glob_c <= 150) and (30 <= glob_r <= 31),
        (153 <= glob_c <= 150) and (34 <= glob_r <= 31),
        (168 <= glob_c <= 254) and (134 <= glob_r <= 140),
        (282 >= glob_r >= 277) and (436 >= glob_c >= 0), # Include Viridian Pokecenter everywhere
        (173 <= glob_r <= 178) and (436 >= glob_c >= 0), # Include Pewter Pokecenter everywhere
        (131 <= glob_r <= 136) and (436 >= glob_c >= 0), # Include Route 4 Pokecenter everywhere
        (137 <= glob_c <= 197) and (82 <= glob_r <= 142), # Mt Moon Route 3
        (137 <= glob_c <= 187) and (53 <= glob_r <= 103), # Mt Moon B1F
        (137 <= glob_c <= 197) and (16 <= glob_r <= 66), # Mt Moon B2F
        (137 <= glob_c <= 436) and (82 <= glob_r <= 444),  # Most of the rest of map after Mt Moon
        # (0 <= glob_c <= 436) and (0 <= glob_r <= 444),  # Whole map included
    ]
            return any(include_conditions)


def random_pokemon():
    # Generate a random number between 1 and 190 inclusive
    random_decimal = random.randint(1, 190)
    # Find the pokemon with the matching decimal value
    matching_pokemon = next((entry['name'] for entry in pokemon_data if int(entry.get('decimal')) == random_decimal), None)
    if matching_pokemon is None:
        # raise ValueError(f"No pokemon found with decimal value {random_decimal}")
        matching_pokemon = "Magikarp"
    # Print the name of the pokemon
    # print(f"Random Pokemon: {matching_pokemon}")
    return matching_pokemon

def bcd(num):
    return 10 * ((num >> 4) & 0x0F) + (num & 0x0F)

# thatguy saving 0.2 seconds while saving the world
def bit_count(bits):
    return bits.bit_count() # bin(bits).count("1")

def read_bit(game, addr, bit) -> bool:
    # add padding so zero will read '0b100000000' instead of '0b0'
    return bin(256 + game.get_memory_value(addr))[-bit - 1] == "1"

def mem_val(game, addr):
    mem = game.get_memory_value(addr)
    return mem

def write_mem(game, addr, value):
    mem = game.set_memory_value(addr, value)
    return mem

def read_uint16(game, start_addr):
    """Read 2 bytes"""
    val_256 = game.get_memory_value(start_addr)
    val_1 = game.get_memory_value(start_addr + 1)
    return 256 * val_256 + val_1

STATUSDICT = {
    0x08: 'Poison',
    # 0x04: 'Burn',
    # 0x05: 'Frozen',
    # 0x06: 'Paralyze',
    0x00: 'None',
}   
POKE = [0xD16B, 0xD197, 0xD1C3, 0xD1EF, 0xD21B, 0xD247] # - Pokémon (Again)
STATUS = [0xD16F, 0xD19B, 0xD1C7, 0xD1F3, 0xD21F, 0xD24B] # - Status (Poisoned, Paralyzed, etc.)
TYPE1 = [0xD170, 0xD19C, 0xD1C8, 0xD1F4, 0xD220, 0xD24C] # - Type 1
TYPE2 = [0xD171, 0xD19D, 0xD1C9, 0xD1F5, 0xD221, 0xD24D] # - Type 2
LEVEL = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268] # - Level (actual level)
MAXHP = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269] # - Max HP if = 01 + 256 to MAXHP2 value
CHP = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248] # - Current HP if = 01 + 256

def pokemon(game):
    # Get memory values from the list POKE and LEVEL
    memory_values = [game.get_memory_value(a) for a in POKE]
    levels = [game.get_memory_value(a) for a in LEVEL]

    # Use memory values to get corresponding names from pokemon_data
    names = [entry['name'] for entry in pokemon_data if entry.get('decimal') and int(entry['decimal']) in memory_values]

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

# # Returns dict of party pokemons' names, levels, and moves for printing to text file:
# def pokemon_l(game):
#     # Get active party information using the party function
#     party_size, _ = party(game)
#     # Initialize a list of dictionaries for all 6 slots
#     pokemon_info = [{"slot": str(i + 1), "name": "", "level": "0", "moves": []} for i in range(6)]
#     # Iterate over each Pokémon slot
#     for i in range(party_size):
#         # Get the Pokémon and level for the current slot
#         p, l = game.get_memory_value(POKE[i]), game.get_memory_value(LEVEL[i])
#         # Convert the Pokémon's decimal value to hex and remove the '0x' prefix
#         hex_value = hex(int(p))[2:].upper()
#         # Check if the hex value is in pokemon_data
#         matching_pokemon = next((entry for entry in pokemon_data if entry.get('hex') == hex_value), None)
#         if matching_pokemon:
#             # Update the Pokémon's name and level
#             pokemon_info[i]["name"] = matching_pokemon["name"]
#             pokemon_info[i]["level"] = str(l)
#             # Get the moves for the current Pokémon
#             moves_addresses = [MOVE1[i], MOVE2[i], MOVE3[i], MOVE4[i]]
#             pokemon_info[i]["moves"] = []  # Clear the moves for the current Pokémon
#             for moves_address in moves_addresses:
#                 # Check each of the 4 possible moves
#                 move_value = game.get_memory_value(moves_address)
#                 if move_value != 0x00:
#                     # Get the move information and add the move name to the Pokémon's moves
#                     move_info = moves_dict.get(move_value, {})
#                     move_name = move_info.get("Move", "")
#                     pokemon_info[i]["moves"].append(move_name)
#     return pokemon_info

def ss_anne_appeared(game):
    """
    D803 - A bunch of bits that do different things
    """
    return game.get_memory_value(SS_ANNE)

def got_hm01(game):
    return read_bit(game, SS_ANNE, 0)

def rubbed_captains_back(game):
    return read_bit(game, SS_ANNE, 1)

def ss_anne_left(game):
    return read_bit(game, SS_ANNE, 2)

def walked_past_guard_after_ss_anne_left(game):
    return read_bit(game, SS_ANNE, 3)

def started_walking_out_of_dock(game):
    return read_bit(game, SS_ANNE, 4)

def walked_out_of_dock(game):
    return read_bit(game, SS_ANNE, 5)

# def npc_y(game, npc_id, npc_bank):
#     npc_id = npc_id * 0x10
#     npc_bank = (npc_bank + 1) *  0x100
#     return game.get_memory_value(0xC004 + npc_id + npc_bank)

# def npc_x(game, npc_id, npc_bank):
#     npc_id = npc_id * 0x10
#     npc_bank = (npc_bank + 1) *  0x100
#     return game.get_memory_value(0xC006 + npc_id + npc_bank)

def npc_y(game, npc_id):
    npc_id = npc_id * 0x10
    return game.get_memory_value(0xC104 + npc_id)

def npc_x(game, npc_id):
    npc_id = npc_id * 0x10
    return game.get_memory_value(0xC106 + npc_id)

def used_cut(game):
    return game.get_memory_value(WCUTTILE)

def player_y(game):
    return game.get_memory_value(PLAYER_Y)

def player_x(game):
    return game.get_memory_value(PLAYER_X)

def get_hm_count(game):
    hm_ids = [0xC4, 0xC5, 0xC6, 0xC7, 0xC8]
    items = get_items_in_bag(game)
    total_hm_cnt = 0
    for hm_id in hm_ids:
        if hm_id in items:
            total_hm_cnt += 1
    return total_hm_cnt * 1

def get_items_in_bag(game, one_indexed=0):
    first_item = 0xD31E
    item_ids = []
    for i in range(0, 20, 2):
        item_id = game.get_memory_value(first_item + i)
        if item_id == 0 or item_id == 0xff:
            break
        item_ids.append(item_id + one_indexed)
    return item_ids

def get_items_names(game, one_indexed=0):
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

def bill_capt(game):
    met_bill = 5 * int(read_bit(game, 0xD7F1, 0))
    used_cell_separator_on_bill = 5 * int(read_bit(game, 0xD7F2, 3))
    ss_ticket = 5 * int(read_bit(game, 0xD7F2, 4))
    met_bill_2 = 5 * int(read_bit(game, 0xD7F2, 5))
    bill_said_use_cell_separator = 5 * int(read_bit(game, 0xD7F2, 6))
    left_bills_house_after_helping = 5 * int(read_bit(game, 0xD7F2, 7))
    got_hm01 = 5 * int(read_bit(game, 0xD803, 0))
    rubbed_captains_back = 5 * int(read_bit(game, 0xD803, 1))
    return sum([met_bill, used_cell_separator_on_bill, ss_ticket, met_bill_2, bill_said_use_cell_separator, left_bills_house_after_helping, got_hm01, rubbed_captains_back])
