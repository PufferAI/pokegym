import sys
sys.path.append('/bet_adsorption_xinpw8/back2bulba/pokegym')
from pathlib import Path
from pdb import set_trace as T
import types
import uuid
from gymnasium import Env, spaces
import numpy as np
from skimage.transform import resize

from collections import defaultdict
import io, os
import random

import matplotlib.pyplot as plt
from pathlib import Path
import mediapy as media
import subprocess
import multiprocessing
import time
from multiprocessing import Manager

from .pyboy_binding import (
    ACTIONS,
    make_env,
    open_state_file,
    load_pyboy_state,
    run_action_on_emulator,
)
from . import ram_map, game_map
from .pokemon_data import IGNORED_EVENT_IDS

def play():
    """Creates an environment and plays it"""
    env = Environment(
        rom_path="pokemon_red.gb",
        state_path=None,
        headless=False,
        disable_input=False,
        sound=False,
        sound_emulated=False,
        verbose=False,
    )

    env.reset()
    env.game.set_emulation_speed(0)

    # Display available actions
    print("Available actions:")
    for idx, action in enumerate(ACTIONS):
        print(f"{idx}: {action}")

    # Create a mapping from WindowEvent to action index
    window_event_to_action = {
        "PRESS_ARROW_DOWN": 0,
        "PRESS_ARROW_LEFT": 1,
        "PRESS_ARROW_RIGHT": 2,
        "PRESS_ARROW_UP": 3,
        "PRESS_BUTTON_A": 4,
        "PRESS_BUTTON_B": 5,
        "PRESS_BUTTON_START": 6,
        "PRESS_BUTTON_SELECT": 7,
        # Add more mappings if necessary
    }

    while True:
        # Get input from pyboy's get_input method
        input_events = env.game.get_input()
        env.game.tick()
        env.render()
        if len(input_events) == 0:
            continue

        for event in input_events:
            event_str = str(event)
            if event_str in window_event_to_action:
                action_index = window_event_to_action[event_str]
                observation, reward, done, _, info = env.step(
                    action_index, fast_video=False
                )

                # Check for game over
                if done:
                    print(f"{done}")
                    break

                # Additional game logic or information display can go here
                print(f"new Reward: {reward}\n")

