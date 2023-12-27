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

from pokegym.pyboy_binding import (
    ACTIONS,
    make_env,
    open_state_file,
    load_pyboy_state,
    run_action_on_emulator,
)
from pokegym import ram_map, game_map

def debug_nice(locals_dict, keys=[]):
    globals()['types'] = __import__('types')
    exclude_keys = ['copyright', 'credits', 'False', 
                    'True', 'None', 'Ellipsis', 'quit']
    exclude_valuetypes = [types.BuiltinFunctionType,
                          types.BuiltinMethodType,
                          types.ModuleType,
                          types.FunctionType]
    return {k: v for k,v in locals_dict.items() if not
               (k in keys or
                k in exclude_keys or
                type(v) in exclude_valuetypes) and
               k[0] != '_'}

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
            # state_path = __file__.rstrip("environment.py") + "has_pokedex_nballs.state"
            state_path = "/home/daa/puffer0.5.2_iron/bill/pokegym/pokegym/current_state/has_pokedex_nballs.state" # .rstrip("environment.py") + "has_pokedex_nballs.state"
                # Make the environment
        self.game, self.screen = make_env(rom_path, headless, quiet, save_video=False, **kwargs)

        # #BET ADDED
        # self.frame_stacks = 4
        # self.output_shape = (36, 40)
        # self.mem_padding = 2
        # self.memory_height = 8
        # self.col_steps = 16
        # self.output_full = (
        #     self.frame_stacks,
        #     self.output_shape[0],
        #     self.output_shape[1]
        # )
        # self.output_vector_shape = (54, )
        
        self.initial_states = [open_state_file(state_path)]
        self.save_video = save_video
        self.headless = headless
        self.mem_padding = 2
        self.memory_shape = 80
        self.use_screen_memory = True
        self.screenshot_counter = 0
        self.s_path = Path(f'session_{str(uuid.uuid4())[:8]}')
        self.instance_id = str(uuid.uuid4())[:8]
        self.reset_count = 0
        
        # R, C = self.screen.raw_screen_buffer_dims()
        # self.obs_size = (R // 2, C // 2) # (self.obs_size = 144 // 2, 160 // 2) = (72, 80)
        # # T()        
        # #BET ADDED
        # # self.output_shape = self.obs_size # (72, 80, self.frame_stacks)
        # # self.coords_pad = 12
        
        # #BET ADDED
        # self.recent_screens = np.zeros((self.obs_size[0], self.obs_size[1], 4), dtype=np.uint8) # (72, 80)
        # self.seen_pokemon = np.zeros(152, dtype=np.uint8)
        # self.caught_pokemon = np.zeros(152, dtype=np.uint8)
        # self.moves_obtained = np.zeros(0xA5, dtype=np.uint8)
        # self.recent_actions = np.zeros((self.frame_stacks,), dtype=np.uint8)

        # if self.use_screen_memory:
        #     self.screen_memory = defaultdict(
        #         lambda: np.zeros((255, 255, 1), dtype=np.uint8)
        #     )
        #     self.obs_size += (4,)
        # else:
        #     self.obs_size += (3,)
        
        # #BET ADDED
        # self.observation_space = spaces.Dict(
        #     {
        #         "screens": spaces.Box(low=0, high=255, dtype=np.uint8, shape=self.obs_size), # Box(0, 255, (72, 80, 4), uint8)
        #         # "health": spaces.Box(low=0, high=1),
        #         # "level": spaces.Box(low=-1, high=1, shape=(self.enc_freqs,)),
        #         # "badges": spaces.MultiBinary(8),
        #         # "events": spaces.MultiBinary((event_flags_end - event_flags_start) * 8),
        #         # "map": spaces.Box(low=0, high=255, shape=(
        #         #     self.coords_pad*4,self.coords_pad*4, 1), dtype=np.uint8),
        #         "recent_actions": spaces.MultiDiscrete([len(ACTIONS)] * self.frame_stacks), # MultiDiscrete([8 8 8 8])
        #         "seen_pokemon": spaces.MultiBinary(152),
        #         "caught_pokemon": spaces.MultiBinary(152),
        #         "moves_obtained": spaces.MultiBinary(0xA5) # (165)
        #     }
        # )   
        # # T()    
        # self.action_space = spaces.Discrete(len(ACTIONS)) # Discrete(8)
               
        self.explore_hidden_obj_weight = 1
    
        # print(f'self.observation_space.sample(): {self.observation_space.sample()}')
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
    # print(f'SCREENSHOT TAKEN!\n')
        self.screenshot_counter += 1
        # print(f'screenshots taken: {self.screenshot_counter} \n')
        ss_dir = Path('screenshots')
        ss_dir.mkdir(exist_ok=True)
        plt.imsave(
            # ss_dir / Path(f'ss_{x}_y_{y}_steps_{steps}_{comment}.jpeg'),
            ss_dir / Path(f'{self.screenshot_counter}_{event}_{map_n}.jpeg'),
            self.screen.screen_ndarray())  # (144, 160, 3)
        # print(f'TOOK SCREENSHOT\n')

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

    # def render(self):
    #     if self.use_screen_memory:
    #         r, c, map_n = ram_map.position(self.game)
    #         # Update tile map
    #         mmap = self.screen_memory[map_n]
    #         if 0 <= r <= 254 and 0 <= c <= 254:
    #             mmap[r, c] = 255

    #         # Downsamples the screen and retrieves a fixed window from mmap,
    #         # then concatenates along the 3rd-dimensional axis (image channel)
            
    #         ''' 
    #         characteristics of mmap
    #         (Pdb) p np.size(mmap)
    #         65025
    #         (Pdb) p np.shape(mmap)
    #         (255, 255, 1)                        
    #         '''
    #         game_pixels_render = np.concatenate(
    #             (
    #                 self.screen.screen_ndarray()[::2, ::2],
    #                 self.get_fixed_window(mmap, r, c, self.obs_size), # (72, 80, 4)                    
    #             ),
    #             axis=2,
    #         )
    #         return game_pixels_render
    #     else:
    #         game_pixels_render = self.screen.screen_ndarray()[::2, ::2]
    #         return game_pixels_render
    
    # def render(self, reduce_res=True, add_memory=True, update_mem=True):
    #     if self.use_screen_memory:
    #         r, c, map_n = ram_map.position(self.game)
    #         mmap = self.screen_memory[map_n]
    #         if 0 <= r <= 254 and 0 <= c <= 254:
    #             mmap[r, c] = 255

    #         print(f'mmap BEFORE np.concat: {np.shape(mmap)}')
            
    #         game_pixels_render  = np.concatenate(
    #             (
    #                 # self.screen.screen_ndarray()[::2, ::2],
    #                 self.screen.screen_ndarray(),
    #                 self.get_fixed_window(mmap, r, c, self.obs_size), # (72, 80, 4)                
    #             ),
    #             axis=2,
    #         )
    #         print(f'game_pixels_render AFTER np.concat: {np.shape(game_pixels_render)}')
    #     else:
    #         game_pixels_render  = self.screen.screen_ndarray()[::2, ::2]
    #         print(f'game_pixels_render ELSE: {np.shape(game_pixels_render)}')

    #     if reduce_res:
    #         game_pixels_render = game_pixels_render[:, :, 0] # should be 3x speed up for rendering
    #         game_pixels_render = (255*resize(game_pixels_render, self.output_shape)).astype(np.uint8)
    #         print(f'game_pixels_render IF REDUCE_RES: {np.shape(game_pixels_render)}')
    #         if update_mem:
    #             reduced_frame = game_pixels_render
    #             self.recent_frames[0] = reduced_frame
    #             print(f'game_pixels_render IF UPDATE_MEM: {np.shape(game_pixels_render)}')
    #         if add_memory:
    #             game_pixels_render = {
    #                 'screens': self.recent_frames,
    #                 'recent_actions': self.recent_actions,
    #                 'seen_pokemon': self.seen_pokemon,
    #                 'caught_pokemon': self.caught_pokemon,
    #                 'moves_obtained': self.moves_obtained,
    #             }
    #     print(f'game_pixels_render FINAL: {np.shape(game_pixels_render)}')
    #     return game_pixels_render

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

    def step(self, action):
        run_action_on_emulator(self.game, self.screen, ACTIONS[action], self.headless)
        return self.render(), 0, False, False, {}

    def close(self):
        self.game.stop(False)
        
    # def update_recent_screens(self, cur_screen):
    #     cur_screen = np.squeeze(cur_screen)
    #     print("Shapes - recent_screens:", self.recent_screens.shape, "cur_screen:", cur_screen.shape)
    #     self.recent_screens = np.roll(self.recent_screens, 1, axis=0)
    #     self.recent_screens[:, :, 0] = cur_screen[:, :, 0]
        
    # def _get_obs(self):
        
    #     obs = self.render()

    #     # self.update_recent_screens(screen)

    #     observation = {
    #         "screens": self.recent_screens,
    #         # "screens": self.recent_screens,
    #         # "health": np.array([self.read_hp_fraction()]),
    #         # "level": self.fourier_encode(level_sum),
    #         # "badges": np.array([int(bit) for bit in f"{self.game.get_memory_value(0xD356):08b}"], dtype=np.int8),
    #         # "events": np.array(self.read_event_bits(), dtype=np.int8),
    #         # "map": self.get_explore_map()[:, :, None],
    #         "recent_actions": self.recent_actions,
    #         "caught_pokemon": self.caught_pokemon,
    #         "seen_pokemon": self.seen_pokemon,
    #         "moves_obtained": self.moves_obtained,
    #     }
        
    #     # Add a channel dimension to each NumPy array because models.py, line 213, in encode observations:
    #     # observations = observations.permute(0, 3, 1, 2)
    #     for key, value in observation.items():
    #         if isinstance(value, np.ndarray):
    #             observation[key] = np.expand_dims(value, axis=-1)        
                
    #     return observation

