import csv
from pathlib import Path
from pdb import set_trace as T
import types
import uuid
from gymnasium import Env, spaces
import numpy as np
import pandas as pd
from skimage.transform import resize

from collections import defaultdict
import io, os
import random

import matplotlib.pyplot as plt
from pathlib import Path
import mediapy as media

from pokegym.pyboy_binding import (
    ACTIONS,
    make_env,
    open_state_file,
    load_pyboy_state,
    run_action_on_emulator,
)
from pokegym import ram_map, game_map, data


def play():
    """Creates an environment and plays it"""
    env = Environment(
        rom_path="pokemon_red.gb",
        state_path=None,
        headless=False,
        disable_input=False,
        sound=False,
        sound_emulated=False,
        verbose=True,
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

STATE_PATH = __file__.rstrip("environment.py") + "States/"

class Base:
    def __init__(
        self,
        rom_path="pokemon_red.gb",
        state_path=None,
        headless=True,
        save_video=False,
        quiet=False,
        **kwargs,
    ):
        """Creates a PokemonRed environment"""
        if state_path is None:
            state_path = STATE_PATH + "Bulbasaur.state" # STATE_PATH + "has_pokedex_nballs.state"
        self.game, self.screen = make_env(rom_path, headless, quiet, save_video=False, **kwargs)

        
        self.initial_states = [open_state_file(state_path)]
        self.save_video = save_video
        self.headless = headless
        self.mem_padding = 2
        self.memory_shape = 80
        self.use_screen_memory = True
        self.screenshot_counter = 0
        self.env_id = Path(f'session_{str(uuid.uuid4())[:4]}')
        self.video_path = Path(f'./videos')
        self.video_path.mkdir(parents=True, exist_ok=True)
        self.csv_path = Path(f'./csv')
        self.csv_path.mkdir(parents=True, exist_ok=True)
        self.reset_count = 0
        self.explore_hidden_obj_weight = 1
        self.csv = True

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
    
    def save_screenshot(self, event, map_n):
        self.screenshot_counter += 1
        ss_dir = Path('screenshots')
        ss_dir.mkdir(exist_ok=True)
        plt.imsave(
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

            mmap = self.screen_memory[map_n]
            if 0 <= r <= 254 and 0 <= c <= 254:
                mmap[r, c] = 255
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
        save_video=True,
        quiet=False,
        verbose=False,
        **kwargs,
    ):
        super().__init__(rom_path, state_path, headless, save_video, quiet, **kwargs)
        self.counts_map = np.zeros((444, 436))
        self.verbose = verbose
        
        self.include_conditions = []
        self.talk_to_npc_count = {}
        self.seen_npcs = set()
        self.explore_npc_weight = 1
        self.seen_pokemon = np.zeros(152, dtype=np.uint8)
        self.caught_pokemon = np.zeros(152, dtype=np.uint8)
        self.moves_obtained = np.zeros(0xA5, dtype=np.uint8)
        
    def update_pokedex(self):
        for i in range(0xD30A - 0xD2F7):
            caught_mem = self.game.get_memory_value(i + 0xD2F7)
            seen_mem = self.game.get_memory_value(i + 0xD30A)
            for j in range(8):
                self.caught_pokemon[8*i + j] = 1 if caught_mem & (1 << j) else 0
                self.seen_pokemon[8*i + j] = 1 if seen_mem & (1 << j) else 0
                
    def write_to_csv(self):
        x, y ,map_n = ram_map.position(self.game)
        reset = self.reset_count
        env_id = self.env_id
        csv_file_path = Path(f'./csv/agent_position.csv')
        with open(csv_file_path, 'a') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([env_id, reset, x, y, map_n])

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
        item_names = []
        for i in range(0, 20, 2):
            item_id = self.game.get_memory_value(first_item + i)
            if item_id == 0 or item_id == 0xff:
                break
            item_id_key = item_id + one_indexed
            item_name = data.items_dict.get(item_id_key, {}).get('Item', f'Unknown Item {item_id_key}')
            item_names.append(item_name)
        return item_names
    
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
        
    def find_neighboring_npc(self, npc_bank, npc_id, player_direction, player_x, player_y) -> int:

        npc_y = ram_map.npc_y(self.game, npc_id, npc_bank)
        npc_x = ram_map.npc_x(self.game, npc_id, npc_bank)
        if (
            (player_direction == 0 and npc_x == player_x and npc_y > player_y) or
            (player_direction == 4 and npc_x == player_x and npc_y < player_y) or
            (player_direction == 8 and npc_y == player_y and npc_x < player_x) or
            (player_direction == 0xC and npc_y == player_y and npc_x > player_x)
        ):
            # Manhattan distance
            return abs(npc_y - player_y) + abs(npc_x - player_x)

        return 1000
    
    def rewardable_coords(self, glob_c, glob_r):
                self.include_conditions = [
            # (80 >= glob_c >= 72) and (294 < glob_r <= 320),
            # (69 < glob_c < 74) and (313 >= glob_r >= 295),
            # (73 >= glob_c >= 72) and (220 <= glob_r <= 330),
            # (75 >= glob_c >= 74) and (310 >= glob_r <= 319),
            # # (glob_c >= 75 and glob_r <= 310),
            # (81 >= glob_c >= 73) and (294 < glob_r <= 313),
            # (73 <= glob_c <= 81) and (294 < glob_r <= 308),
            # (80 >= glob_c >= 74) and (330 >= glob_r >= 284),
            # (90 >= glob_c >= 89) and (336 >= glob_r >= 328),
            # # New below
            # # Viridian Pokemon Center
            # (282 >= glob_r >= 277) and glob_c == 98,
            # # Pewter Pokemon Center
            # (173 <= glob_r <= 178) and glob_c == 42,
            # # Route 4 Pokemon Center
            # (131 <= glob_r <= 136) and glob_c == 132,
            # (75 <= glob_c <= 76) and (271 < glob_r < 273),
            # (82 >= glob_c >= 74) and (284 <= glob_r <= 302),
            # (74 <= glob_c <= 76) and (284 >= glob_r >= 277),
            # (76 >= glob_c >= 70) and (266 <= glob_r <= 277),
            # (76 <= glob_c <= 78) and (274 >= glob_r >= 272),
            # (74 >= glob_c >= 71) and (218 <= glob_r <= 266),
            # (71 >= glob_c >= 67) and (218 <= glob_r <= 235),
            # (106 >= glob_c >= 103) and (228 <= glob_r <= 244),
            # (116 >= glob_c >= 106) and (228 <= glob_r <= 232),
            # (116 >= glob_c >= 113) and (196 <= glob_r <= 232),
            # (113 >= glob_c >= 89) and (208 >= glob_r >= 196),
            # (97 >= glob_c >= 89) and (188 <= glob_r <= 214),
            # (102 >= glob_c >= 97) and (189 <= glob_r <= 196),
            # (89 <= glob_c <= 91) and (188 >= glob_r >= 181),
            # (74 >= glob_c >= 67) and (164 <= glob_r <= 184),
            # (68 >= glob_c >= 67) and (186 >= glob_r >= 184),
            # (64 <= glob_c <= 71) and (151 <= glob_r <= 159),
            # (71 <= glob_c <= 73) and (151 <= glob_r <= 156),
            # (73 <= glob_c <= 74) and (151 <= glob_r <= 164),
            # (103 <= glob_c <= 74) and (157 <= glob_r <= 156),
            # (80 <= glob_c <= 111) and (155 <= glob_r <= 156),
            # (111 <= glob_c <= 99) and (155 <= glob_r <= 150),
            # (111 <= glob_c <= 154) and (150 <= glob_r <= 153),
            # (138 <= glob_c <= 154) and (153 <= glob_r <= 160),
            # (153 <= glob_c <= 154) and (153 <= glob_r <= 154),
            # (143 <= glob_c <= 144) and (153 <= glob_r <= 154),
            # (154 <= glob_c <= 158) and (134 <= glob_r <= 145),
            # (152 <= glob_c <= 156) and (145 <= glob_r <= 150),
            # (42 <= glob_c <= 43) and (173 <= glob_r <= 178),
            # (158 <= glob_c <= 163) and (134 <= glob_r <= 135),
            # (161 <= glob_c <= 163) and (114 <= glob_r <= 128),
            # (163 <= glob_c <= 169) and (114 <= glob_r <= 115),
            # (114 <= glob_c <= 169) and (167 <= glob_r <= 102),
            # (169 <= glob_c <= 179) and (102 <= glob_r <= 103),
            # (178 <= glob_c <= 179) and (102 <= glob_r <= 95),
            # (178 <= glob_c <= 163) and (95 <= glob_r <= 96),
            # (164 <= glob_c <= 163) and (110 <= glob_r <= 96),
            # (163 <= glob_c <= 151) and (110 <= glob_r <= 109),
            # (151 <= glob_c <= 154) and (101 <= glob_r <= 109),
            # (151 <= glob_c <= 152) and (101 <= glob_r <= 97),
            # (153 <= glob_c <= 154) and (97 <= glob_r <= 101),
            # (151 <= glob_c <= 154) and (97 <= glob_r <= 98),
            # (152 <= glob_c <= 155) and (69 <= glob_r <= 81),
            # (155 <= glob_c <= 169) and (80 <= glob_r <= 81),
            # (168 <= glob_c <= 184) and (39 <= glob_r <= 43),
            # (183 <= glob_c <= 178) and (43 <= glob_r <= 51),
            # (179 <= glob_c <= 183) and (48 <= glob_r <= 59),
            # (179 <= glob_c <= 158) and (59 <= glob_r <= 57),
            # (158 <= glob_c <= 161) and (57 <= glob_r <= 30),
            # (158 <= glob_c <= 150) and (30 <= glob_r <= 31),
            # (153 <= glob_c <= 150) and (34 <= glob_r <= 31),
            # (168 <= glob_c <= 254) and (134 <= glob_r <= 140),
            # (282 >= glob_r >= 277) and (436 >= glob_c >= 0), # Include Viridian Pokecenter everywhere
            # (173 <= glob_r <= 178) and (436 >= glob_c >= 0), # Include Pewter Pokecenter everywhere
            # (131 <= glob_r <= 136) and (436 >= glob_c >= 0), # Include Route 4 Pokecenter everywhere
            # (137 <= glob_c <= 197) and (82 <= glob_r <= 142), # Mt Moon Route 3
            # (137 <= glob_c <= 187) and (53 <= glob_r <= 103), # Mt Moon B1F
            # (137 <= glob_c <= 197) and (16 <= glob_r <= 66), # Mt Moon B2F
            # (137 <= glob_c <= 436) and (82 <= glob_r <= 444),  # Most of the rest of map after Mt Moon
            (0 <= glob_c <= 436) and (0 <= glob_r <= 444),  # Whole map included
        ]
                return any(self.include_conditions)

    def reset(self, seed=None, options=None, max_episode_steps=20480, reward_scale=4.0):
        """Resets the game. Seeding is NOT supported"""
        load_pyboy_state(self.game, self.load_last_state())
        
        if self.save_video:
            base_dir = self.video_path
            base_dir.mkdir(parents=True, exist_ok=True)
            full_name = Path(f'{self.env_id}_reset_{self.reset_count}').with_suffix('.mp4')
            self.full_frame_writer = media.VideoWriter(base_dir / full_name, (144, 160), fps=60)
            self.full_frame_writer.__enter__()

        if self.use_screen_memory:
            self.screen_memory = defaultdict(
                lambda: np.zeros((255, 255, 1), dtype=np.uint8)
            )
        
        self.time = 0
        self.max_episode_steps = max_episode_steps
        self.reward_scale = reward_scale
        self.prev_map_n = None
        #BET ADDED
        self.max_events = 0
        self.max_level_sum = 0
        self.max_opponent_level = 0
        self.seen_hidden_objs = set()
        self.seen_coords = set()
        self.seen_maps = set()
        ########################################################### Moved from Environment_Init()
        self.is_dead = False
        self.last_map = -1
        #End
        self.death_count = 0
        self.total_healing = 0
        self.last_hp = 1.0
        self.last_party_size = 1
        self.last_reward = None
        self.seen_coords_no_reward = set()
        self.reset_count += 1
        
        return self.render(), {}

    def step(self, action, fast_video=True):
        run_action_on_emulator(
            self.game,
            self.screen,
            ACTIONS[action],
            self.headless,
            fast_video=fast_video,
        )
        self.time += 1
        if self.save_video:
            self.add_video_frame()

        if self.csv:
            self.write_to_csv() 
        
        # Exploration reward
        r, c, map_n = ram_map.position(self.game)
                # Convert local position to global position
        try:
            glob_r, glob_c = game_map.local_to_global(r, c, map_n)
        except IndexError:
            print(f'IndexError: index {glob_r} or {glob_c} is out of bounds for axis 0 with size 444.')
            glob_r = 0
            glob_c = 0
        
        # Only reward for specified coordinates, not all coordinates seen
        if self.rewardable_coords(glob_c, glob_r):
            self.seen_coords.add((r, c, map_n))
        else:
            self.seen_coords_no_reward.add((glob_c, glob_r, map_n))

        if map_n != self.prev_map_n:
            self.prev_map_n = map_n
            if map_n not in self.seen_maps:
                self.seen_maps.add(map_n)
                self.talk_to_npc_count[map_n] = 0  # Initialize NPC talk count for this new map
                self.save_state()
                
     
        self.update_pokedex()
        self.update_moves_obtained()
        # obs = self.render()

        ############################################################### Added map_n into explore reward
        coord_reward = 0.01 * len(self.seen_coords)
        map_reward = 0.1 * len(self.seen_maps)
        exploration_reward = coord_reward + map_reward
        self.update_heat_map(r, c, map_n)


        # Level reward
        party_size, party_levels = ram_map.party(self.game)
        self.max_level_sum = max(self.max_level_sum, sum(party_levels))
        if self.max_level_sum < 30:
            level_reward = 1 * self.max_level_sum
        else:
            level_reward = 30 + (self.max_level_sum - 30) / 4
            
        # Healing and death rewards
        hp = ram_map.hp(self.game)
        hp_delta = hp - self.last_hp
        party_size_constant = party_size == self.last_party_size

        # Only reward if not reviving at pokecenter
        if hp_delta > 0 and party_size_constant and not self.is_dead:
            self.total_healing += hp_delta

        # Dead if hp is zero
        if hp <= 0 and self.last_hp > 0:
            self.death_count += 1
            self.is_dead = True
        elif hp > 0.01:  # TODO: Check if this matters
            self.is_dead = False

        # Update last known values for next iteration
        self.last_hp = hp
        self.last_party_size = party_size
        death_reward = 0 # -0.08 * self.death_count  # -0.05
        
        # Set rewards
        healing_reward = self.total_healing

        # Opponent level reward
        max_opponent_level = max(ram_map.opponent(self.game))
        self.max_opponent_level = max(self.max_opponent_level, max_opponent_level)
        opponent_level_reward = 0 # 0.2 * self.max_opponent_level

        # Badge reward
        badges = ram_map.badges(self.game)
        badges_reward = 5 * badges
        
        # Save Bill
        bill_state = ram_map.saved_bill(self.game)
        bill_reward = 10 * bill_state
        
        # SS Anne appeared
        ss_anne_state = ram_map.ss_anne_appeared(self.game)
        if ss_anne_state:
            ss_anne_state_reward = 5
        else:
            ss_anne_state_reward = 0
            
        # HM reward
        hm_count = self.get_hm_rewards()
        hm_reward = hm_count * 5

        # Event reward
        events = ram_map.events(self.game)
        self.max_events = max(self.max_events, events)
        event_reward = self.max_events

        # Money
        money = ram_map.money(self.game)
        

        if ram_map.mem_val(self.game, 0xCFC4):
            # check if we are talking to a hidden object:
            if ram_map.mem_val(self.game, 0xCD3D) == 0x0 and ram_map.mem_val(self.game, 0xCD3E) == 0x0:
                # add hidden object to seen hidden objects
                self.seen_hidden_objs.add((ram_map.mem_val(self.game, 0xD35E), ram_map.mem_val(self.game, 0xCD3F)))
            else:

                player_direction = ram_map.player_direction(self.game)
                player_y = ram_map.player_y(self.game)
                player_x = ram_map.player_x(self.game)

                mindex = (0, 0)
                minv = 1000
                for npc_bank in range(1):
                    
                    for npc_id in range(1, ram_map.sprites(self.game) + 15):
                        npc_dist = self.find_neighboring_npc(npc_bank, npc_id, player_direction, player_x, player_y)
                        if npc_dist < minv:
                            mindex = (npc_bank, npc_id)
                            minv = npc_dist        
                self.seen_npcs.add((ram_map.map_n(self.game), mindex[0], mindex[1]))

        explore_npcs_reward = self.reward_scale * self.explore_npc_weight * len(self.seen_npcs) * 0.00015
        seen_pokemon_reward = self.reward_scale * sum(self.seen_pokemon) * 0.00010
        caught_pokemon_reward = self.reward_scale * sum(self.caught_pokemon) * 0.00010
        moves_obtained_reward = self.reward_scale * sum(self.moves_obtained) * 0.00010
        explore_hidden_objs_reward = self.reward_scale * self.explore_hidden_obj_weight * len(self.seen_hidden_objs) * 0.00015

        reward = self.reward_scale * (
            event_reward
            + explore_npcs_reward
            + seen_pokemon_reward
            + caught_pokemon_reward
            + moves_obtained_reward
            + explore_hidden_objs_reward
            + bill_reward
            + hm_reward
            + level_reward
            # + opponent_level_reward
            # + death_reward
            + badges_reward
            + healing_reward
            + exploration_reward
        )

        # Subtract previous reward
        # TODO: Don't record large cumulative rewards in the first place
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
        if done:
            pokemon_info = data.pokemon_l(self.game)
            x, y ,map_n = ram_map.position(self.game)
            items = self.get_items_in_bag()
            reset = self.reset_count
            pokemon = []
            for p in pokemon_info:
                pokemon.append({
                    'env_id': self.env_id,
                    'slot': p['slot'],
                    'name': p['name'],
                    'level': p['level'],
                    'moves': p['moves'],
                    'items': items,
                })
            info = {
                "reward": {
                    "delta": reward,
                    "event": event_reward,
                    "level": level_reward,
                    "opponent_level": opponent_level_reward,
                    "death": death_reward,
                    "badges": badges_reward,
                    "bill_saved_reward": bill_reward,
                    "hm_count_award": hm_reward,
                    "ss_anne_present": ss_anne_state_reward,
                    "healing": healing_reward,
                    "exploration": exploration_reward,
                    "explore_npcs_reward": explore_npcs_reward,
                    "seen_pokemon_reward": seen_pokemon_reward,
                    "caught_pokemon_reward": caught_pokemon_reward,
                    "moves_obtained_reward": moves_obtained_reward,
                    "hidden_obj_count_reward": explore_hidden_objs_reward,
                },
                "maps_explored": len(self.seen_maps),
                "party_size": party_size,
                "highest_pokemon_level": max(party_levels),
                "total_party_level": sum(party_levels),
                "deaths": self.death_count,
                "bill_saved": bill_state,
                "hm_count": hm_count,
                "ss_anne_state": ss_anne_state,
                "badge_1": float(badges >= 1),
                "badge_2": float(badges >= 2),
                "event": events,
                "money": money,
                "pokemon_exploration_map": self.counts_map,
                "seen_npcs_count": len(self.seen_npcs),
                "seen_pokemon": sum(self.seen_pokemon),
                "caught_pokemon": sum(self.caught_pokemon),
                "moves_obtained": sum(self.moves_obtained),
                "hidden_obj_count": len(self.seen_hidden_objs),
                "logging": pokemon,
            }

        if self.verbose:
            print(
                f'number of signs: {ram_map.signs(self.game)}, number of sprites: {ram_map.sprites(self.game)}\n',
                f"steps: {self.time}\n",
                f"seen_npcs #: {len(self.seen_npcs)}\n",
                f"seen_npcs set: {self.seen_npcs}\n",
                # f"is_in_battle: {ram_map.is_in_battle(self.game)}",
                f"exploration reward: {exploration_reward}\n",
                f"explore_npcs reward: {explore_npcs_reward}\n",
                f"level_Reward: {level_reward}\n",
                f"healing: {healing_reward}\n",
                f"death: {death_reward}\n",
                f"op_level: {opponent_level_reward}\n",
                f"badges reward: {badges_reward}\n",
                f"event reward: {event_reward}\n",
                f"money: {money}\n",
                f"ai reward: {reward}\n",
                f"Info: {info}\n",
            )
        
        return self.render(), reward, done, done, info