class Base:
    # Shared counter among processes
    counter_lock = multiprocessing.Lock()
    counter = multiprocessing.Value('i', 0)
    
    # Initialize a shared integer with a lock for atomic updates
    shared_length = multiprocessing.Value('i', 0)  # 'i' for integer
    lock = multiprocessing.Lock()  # Lock to synchronize access
    
    # Initialize a Manager for shared BytesIO object
    manager = Manager()
    shared_bytes_io_data = manager.list([b''])  # Holds serialized BytesIO data

    def __init__(
        self,
        rom_path="pokemon_red.gb",
        state_path=None,
        headless=True,
        save_video=False,
        quiet=False,
        **kwargs,
    ):
        # Increment counter atomically to get unique sequential identifier
        with Base.counter_lock:
            env_id = Base.counter.value
            Base.counter.value += 1
        
        """Creates a PokemonRed environment"""
        # Change state_path if you want to load off a different state file to start
        if state_path is None:
            state_path = __file__.rstrip("environment.py") + "Bulbasaur.state"
            # state_path = __file__.rstrip("environment.py") + "Bulbasaur_fast_text_no_battle_animations_fixed_battle.state"
        # Make the environment
        self.game, self.screen = make_env(rom_path, headless, quiet, save_video=False, **kwargs)
        self.initial_states = [open_state_file(state_path)]
        self.always_starting_state = [open_state_file(state_path)]
        self.save_video = save_video
        self.headless = headless
        self.use_screen_memory = True
        self.screenshot_counter = 0
        self.step_states = []
        self.map_n_100_steps = 40
        # self.counts_array = np.zeros([256,50,50], dtype=np.uint8)
        # counts_array_update(arr, map_n, r, c):
        #     self.counts_array[map_n, r, c] += 1
        
        # BET nimixx api
        # self.api = Game(self.game) # import this class for api BET
        
        # Logging initializations
        with open("experiments/running_experiment.txt", "r") as file:
        # with open("experiments/test_exp.txt", "r") as file: # for testing video writing BET
            exp_name = file.read()
        self.exp_path = Path(f'experiments/{str(exp_name)}')
        # self.env_id = Path(f'session_{str(uuid.uuid4())[:8]}')
        self.env_id = env_id
        self.s_path = Path(f'{str(self.exp_path)}/sessions/{str(self.env_id)}')
        
        # Manually create running_experiment.txt at pufferlib/experiments/running_experiment.txt
        # Set logging frequency in steps and log_file_aggregator.py path here.
        # Logging makes a file pokemon_party_log.txt in each environment folder at
        # pufferlib/experiments/2w31qioa/sessions/{session_uuid8}/pokemon_party_log.txt
        self.log = True
        self.stepwise_csv_logging = False
        self.log_on_reset = True
        self.log_frequency = 500 # Frequency to log, in steps, if self.log=True and self.log_on_reset=False
        self.aggregate_frequency = 600
        self.aggregate_file_path = 'log_file_aggregator.py'
        
        self.reset_count = 0
        self.explore_hidden_obj_weight = 1
        self.initial_wall_time = time.time()
        self.seen_maps = set()

        R, C = self.screen.raw_screen_buffer_dims()
        self.obs_size = (R // 2, C // 2)

        if self.use_screen_memory:
            self.screen_memory = defaultdict(
                lambda: np.zeros((255, 255, 1), dtype=np.uint8)
            )
            self.obs_size += (4,)
        else:
            self.obs_size += (3,)
        self.observation_space = spaces.Box(
            low=0, high=255, dtype=np.uint8, shape=self.obs_size
        )
        self.action_space = spaces.Discrete(len(ACTIONS))
            
    def init_hidden_obj_mem(self):
        self.seen_hidden_objs = set()
    
    def save_screenshot(self, event, map_n):
        self.screenshot_counter += 1
        ss_dir = Path('screenshots')
        ss_dir.mkdir(exist_ok=True)
        plt.imsave(
            # ss_dir / Path(f'ss_{x}_y_{y}_steps_{steps}_{comment}.jpeg'),
            ss_dir / Path(f'{self.screenshot_counter}_{event}_{map_n}.jpeg'),
            self.screen.screen_ndarray())  # (144, 160, 3)

    def save_state(self):
        state = io.BytesIO()
        state.seek(0)
        self.game.save_state(state)
        self.initial_states.append(state)
    
    def load_last_state(self):
        return self.initial_states[len(self.initial_states) - 1]

    def reset(self, seed=None, options=None):
        """Resets the game. Seeding is NOT supported"""
        return self.screen.screen_ndarray(), {}

    def get_fixed_window(self, arr, y, x, window_size):
        height, width, _ = arr.shape
        h_w, w_w = window_size[0], window_size[1]
        h_w, w_w = window_size[0] // 2, window_size[1] // 2

        y_min = max(0, y - h_w)
        y_max = min(height, y + h_w + (window_size[0] % 2))
        x_min = max(0, x - w_w)
        x_max = min(width, x + w_w + (window_size[1] % 2))

        window = arr[y_min:y_max, x_min:x_max]

        pad_top = h_w - (y - y_min)
        pad_bottom = h_w + (window_size[0] % 2) - 1 - (y_max - y - 1)
        pad_left = w_w - (x - x_min)
        pad_right = w_w + (window_size[1] % 2) - 1 - (x_max - x - 1)

        return np.pad(
            window,
            ((pad_top, pad_bottom), (pad_left, pad_right), (0, 0)),
            mode="constant",
        )

    def render(self):
        if self.use_screen_memory:
            r, c, map_n = ram_map.position(self.game)
            # Update tile map
            mmap = self.screen_memory[map_n]
            if 0 <= r <= 254 and 0 <= c <= 254:
                mmap[r, c] = 255

            # Downsamples the screen and retrieves a fixed window from mmap,
            # then concatenates along the 3rd-dimensional axis (image channel)
            return np.concatenate(
                (
                    self.screen.screen_ndarray()[::2, ::2],
                    self.get_fixed_window(mmap, r, c, self.observation_space.shape),
                ),
                axis=2,
            )
        else:
            return self.screen.screen_ndarray()[::2, ::2]

    def step(self, action):
        run_action_on_emulator(self.game, self.screen, ACTIONS[action], self.headless)
        return self.render(), 0, False, False, {}
        
    def video(self):
        video = self.screen.screen_ndarray()
        return video

    def close(self):
        self.game.stop(False)

class Environment(Base):
    def __init__(
        self,
        rom_path="pokemon_red.gb",
        state_path=None,
        headless=True,
        save_video=False,
        quiet=False,
        verbose=False,
        **kwargs,
    ):
        super().__init__(rom_path, state_path, headless, save_video, quiet, **kwargs)
        self.counts_map = np.zeros((444, 436))
        self.verbose = verbose
        self.screenshot_counter = 0
        self.include_conditions = []
        self.seen_maps_difference = set()
        self.seen_maps = 0
        self.current_maps = []
        self.exclude_map_n = {37, 38, 39, 43, 52, 53, 55, 57}
        self.exclude_map_n = set()
        # self.exclude_map_n_moon = {0, 1, 2, 12, 13, 14, 15, 33, 34, 37, 38, 39, 40, 41, 42, 43, 44, 47, 50, 51, 52, 53, 54, 55, 56, 57, 58, 193, 68}
        self.is_dead = False
        self.talk_to_npc_reward = 0
        self.talk_to_npc_count = {}
        self.already_got_npc_reward = set()
        self.ss_anne_state = False
        self.seen_npcs = set()
        self.explore_npc_weight = 1
        self.last_map = -1
        self.init_hidden_obj_mem()
        self.seen_pokemon = np.zeros(152, dtype=np.uint8)
        self.caught_pokemon = np.zeros(152, dtype=np.uint8)
        self.moves_obtained = np.zeros(0xA5, dtype=np.uint8)
        self.log = False
        self.pokecenter_ids = [0x01, 0x02, 0x03, 0x0F, 0x15, 0x05, 0x06, 0x04, 0x07, 0x08, 0x0A, 0x09]
        self.visited_pokecenter_list = []
        self._all_events_string = ''
        self.used_cut_coords_dict = {}
        self.rewarded_coords = set()
        self.rewarded_position = (0, 0)
        
    def update_pokedex(self):
        for i in range(0xD30A - 0xD2F7):
            caught_mem = self.game.get_memory_value(i + 0xD2F7)
            seen_mem = self.game.get_memory_value(i + 0xD30A)
            for j in range(8):
                self.caught_pokemon[8*i + j] = 1 if caught_mem & (1 << j) else 0
                self.seen_pokemon[8*i + j] = 1 if seen_mem & (1 << j) else 0   
    
    def update_moves_obtained(self):
        # Scan party
        for i in [0xD16B, 0xD197, 0xD1C3, 0xD1EF, 0xD21B, 0xD247]:
            if self.game.get_memory_value(i) != 0:
                for j in range(4):
                    move_id = self.game.get_memory_value(i + j + 8)
                    if move_id != 0:
                        if move_id != 0:
                            self.moves_obtained[move_id] = 1
        # Scan current box (since the box doesn't auto increment in pokemon red)
        num_moves = 4
        box_struct_length = 25 * num_moves * 2
        for i in range(self.game.get_memory_value(0xda80)):
            offset = i*box_struct_length + 0xda96
            if self.game.get_memory_value(offset) != 0:
                for j in range(4):
                    move_id = self.game.get_memory_value(offset + j + 8)
                    if move_id != 0:
                        self.moves_obtained[move_id] = 1
    
    def get_items_in_bag(self, one_indexed=0):
        first_item = 0xD31E
        # total 20 items
        # item1, quantity1, item2, quantity2, ...
        item_ids = []
        for i in range(0, 20, 2):
            item_id = self.game.get_memory_value(first_item + i)
            if item_id == 0 or item_id == 0xff:
                break
            item_ids.append(item_id + one_indexed)
        return item_ids
    
    def poke_count_hms(self):
        pokemon_info = ram_map.pokemon_l(self.game)
        pokes_hm_counts = {
            'Cut': 0,
            'Flash': 0,
            'Fly': 0,
            'Surf': 0,
            'Strength': 0,
        }
        for pokemon in pokemon_info:
            moves = pokemon['moves']
            pokes_hm_counts['Cut'] += 'Cut' in moves
            pokes_hm_counts['Flash'] += 'Flash' in moves
            pokes_hm_counts['Fly'] += 'Fly' in moves
            pokes_hm_counts['Surf'] += 'Surf' in moves
            pokes_hm_counts['Strength'] += 'Strength' in moves
        return pokes_hm_counts
    
    def write_to_log(self):
        # Get the Pokémon information
        pokemon_info = ram_map.pokemon_l(self.game)
        base_dir = self.s_path
        base_dir.mkdir(parents=True, exist_ok=True)
        # Open the log file in write mode
        with open(base_dir / self.full_name_log, 'w') as f:
            # Iterate over each Pokémon
            for pokemon in pokemon_info:
                # Write the Pokémon information to the file
                f.write(f"Slot: {pokemon['slot']}\n")
                f.write(f"Name: {pokemon['name']}\n")
                f.write(f"Level: {pokemon['level']}\n")
                f.write(f"Moves: {', '.join(pokemon['moves'])}\n")
                f.write("\n")  # Add a newline between Pokémon
    
    def get_hm_rewards(self):
        hm_ids = [0xC4, 0xC5, 0xC6, 0xC7, 0xC8]
        items = self.get_items_in_bag()
        total_hm_cnt = 0
        for hm_id in hm_ids:
            if hm_id in items:
                total_hm_cnt += 1
        return total_hm_cnt * 1
            
    def add_video_frame(self):
        self.full_frame_writer.add_image(self.video())
             
    def update_heat_map(self, r, c, current_map):
        '''
        Updates the heat map based on the agent's current position.

        Args:
            r (int): global y coordinate of the agent's position.
            c (int): global x coordinate of the agent's position.
            current_map (int): ID of the current map (map_n)

        Updates the counts_map to track the frequency of visits to each position on the map.
        '''
        # Convert local position to global position
        try:
            glob_r, glob_c = game_map.local_to_global(r, c, current_map)
        except IndexError:
            print(f'IndexError: index {glob_r} or {glob_c} for {current_map} is out of bounds for axis 0 with size 444.')
            glob_r = 0
            glob_c = 0

        # Update heat map based on current map
        if self.last_map == current_map or self.last_map == -1:
            # Increment count for current global position
                try:
                    self.counts_map[glob_r, glob_c] += 1
                except:
                    pass
        else:
            # Reset count for current global position if it's a new map for warp artifacts
            self.counts_map[(glob_r, glob_c)] = -1

        # Update last_map for the next iteration
        self.last_map = current_map

    def find_neighboring_npc(self, npc_id, player_direction, player_x, player_y) -> int:

        npc_y = ram_map.npc_y(self.game, npc_id)
        npc_x = ram_map.npc_x(self.game, npc_id)
        # Check if player is facing the NPC (skip NPC direction)
        # 0 - down, 4 - up, 8 - left, 0xC - right
        if (
            (player_direction == 0 and npc_x == player_x and npc_y > player_y) or
            (player_direction == 4 and npc_x == player_x and npc_y < player_y) or
            (player_direction == 8 and npc_y == player_y and npc_x < player_x) or
            (player_direction == 0xC and npc_y == player_y and npc_x > player_x)
        ):
            # Manhattan distance
            return abs(npc_y - player_y) + abs(npc_x - player_x)

        return 1000
    
    
    def find_neighboring_sign(self, sign_id, player_direction, player_x, player_y) -> bool:

            sign_y = ram_map.mem_val(self.game, (0xD4B0 + (2 * sign_id)))
            sign_x = ram_map.mem_val(self.game, (0xD4B0 + (2 * sign_id + 1)))

            # Check if player is facing the sign (skip sign direction)
            # 0 - down, 4 - up, 8 - left, 0xC - right
            # We are making the assumption that a player will only ever be 1 space away
            # from a sign
            return (
                (player_direction == 0 and sign_x == player_x and sign_y == player_y + 1) or
                (player_direction == 4 and sign_x == player_x and sign_y == player_y - 1) or
                (player_direction == 8 and sign_y == player_y and sign_x == player_x - 1) or
                (player_direction == 0xC and sign_y == player_y and sign_x == player_x + 1)
            )
            
    def get_last_pokecenter_list(self):
        pc_list = [0, ] * len(self.pokecenter_ids)
        last_pokecenter_id = self.get_last_pokecenter_id()
        if last_pokecenter_id != -1:
            pc_list[last_pokecenter_id] = 1
        return pc_list
    
    def get_last_pokecenter_id(self):
        
        last_pokecenter = self.game.get_memory_value(0xD719)
        # will throw error if last_pokecenter not in pokecenter_ids, intended
        if last_pokecenter == 0:
            # no pokecenter visited yet
            return -1
        if last_pokecenter not in self.pokecenter_ids:
            print(f'\nERROR: last_pokecenter: {last_pokecenter} not in pokecenter_ids')
            return -1
        else:
            return self.pokecenter_ids.index(last_pokecenter)

    def get_visited_pokecenter_obs(self):
        result = [0] * len(self.pokecenter_ids)
        for i in self.visited_pokecenter_list:
            result[i] = 1
        return result
    
    def update_visited_pokecenter_list(self):
        last_pokecenter_id = self.get_last_pokecenter_id()
        if last_pokecenter_id != -1 and last_pokecenter_id not in self.visited_pokecenter_list:
            self.visited_pokecenter_list.append(last_pokecenter_id)

    def get_visited_pokecenter_reward(self):
        # reward for first time healed in pokecenter
        return len(self.visited_pokecenter_list) * 2
    
    @staticmethod
    def set_bit(value, bit):
        return value | (1<<bit)
    
    @property
    def all_events_string(self):
        # cache all events string to improve performance
        if not self._all_events_string:
            event_flags_start = 0xD747
            event_flags_end = 0xD886
            result = ''
            for i in range(event_flags_start, event_flags_end):
                result += bin(self.game.get_memory_value(i))[2:].zfill(8)  # .zfill(8)
            self._all_events_string = result
        return self._all_events_string
    
    def get_base_event_flags(self):
        # event patches
        # 1. triggered EVENT_FOUND_ROCKET_HIDEOUT 
        # event_value = self.read_m(0xD77E)  # bit 1
        # self.pyboy.set_memory_value(0xD77E, self.set_bit(event_value, 1))
        # 2. triggered EVENT_GOT_TM13 , fresh_water trade
        event_value = self.game.get_memory_value(0xD778)  # bit 4
        self.game.set_memory_value(0xD778, self.set_bit(event_value, 4))
        address_bits = [
            # seafoam islands
            [0xD7E8, 6],
            [0xD7E8, 7],
            [0xD87F, 0],
            [0xD87F, 1],
            [0xD880, 0],
            [0xD880, 1],
            [0xD881, 0],
            [0xD881, 1],
            # victory road
            [0xD7EE, 0],
            [0xD7EE, 7],
            [0xD813, 0],
            [0xD813, 6],
            [0xD869, 7],
        ]
        for ab in address_bits:
            event_value = self.game.get_memory_value(ab[0])
            self.game.set_memory_value(ab[0], self.set_bit(event_value, ab[1]))

        n_ignored_events = 0
        for event_id in IGNORED_EVENT_IDS:
            if self.all_events_string[event_id] == '1':
                n_ignored_events += 1
        return max(
            self.all_events_string.count('1')
            - n_ignored_events,
        0,
    )

    # def rewardable_coords(self, glob_c, glob_r):
    #                 self.include_conditions = [
    #             (80 >= glob_c >= 72) and (294 < glob_r <= 320),
    #             (69 < glob_c < 74) and (313 >= glob_r >= 295),
    #             (73 >= glob_c >= 72) and (220 <= glob_r <= 330),
    #             (75 >= glob_c >= 74) and (310 >= glob_r <= 319),
    #             # (glob_c >= 75 and glob_r <= 310),
    #             (81 >= glob_c >= 73) and (294 < glob_r <= 313),
    #             (73 <= glob_c <= 81) and (294 < glob_r <= 308),
    #             (80 >= glob_c >= 74) and (330 >= glob_r >= 284),
    #             (90 >= glob_c >= 89) and (336 >= glob_r >= 328),
    #             # New below
    #             # Viridian Pokemon Center
    #             (282 >= glob_r >= 277) and glob_c == 98,
    #             # Pewter Pokemon Center
    #             (173 <= glob_r <= 178) and glob_c == 42,
    #             # Route 4 Pokemon Center
    #             (131 <= glob_r <= 136) and glob_c == 132,
    #             (75 <= glob_c <= 76) and (271 < glob_r < 273),
    #             (82 >= glob_c >= 74) and (284 <= glob_r <= 302),
    #             (74 <= glob_c <= 76) and (284 >= glob_r >= 277),
    #             (76 >= glob_c >= 70) and (266 <= glob_r <= 277),
    #             (76 <= glob_c <= 78) and (274 >= glob_r >= 272),
    #             (74 >= glob_c >= 71) and (218 <= glob_r <= 266),
    #             (71 >= glob_c >= 67) and (218 <= glob_r <= 235),
    #             (106 >= glob_c >= 103) and (228 <= glob_r <= 244),
    #             (116 >= glob_c >= 106) and (228 <= glob_r <= 232),
    #             (116 >= glob_c >= 113) and (196 <= glob_r <= 232),
    #             (113 >= glob_c >= 89) and (208 >= glob_r >= 196),
    #             (97 >= glob_c >= 89) and (188 <= glob_r <= 214),
    #             (102 >= glob_c >= 97) and (189 <= glob_r <= 196),
    #             (89 <= glob_c <= 91) and (188 >= glob_r >= 181),
    #             (74 >= glob_c >= 67) and (164 <= glob_r <= 184),
    #             (68 >= glob_c >= 67) and (186 >= glob_r >= 184),
    #             (64 <= glob_c <= 71) and (151 <= glob_r <= 159),
    #             (71 <= glob_c <= 73) and (151 <= glob_r <= 156),
    #             (73 <= glob_c <= 74) and (151 <= glob_r <= 164),
    #             (103 <= glob_c <= 74) and (157 <= glob_r <= 156),
    #             (80 <= glob_c <= 111) and (155 <= glob_r <= 156),
    #             (111 <= glob_c <= 99) and (155 <= glob_r <= 150),
    #             (111 <= glob_c <= 154) and (150 <= glob_r <= 153),
    #             (138 <= glob_c <= 154) and (153 <= glob_r <= 160),
    #             (153 <= glob_c <= 154) and (153 <= glob_r <= 154),
    #             (143 <= glob_c <= 144) and (153 <= glob_r <= 154),
    #             (154 <= glob_c <= 158) and (134 <= glob_r <= 145),
    #             (152 <= glob_c <= 156) and (145 <= glob_r <= 150),
    #             (42 <= glob_c <= 43) and (173 <= glob_r <= 178),
    #             (158 <= glob_c <= 163) and (134 <= glob_r <= 135),
    #             (161 <= glob_c <= 163) and (114 <= glob_r <= 128),
    #             (163 <= glob_c <= 169) and (114 <= glob_r <= 115),
    #             (114 <= glob_c <= 169) and (167 <= glob_r <= 102),
    #             (169 <= glob_c <= 179) and (102 <= glob_r <= 103),
    #             (178 <= glob_c <= 179) and (102 <= glob_r <= 95),
    #             (178 <= glob_c <= 163) and (95 <= glob_r <= 96),
    #             (164 <= glob_c <= 163) and (110 <= glob_r <= 96),
    #             (163 <= glob_c <= 151) and (110 <= glob_r <= 109),
    #             (151 <= glob_c <= 154) and (101 <= glob_r <= 109),
    #             (151 <= glob_c <= 152) and (101 <= glob_r <= 97),
    #             (153 <= glob_c <= 154) and (97 <= glob_r <= 101),
    #             (151 <= glob_c <= 154) and (97 <= glob_r <= 98),
    #             (152 <= glob_c <= 155) and (69 <= glob_r <= 81),
    #             (155 <= glob_c <= 169) and (80 <= glob_r <= 81),
    #             (168 <= glob_c <= 184) and (39 <= glob_r <= 43),
    #             (183 <= glob_c <= 178) and (43 <= glob_r <= 51),
    #             (179 <= glob_c <= 183) and (48 <= glob_r <= 59),
    #             (179 <= glob_c <= 158) and (59 <= glob_r <= 57),
    #             (158 <= glob_c <= 161) and (57 <= glob_r <= 30),
    #             (158 <= glob_c <= 150) and (30 <= glob_r <= 31),
    #             (153 <= glob_c <= 150) and (34 <= glob_r <= 31),
    #             (168 <= glob_c <= 254) and (134 <= glob_r <= 140),
    #             (282 >= glob_r >= 277) and (436 >= glob_c >= 0), # Include Viridian Pokecenter everywhere
    #             (173 <= glob_r <= 178) and (436 >= glob_c >= 0), # Include Pewter Pokecenter everywhere
    #             (131 <= glob_r <= 136) and (436 >= glob_c >= 0), # Include Route 4 Pokecenter everywhere
    #             (137 <= glob_c <= 197) and (82 <= glob_r <= 142), # Mt Moon Route 3
    #             (137 <= glob_c <= 187) and (53 <= glob_r <= 103), # Mt Moon B1F
    #             (137 <= glob_c <= 197) and (16 <= glob_r <= 66), # Mt Moon B2F
    #             (137 <= glob_c <= 436) and (82 <= glob_r <= 444),  # Most of the rest of map after Mt Moon
    #             # (0 <= glob_c <= 436) and (0 <= glob_r <= 444),  # Whole map included
    #         ]
    #                 return any(self.include_conditions)

    def update_reward(self, new_position, rewarded_coords=set([(0, 0)])):
        """
        Update and determine if the new_position should be rewarded based on every 10 steps
        taken in any direction considering the Manhattan distance. Utilizes a static variable
        'rewarded_coords' to keep track of rewarded positions.
        
        :param new_position: Tuple (r, c) representing the new position of the agent.
        :param rewarded_coords: Static set of tuples representing rewarded positions.
        :return: Float, the reward amount (0.01 for reward, 0 otherwise).
        """
        # Define should_reward as an inner function to determine if the position should be rewarded
        def should_reward(new_position, rewarded_coords):
            for rewarded_position in rewarded_coords:
                # print(f'rewarded_position: {self.rewarded_position}')
                # print(f'new_position: {new_position}')
                distance = abs(rewarded_position[0] - new_position[0]) + abs(self.rewarded_position[1] - new_position[1])
                # print(f'distance={distance}')
                if distance >= 10:
                    return True
            return False

        if should_reward(new_position, rewarded_coords):
            rewarded_coords.add(new_position)
            # print(f'rewarded_position: {self.rewarded_position}')
            # print(f'new_position: {new_position}, rewarded_coords: {rewarded_coords}')
            # return 0.01  # Reward amount
        return rewarded_coords # 0

    def reset(self, seed=None, options=None, max_episode_steps=20480, reward_scale=4.0): # 20480
        """Resets the game. Seeding is NOT supported"""
        load_pyboy_state(self.game, self.load_last_state())
        
        if self.save_video:
            base_dir = self.s_path
            base_dir.mkdir(parents=True, exist_ok=True)
            full_name = Path(f'reset_{self.reset_count}').with_suffix('.mp4')
            self.full_frame_writer = media.VideoWriter(base_dir / full_name, (144, 160), fps=60)
            self.full_frame_writer.__enter__()
            
        if self.log:
            self.full_name_log = Path(f'pokemon_party_log').with_suffix('.txt')
            self.write_to_log()

        if self.use_screen_memory:
            self.screen_memory = defaultdict(
                lambda: np.zeros((255, 255, 1), dtype=np.uint8)
            )

        self.time = 0
        self.max_episode_steps = max_episode_steps
        self.reward_scale = reward_scale
        self.prev_map_n = None
        self.init_hidden_obj_mem()
        self.max_events = 0
        self.max_level_sum = 0
        self.max_opponent_level = 0
        self.seen_coords = set()
        self.seen_maps = set()
        self.death_count = 0
        self.total_healing = 0
        self.last_hp = 1.0
        self.last_party_size = 1
        self.last_reward = None
        self.seen_coords_no_reward = set()
        
        self.visited_pokecenter_list = []

        self._all_events_string = ''
        self.agent_stats = []
        self.base_explore = 0
        self.max_event_rew = 0
        self.max_level_rew = 0
        self.party_level_base = 0
        self.party_level_post = 0
        self.last_num_mon_in_box = 0
        self.death_count = 0
        self.visited_pokecenter_list = []
        self.last_10_map_ids = np.zeros((10, 2), dtype=np.float32)
        self.last_10_coords = np.zeros((10, 2), dtype=np.uint8)
        self.past_events_string = ''
        self.last_10_event_ids = np.zeros((128, 2), dtype=np.float32)
        self.step_count = 0
        self.past_rewards = np.zeros(10240, dtype=np.float32)
        self.base_event_flags = self.get_base_event_flags()
        assert len(self.all_events_string) == 2552, f'len(self.all_events_string): {len(self.all_events_string)}'
        self.rewarded_events_string = '0' * 2552
        self.seen_map_dict = {}
        self._last_item_count = 0
        self._is_box_mon_higher_level = False
        self.secret_switch_states = {}
        self.hideout_elevator_maps = []
        self.use_mart_count = 0
        self.use_pc_swap_count = 0
        # self.progress_reward = self.get_game_state_reward()
        self.total_reward = 0
        self.reset_count += 1
        self.used_cut = 0
        self.rewarded_coords = set()
        
        return self.render(), {}

    # def step(self, action, fast_video=True):
    #     run_action_on_emulator(
    #         self.game,
    #         self.screen,
    #         ACTIONS[action],
    #         self.headless,
    #         fast_video=fast_video,
    #     )
    #     self.time += 1
    #     if self.save_video:
    #         self.add_video_frame()
        
    #     # Exploration reward
    #     r, c, map_n = ram_map.position(self.game)
    #     #         # Convert local position to global position
    #     # try:
    #     #     glob_r, glob_c = game_map.local_to_global(r, c, map_n)
    #     # except IndexError:
    #     #     print(f'IndexError: index {glob_r} or {glob_c} is out of bounds for axis 0 with size 444.')
    #     #     glob_r = 0
    #     #     glob_c = 0
        
    #     # # Only reward for specified coordinates, not all coordinates seen
    #     # if self.rewardable_coords(glob_c, glob_r):
    #     #     self.seen_coords.add((r, c, map_n))
    #     # else:
    #     #     self.seen_coords_no_reward.add((glob_c, glob_r, map_n))
        
    #     try:
    #         self.seen_coords.add((r, c, map_n))
    #     except:
    #         pass
        
    #     if map_n != self.prev_map_n:
    #         self.prev_map_n = map_n
    #         if map_n not in self.seen_maps:
    #             self.seen_maps.add(map_n)
    #             self.talk_to_npc_count[map_n] = 0  # Initialize NPC talk count for this new map
    #             self.save_state()
     
    #     self.update_pokedex()
    #     self.update_moves_obtained()
    #     self.update_visited_pokecenter_list()
    #     # self.past_events_string = self.all_events_string
        
    #     # self.seen_coords.add((r, c))
    #     exploration_reward = 0.05 * len(self.seen_coords)
        
    #     self.update_heat_map(r, c, map_n)

    #     # Aggregate the data in each env log file. Default location of file: pufferlib/log_file_aggregator.py
    #     # if self.time % 10000 == 0:
    #     #     try:
    #     #         subprocess.run(['python', '/home/daa/puffer0.5.2_iron/bill/pufferlib/log_file_aggregator.py'], check=True)
    #     #     except subprocess.CalledProcessError as e:
    #     #         print(f"Error running log_file_aggregator.py: {e}")
        
    #     # Level reward
    #     party_size, party_levels = ram_map.party(self.game)
    #     self.max_level_sum = max(self.max_level_sum, sum(party_levels))
    #     if self.max_level_sum < 30:
    #         level_reward = 1 * self.max_level_sum
    #     else:
    #         level_reward = 30 + (self.max_level_sum - 30) / 4
            
    #     # Healing and death rewards
    #     hp = ram_map.hp(self.game)
    #     hp_delta = hp - self.last_hp
    #     party_size_constant = party_size == self.last_party_size

    #     # Only reward if not reviving at pokecenter
    #     if hp_delta > 0 and party_size_constant and not self.is_dead:
    #         self.total_healing += hp_delta

    #     # Dead if hp is zero
    #     if hp <= 0 and self.last_hp > 0:
    #         self.death_count += 1
    #         self.is_dead = True
    #     elif hp > 0.01:  # TODO: Check if this matters
    #         self.is_dead = False

    #     # Update last known values for next iteration
    #     self.last_hp = hp
    #     self.last_party_size = party_size
    #     death_reward = 0 # -0.08 * self.death_count  # -0.05
        
    #     # Set rewards
    #     healing_reward = self.total_healing

    #     # Opponent level reward
    #     max_opponent_level = max(ram_map.opponent(self.game))
    #     self.max_opponent_level = max(self.max_opponent_level, max_opponent_level)
    #     opponent_level_reward = 0 # 0.2 * self.max_opponent_level

    #     # Badge reward
    #     badges = ram_map.badges(self.game)
    #     badges_reward = 5 * badges
                
    #     # Saved Bill
    #     bill_state = ram_map.saved_bill(self.game)
    #     bill_reward = 10 * bill_state

    
    
    def step(self, action, fast_video=True):
        run_action_on_emulator(self.game, self.screen, ACTIONS[action], self.headless, fast_video=fast_video,)
        self.time += 1

        if self.save_video:
            self.add_video_frame()
        
        # Exploration reward
        r, c, map_n = ram_map.position(self.game)
        self.rewarded_coords = self.update_reward((r,c))
        exploration_reward = 0.05 * len(self.rewarded_coords)
        # self.seen_coords.add((r, c, map_n))
        # exploration_reward = 0.01 * len(self.seen_coords)

        self.update_heat_map(r, c, map_n)

        if map_n != self.prev_map_n:
            self.prev_map_n = map_n
            if map_n not in self.seen_maps:
                self.seen_maps.add(map_n)
                self.save_state()

        # Level reward
        party_size, party_levels = ram_map.party(self.game)
        self.max_level_sum = max(self.max_level_sum, sum(party_levels))
        if self.max_level_sum < 30:
            level_reward = 0.5 * self.max_level_sum
        else:
            level_reward = 15 + (self.max_level_sum - 30) / 4
            
        # Healing and death rewards
        hp = ram_map.hp(self.game)
        hp_delta = hp - self.last_hp
        party_size_constant = party_size == self.last_party_size
        if hp_delta > 0 and party_size_constant and not self.is_dead:
            self.total_healing += hp_delta
        if hp <= 0.2 and self.last_hp > 0:
            self.death_count += 1
            self.is_dead = True
        elif hp > 0.01:  # TODO: Check if this matters
            self.is_dead = False
        self.last_hp = hp
        self.last_party_size = party_size
        death_reward = 0 # -0.08 * self.death_count  # -0.05
        healing_reward = self.total_healing

        # Badge reward
        badges = ram_map.badges(self.game)
        badges_reward = 10 * badges
                
        # Save Bill
        bill_state = ram_map.saved_bill(self.game)
        bill_reward = 10 * bill_state
        
        # # HM reward
        # hm_count = ram_map.get_hm_count(self.game)
        # if hm_count >= 1 and self.hm_count == 0:
        #     self.save_state()
        #     self.hm_count = 1
        # hm_reward = hm_count * 10
        # cut_rew = self.cut * 10    

        # Event reward
        events = ram_map.events(self.game)
        self.max_events = max(self.max_events, events)
        event_reward = self.max_events    
        # Has HMs reward
        # Returns number of party pokemon with each HM
        poke_counts = self.poke_count_hms()
        poke_has_cut = poke_counts['Cut']
        poke_has_flash = poke_counts['Flash']
        poke_has_fly = poke_counts['Fly']
        poke_has_surf = poke_counts['Surf']
        poke_has_strength = poke_counts['Strength']
        
        # HM count
        hm_count = sum(poke_counts.values())
        self.hm_count = hm_count
        if hm_count >= 1 and self.hm_count == 0:
            self.save_state()
        
        # Rewards based on the number of each HM
        poke_has_cut_reward = poke_has_cut * 20
        poke_has_flash_reward = poke_has_flash
        poke_has_fly_reward = poke_has_fly
        poke_has_surf_reward = poke_has_surf
        poke_has_strength_reward = poke_has_strength
        
        # Used Cut
        used_cut_reward = 0
        if self.used_cut > 0:
            used_cut_reward = self.used_cut * 20
        if ram_map.used_cut(self.game) == 61:
            ram_map.write_mem(self.game, 0xCD4D, 00) # address, byte to write
            self.used_cut += 1
            self.used_cut_coords_dict[f'x:{c} y:{r} m:{map_n}'] = self.time
            used_cut_reward = self.used_cut * 20
        
        # SS Anne rewards
        # Experimental
        got_hm01_reward = 5 if ram_map.got_hm01(self.game) else 0
        rubbed_captains_back_reward = 5 if ram_map.rubbed_captains_back(self.game) else 0
        ss_anne_left_reward = 5 if ram_map.ss_anne_left(self.game) else 0
        walked_past_guard_after_ss_anne_left_reward = 5 if ram_map.walked_past_guard_after_ss_anne_left(self.game) else 0
        started_walking_out_of_dock_reward = 5 if ram_map.started_walking_out_of_dock(self.game) else 0
        walked_out_of_dock_reward = 5 if ram_map.walked_out_of_dock(self.game) else 0

        # SS Anne flags
        # Experimental
        got_hm01 = int(bool(got_hm01_reward))
        self.rubbed_captains_back = int(bool(rubbed_captains_back_reward))
        self.ss_anne_left = int(bool(ss_anne_left_reward))
        self.walked_past_guard_after_ss_anne_left = int(bool(walked_past_guard_after_ss_anne_left_reward))
        self.started_walking_out_of_dock = int(bool(started_walking_out_of_dock_reward))
        self.walked_out_of_dock = int(bool(walked_out_of_dock_reward))
        
        # got_hm01 flag to enable cut menu conditioning
        self.got_hm01 = got_hm01
        self.got_hm01_reward = self.got_hm01 * 5        

        # SS Anne appeared
        ss_anne_state = ram_map.ss_anne_appeared(self.game)
        if ss_anne_state:
            ss_anne_state_reward = 10 # 5
            ss_anne_obtained = 1
        else:
            ss_anne_state_reward = 0
            ss_anne_obtained = 0
    
        # HM reward
        hm_count = self.get_hm_rewards()
        hm_reward = hm_count * 10

        # Event reward
        events = ram_map.events(self.game)
        self.max_events = max(self.max_events, events)
        event_reward = self.max_events
        money = ram_map.money(self.game)
        
        # Explore NPCs
        # Known to not actually work correctly. Counts first sign on each map as NPC. Treats NPCs as hidden obj and vice versa.
        # Intentionally left this way because it works better, i.e. proper NPC/hidden obj. rewarding/ignoring signs gets
        # worse results.
        # Check NPC/hidden object function
        # check if the font is loaded
        if ram_map.mem_val(self.game, 0xCFC4):
            # check if we are talking to a hidden object:
            player_direction = ram_map.mem_val(self.game, 0xC109)
            if ram_map.mem_val(self.game, 0xCD3D) != 0x0 and ram_map.mem_val(self.game, 0xCD3E) != 0x0:
                # add hidden object to seen hidden objects
                self.seen_hidden_objs.add((ram_map.mem_val(self.game, 0xD35E), ram_map.mem_val(self.game, 0xCD3F)))
        else:
            # get information for player
            player_direction = ram_map.mem_val(self.game, 0xC109)
            player_y = ram_map.mem_val(self.game, 0xC104)
            player_x = ram_map.mem_val(self.game, 0xC106)
            # get the npc who is closest to the player and facing them
            # we go through all npcs because there are npcs like
            # nurse joy who can be across a desk and still talk to you
            mindex = 0
            minv = 1000
            for npc_id in range(1, ram_map.mem_val(self.game, 0xD4E1)):
                npc_dist = self.find_neighboring_npc(npc_id, player_direction, player_x, player_y)
                if npc_dist < minv:
                    mindex = npc_id
                    minv = npc_dist
            # A little counterintuitive. A mindex of 0 means the player isn't talking to an NPC
            # However, given that we are also checking for hidden objects and signs,
            # it could also mean a field move is being used which is worth the reward.
            if mindex != 0:
                self.seen_npcs.add((ram_map.mem_val(self.game, 0xD35E), mindex))

        explore_npcs_reward = self.reward_scale * self.explore_npc_weight * len(self.seen_npcs) * 0.00015
        seen_pokemon_reward = self.reward_scale * sum(self.seen_pokemon) * 0.00010
        caught_pokemon_reward = self.reward_scale * sum(self.caught_pokemon) * 0.00010
        moves_obtained_reward = self.reward_scale * sum(self.moves_obtained) * 0.00010
        explore_hidden_objs_reward = self.reward_scale * self.explore_hidden_obj_weight * len(self.seen_hidden_objs) * 0.00015

        level_reward = 0.001 * level_reward
        # caught_pokemon_reward = 0 # helps it beat early trainers
        seen_pokemon_reward = 0
        healing_reward = 0
        event_reward = event_reward * 0.3
    

        reward = self.reward_scale * (
            event_reward
            + explore_npcs_reward # Doesn't reset on reset but maybe should?
            + seen_pokemon_reward
            + caught_pokemon_reward
            + moves_obtained_reward
            + explore_hidden_objs_reward # Resets on reset
            + bill_reward
            + hm_reward
            + level_reward
            # + opponent_level_reward
            + death_reward # Resets on reset
            + badges_reward
            + healing_reward # Resets each step
            + exploration_reward # Resets on reset
            + poke_has_cut_reward
            + used_cut_reward
        )

        # Subtract previous reward
        if self.last_reward is None:
            reward = 0
            self.last_reward = 0
        else:
            nxt_reward = reward
            reward -= self.last_reward
            self.last_reward = nxt_reward

        info = {} 
        done = self.time >= self.max_episode_steps
        if self.save_video and done:
            self.full_frame_writer.close()
        if done or self.time % 3000 == 0:   
            levels = [self.game.get_memory_value(a) for a in [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]]       
            info = {
                "stats": {
                    "step": self.time,
                    "x": c,
                    "y": r,
                    "map": map_n,
                    # "map_location": self.get_map_location(map_n),
                    # "max_map_progress": self.max_map_progress,
                    "pcount": int(self.game.get_memory_value(0xD163)),
                    "levels": levels,
                    "levels_sum": sum(levels),
                    # "ptypes": self.read_party(),
                    # "hp": self.read_hp_fraction(),
                    "coord": np.sum(self.counts_map),  # np.sum(self.seen_global_coords),
                    # "map_id": np.sum(self.seen_map_ids),
                    # "npc": sum(self.seen_npcs.values()),
                    # "hidden_obj": sum(self.seen_hidden_objs.values()),
                    "deaths": self.death_count,
                    "badges": float(badges),
                    "badge_1": float(badges >= 1),
                    "badge_2": float(badges >= 2),
                    "badge_3": float(badges >= 3),
                    "badge_4": float(badges >= 4),
                    "badge_5": float(badges >= 5),
                    "badge_6": float(badges >= 6),
                    "events": len(self.past_events_string),
                    # "action_hist": self.action_hist,
                    # "caught_pokemon": int(sum(self.caught_pokemon)),
                    # "seen_pokemon": int(sum(self.seen_pokemon)),
                    # "moves_obtained": int(sum(self.moves_obtained)),
                    "opponent_level": self.max_opponent_level,
                    "met_bill": int(ram_map.read_bit(self.game, 0xD7F1, 0)),
                    "used_cell_separator_on_bill": int(ram_map.read_bit(self.game, 0xD7F2, 3)),
                    "ss_ticket": int(ram_map.read_bit(self.game, 0xD7F2, 4)),
                    "met_bill_2": int(ram_map.read_bit(self.game, 0xD7F2, 5)),
                    "bill_said_use_cell_separator": int(ram_map.read_bit(self.game, 0xD7F2, 6)),
                    "left_bills_house_after_helping": int(ram_map.read_bit(self.game, 0xD7F2, 7)),
                    "got_hm01": int(ram_map.read_bit(self.game, 0xD803, 0)),
                    "rubbed_captains_back": int(ram_map.read_bit(self.game, 0xD803, 1)),
                    # "taught_cut": int(self.check_if_party_has_cut()),
                    # "cut_coords": sum(self.cut_coords.values()),
                    'pcount': int(self.game.get_memory_value(0xD163)), 
                    'visited_pokecenterr': self.get_visited_pokecenter_reward(),
                    # 'rewards': int(self.total_reward) if self.total_reward is not None else 0,
                    "maps_explored": len(self.seen_maps),
                    "party_size": party_size,
                    "highest_pokemon_level": max(party_levels),
                    "total_party_level": sum(party_levels),
                    "deaths": self.death_count,
                    "bill_saved": bill_state,
                    "hm_count": hm_count,
                    "ss_anne_obtained": ss_anne_obtained,
                    "event": events,
                    "money": money,
                    "pokemon_exploration_map": self.counts_map,
                    "seen_npcs_count": len(self.seen_npcs),
                    "seen_pokemon": np.sum(self.seen_pokemon),
                    "caught_pokemon": np.sum(self.caught_pokemon),
                    "moves_obtained": np.sum(self.moves_obtained),
                    "hidden_obj_count": len(self.seen_hidden_objs),
                },
                "reward": {
                    "delta": reward,
                    "event": event_reward,
                    "level": level_reward,
                    # "opponent_level": opponent_level_reward,
                    "death": death_reward,
                    "badges": badges_reward,
                    "bill_saved_reward": bill_reward,
                    "hm_count_reward": hm_reward,
                    "ss_anne_done_reward": ss_anne_state_reward,
                    "healing": healing_reward,
                    "exploration": exploration_reward,
                    "explore_npcs_reward": explore_npcs_reward,
                    "seen_pokemon_reward": seen_pokemon_reward,
                    "caught_pokemon_reward": caught_pokemon_reward,
                    "moves_obtained_reward": moves_obtained_reward,
                    "hidden_obj_count_reward": explore_hidden_objs_reward,
                },
                "pokemon_exploration_map": self.counts_map, # self.explore_map, #  self.counts_map, 
            }

        if self.verbose:
            print({
                "stats": {
                    "step": self.time,
                    "x": c,
                    "y": r,
                    "map": map_n,
                    # "map_location": self.get_map_location(map_n),
                    # "max_map_progress": self.max_map_progress,
                    "pcount": int(self.game.get_memory_value(0xD163)),
                    # "ptypes": self.read_party(),
                    # "hp": self.read_hp_fraction(),
                    "coord": np.sum(self.counts_map),  # np.sum(self.seen_global_coords),
                    # "map_id": np.sum(self.seen_map_ids),
                    # "npc": sum(self.seen_npcs.values()),
                    # "hidden_obj": sum(self.seen_hidden_objs.values()),
                    "deaths": self.death_count,
                    "badges": float(badges),
                    "badge_1": float(badges >= 1),
                    "badge_2": float(badges >= 2),
                    "badge_3": float(badges >= 3),
                    "badge_4": float(badges >= 4),
                    "badge_5": float(badges >= 5),
                    "badge_6": float(badges >= 6),
                    "events": len(self.past_events_string),
                    # "action_hist": self.action_hist,
                    # "caught_pokemon": int(sum(self.caught_pokemon)),
                    # "seen_pokemon": int(sum(self.seen_pokemon)),
                    # "moves_obtained": int(sum(self.moves_obtained)),
                    "opponent_level": self.max_opponent_level,
                    "met_bill": int(ram_map.read_bit(self.game, 0xD7F1, 0)),
                    "used_cell_separator_on_bill": int(ram_map.read_bit(self.game, 0xD7F2, 3)),
                    "ss_ticket": int(ram_map.read_bit(self.game, 0xD7F2, 4)),
                    "met_bill_2": int(ram_map.read_bit(self.game, 0xD7F2, 5)),
                    "bill_said_use_cell_separator": int(ram_map.read_bit(self.game, 0xD7F2, 6)),
                    "left_bills_house_after_helping": int(ram_map.read_bit(self.game, 0xD7F2, 7)),
                    "got_hm01": int(ram_map.read_bit(self.game, 0xD803, 0)),
                    "rubbed_captains_back": int(ram_map.read_bit(self.game, 0xD803, 1)),
                    # "taught_cut": int(self.check_if_party_has_cut()),
                    # "cut_coords": sum(self.cut_coords.values()),
                    'pcount': int(self.game.get_memory_value(0xD163)), 
                    'visited_pokecenterr': self.get_visited_pokecenter_reward(),
                    # 'rewards': int(self.total_reward) if self.total_reward is not None else 0,
                    "maps_explored": len(self.seen_maps),
                    "party_size": party_size,
                    "highest_pokemon_level": max(party_levels),
                    "total_party_level": sum(party_levels),
                    "deaths": self.death_count,
                    "bill_saved": bill_state,
                    "hm_count": hm_count,
                    "ss_anne_obtained": ss_anne_obtained,
                    "event": events,
                    "money": money,
                    "pokemon_exploration_map": self.counts_map,
                    "seen_npcs_count": len(self.seen_npcs),
                    "seen_pokemon": np.sum(self.seen_pokemon),
                    "caught_pokemon": np.sum(self.caught_pokemon),
                    "moves_obtained": np.sum(self.moves_obtained),
                    "hidden_obj_count": len(self.seen_hidden_objs),
                },
                "reward": {
                    "delta": reward,
                    "event": event_reward,
                    "level": level_reward,
                    # "opponent_level": opponent_level_reward,
                    "death": death_reward,
                    "badges": badges_reward,
                    "bill_saved_reward": bill_reward,
                    "hm_count_reward": hm_reward,
                    "ss_anne_done_reward": ss_anne_state_reward,
                    "healing": healing_reward,
                    "exploration": exploration_reward,
                    "explore_npcs_reward": explore_npcs_reward,
                    "seen_pokemon_reward": seen_pokemon_reward,
                    "caught_pokemon_reward": caught_pokemon_reward,
                    "moves_obtained_reward": moves_obtained_reward,
                    "hidden_obj_count_reward": explore_hidden_objs_reward,
                },
                "pokemon_exploration_map": self.counts_map, # self.explore_map, #  self.counts_map, 
            }
            )
        
        return self.render(), reward, done, done, info