# T()

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
        
    # def find_neighboring_npc(self, npc_id, player_direction, player_x, player_y) -> int:

    #     npc_y = self.game.get_memory_value(0xC104 + (npc_id * 0x10))
    #     npc_x = self.game.get_memory_value(0xC106 + (npc_id * 0x10))

    #     # Check if player is facing the NPC (skip NPC direction)
    #     # 0 - down, 4 - up, 8 - left, 0xC - right
    #     if (
    #         (player_direction == 0 and npc_x == player_x and npc_y > player_y) or
    #         (player_direction == 4 and npc_x == player_x and npc_y < player_y) or
    #         (player_direction == 8 and npc_y == player_y and npc_x < player_x) or
    #         (player_direction == 0xC and npc_y == player_y and npc_x > player_x)
    #     ):
    #         # Manhattan distance
    #         return abs(npc_y - player_y) + abs(npc_x - player_x)

    #     return 1000

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
    
    # def update_recent_actions(self, action):
    #     self.recent_actions = np.roll(self.recent_actions, 1)
    #     self.recent_actions[0] = action
        
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
            base_dir = self.s_path
            base_dir.mkdir(parents=True, exist_ok=True)
            full_name = Path(f'reset_{self.reset_count}').with_suffix('.mp4')
            self.full_frame_writer = media.VideoWriter(base_dir / full_name, (144, 160), fps=60)
            self.full_frame_writer.__enter__()

        if self.use_screen_memory:
            self.screen_memory = defaultdict(
                lambda: np.zeros((255, 255, 1), dtype=np.uint8)
            )
        
        #BET ADDED
        # self.recent_frames = np.zeros(
        #     (self.frame_stacks, self.output_shape[0], 
        #     self.output_shape[1]),
        #     dtype=np.uint8)
        
        self.time = 0
        self.max_episode_steps = max_episode_steps
        self.reward_scale = reward_scale
        self.prev_map_n = None
        
        #BET ADDED
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
                
        #BET ADDED
        # self.recent_frames = np.roll(self.recent_frames, 1, axis=0)
        # self.update_recent_actions(action)        
        self.update_pokedex()
        self.update_moves_obtained()
        # obs = self.render()

        exploration_reward = 0.01 * len(self.seen_coords)
        self.update_heat_map(r, c, map_n)
        # glob_r, glob_c = game_map.local_to_global(r, c, map_n)
        # try:
        #     self.counts_map[glob_r, glob_c] += 1
        # except:
        #     pass

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

        money = ram_map.money(self.game)
        
        #  # check if the font is loaded
        # if self.game.get_memory_value(0xCFC4):
        #     # check if we are talking to a hidden object:
        #     if self.game.get_memory_value(0xCD3D) == 0x0 and self.game.get_memory_value(0xCD3E) == 0x0:
        #         # add hidden object to seen hidden objects
        #         self.seen_hidden_objs.add((self.game.get_memory_value(0xD35E), self.game.get_memory_value(0xCD3F)))
        #     else:
        #         # get information for player
        #         player_direction = self.game.get_memory_value(0xC109)
        #         player_y = self.game.get_memory_value(0xC104)
        #         player_x = self.game.get_memory_value(0xC106)
        #         # get the npc who is closest to the player and facing them
        #         # we go through all npcs because there are npcs like
        #         # nurse joy who can be across a desk and still talk to you
        #         mindex = 0
        #         minv = 1000
        #         for npc_id in range(1, self.game.get_memory_value(0xD4E1)):
        #             npc_dist = self.find_neighboring_npc(npc_id, player_direction, player_x, player_y)
        #             if npc_dist < minv:
        #                 mindex = npc_id
        #                 minv = npc_dist
        #         if mindex != 0:
        #             self.seen_npcs.add((self.game.get_memory_value(0xD35E), mindex))
        
        # names = ram_map.pokemon(self.game)
        # print(f'names of pokemon in party: {names}')
        names_l = ram_map.pokemon_l(self.game)
        print(f'names_l = {names_l}')  
        # Explore NPCs
                # check if the font is loaded
        if ram_map.mem_val(self.game, 0xCFC4):
            # check if we are talking to a hidden object:
            if ram_map.mem_val(self.game, 0xCD3D) == 0x0 and ram_map.mem_val(self.game, 0xCD3E) == 0x0:
                # add hidden object to seen hidden objects
                self.seen_hidden_objs.add((ram_map.mem_val(self.game, 0xD35E), ram_map.mem_val(self.game, 0xCD3F)))
            else:
                # check if we are talking to someone
                # if ram_map.if_font_is_loaded(self.game):
                    # get information for player
                player_direction = ram_map.player_direction(self.game)
                player_y = ram_map.player_y(self.game)
                player_x = ram_map.player_x(self.game)
                # get the npc who is closest to the player and facing them
                # we go through all npcs because there are npcs like
                # nurse joy who can be across a desk and still talk to you
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
            + opponent_level_reward
            + death_reward
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
                    "ss_anne_done_reward": ss_anne_state_reward,
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
