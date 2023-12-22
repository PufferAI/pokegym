
import sys
import uuid 
import os
from math import floor, sqrt
import json
import pickle
from pathlib import Path

import numpy as np
from einops import rearrange
import matplotlib.pyplot as plt
from skimage.transform import resize
from pyboy import PyBoy
import hnswlib
import mediapy as media
import pandas as pd

from gymnasium import Env, spaces
from pyboy.utils import WindowEvent

class RedGymEnvV3(Env):


    def __init__(
        self, config=None):

        self.debug = config['debug']
        self.s_path = config['session_path']
        self.save_final_state = config['save_final_state']
        self.print_rewards = config['print_rewards']
        self.vec_dim = 4320 #1000
        self.headless = config['headless']
        self.num_elements = 20000 # max
        self.init_state = config['init_state']
        self.act_freq = config['action_freq']
        self.max_steps = config['max_steps']
        self.early_stopping = config['early_stop']
        self.save_video = config['save_video']
        self.fast_video = config['fast_video']
        self.video_interval = 256 * self.act_freq
        self.downsample_factor = 2
        self.frame_stacks = 3
        self.explore_weight = 1 if 'explore_weight' not in config else config['explore_weight']
        self.use_screen_explore = True if 'use_screen_explore' not in config else config['use_screen_explore']
        self.randomize_first_ep_split_cnt = 0 if 'randomize_first_ep_split_cnt' not in config else config['randomize_first_ep_split_cnt']
        self.similar_frame_dist = config['sim_frame_dist']
        self.reward_scale = 1 if 'reward_scale' not in config else config['reward_scale']
        self.extra_buttons = False if 'extra_buttons' not in config else config['extra_buttons']
        self.debug_buttons = False if 'debug_buttons' not in config else config['debug_buttons']
        self.restricted_start_menu = False if 'restricted_start_menu' not in config else config['restricted_start_menu']
        self.instance_id = str(uuid.uuid4())[:8] if 'instance_id' not in config else config['instance_id']
        self.save_state_dir = None if 'save_state_dir' not in config else config['save_state_dir']
        self.s_path.mkdir(exist_ok=True)
        self.warmed_up = False  # for randomize_first_ep_split_cnt usage
        self.reset_count = 0
        self.all_runs = []
        self.n_pokemon_features = 23

        # Set this in SOME subclasses
        self.metadata = {"render.modes": []}
        self.reward_range = (0, 15000)
        # self.pokecenter_ids = [0x29, 0x3A, 0x40, 0x44, 0x51, 0x59, 0x85, 0x8D, 0x9A, 0xAB, 0xB6]
        self.pokecenter_ids = [0x01, 0x02, 0x03, 0x0F, 0x15, 0x05, 0x06, 0x04, 0x07, 0x08, 0x0A]
        self.valid_actions = [
            WindowEvent.PRESS_ARROW_DOWN,
            WindowEvent.PRESS_ARROW_LEFT,
            WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_UP,
            WindowEvent.PRESS_BUTTON_A,
            WindowEvent.PRESS_BUTTON_B,
        ]
        
        if self.extra_buttons:
            self.valid_actions.extend([
                WindowEvent.PRESS_BUTTON_START,
                # WindowEvent.PASS
            ])

        if self.debug_buttons:
            self.valid_actions.extend([
                WindowEvent.PASS
            ])

        self.release_arrow = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP
        ]

        self.release_button = [
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B
        ]

        self.output_shape = (36, 40)
        self.mem_padding = 2
        self.memory_height = 8
        self.col_steps = 16
        self.output_full = (
            self.frame_stacks,
            self.output_shape[0],
            self.output_shape[1]
        )
        self.output_vector_shape = (54, )

        # Set these in ALL subclasses
        self.action_space = spaces.Discrete(len(self.valid_actions))
        # self.observation_space = spaces.Box(low=0, high=255, shape=self.output_full, dtype=np.uint8)
        self.observation_space = spaces.Dict({
            'image': spaces.Box(low=0, high=255, shape=self.output_full, dtype=np.uint8),
            'vector': spaces.Box(low=-1, high=1, shape=self.output_vector_shape, dtype=np.float32),
            'map_ids': spaces.Box(low=0, high=255, shape=(1,), dtype=np.uint8),
            'item_ids': spaces.Box(low=0, high=255, shape=(20,), dtype=np.uint8),
            'item_quantity': spaces.Box(low=-1, high=1, shape=(20, 1), dtype=np.float32),
            'poke_ids': spaces.Box(low=0, high=255, shape=(12,), dtype=np.uint8),
            'poke_type_ids': spaces.Box(low=0, high=255, shape=(12, 2), dtype=np.uint8),
            'poke_move_ids': spaces.Box(low=0, high=255, shape=(12, 4), dtype=np.uint8),
            'poke_move_pps': spaces.Box(low=-1, high=1, shape=(12, 4, 2), dtype=np.float32),
            'poke_all': spaces.Box(low=-1, high=1, shape=(12, self.n_pokemon_features), dtype=np.float32),
            'event_ids': spaces.Box(low=0, high=2570, shape=(10,), dtype=np.int16),
            'event_step_since': spaces.Box(low=-1, high=1, shape=(10, 1), dtype=np.float32),
            # 'in_battle_mask': spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
        })

        head = 'headless' if config['headless'] else 'SDL2'

        self.pyboy = PyBoy(
                config['gb_path'],
                debugging=False,
                disable_input=False,
                window_type=head,
                hide_window='--quiet' in sys.argv,
            )

        self.screen = self.pyboy.botsupport_manager().screen()

        if not config['headless']:
            self.pyboy.set_emulation_speed(1)
            
        self.reset()

    def reset(self, seed=None):
        self.seed = seed
        
        if self.use_screen_explore:
            self.init_knn()
        else:
            self.init_map_mem()

        # restart game, skipping credits
        with open(self.init_state, "rb") as f:
            self.pyboy.load_state(f)

        self.recent_memory = np.zeros((self.output_shape[1]*self.memory_height, 3), dtype=np.uint8)
        
        self.recent_frames = np.zeros(
            (self.frame_stacks, self.output_shape[0], 
            self.output_shape[1]),
            dtype=np.uint8)

        self.agent_stats = []
        self.levels_satisfied = False
        self.base_explore = 0
        self.max_opponent_level = 0
        self.max_event_rew = 0
        self.max_level_rew = 0
        self.last_health = 1
        self.last_num_poke = 1
        self.total_healing_rew = 0
        self.died_count = 0
        self.prev_knn_rew = 0
        self.visited_pokecenter_list = []
        self.last_10_map_ids = np.zeros(10, dtype=np.uint8)
        self.last_10_coords = np.zeros((10, 2), dtype=np.uint8)
        self.init_caches()
        self.past_events_string = ''
        self.last_10_event_ids = np.zeros((10, 2), dtype=np.float32)
        self.early_done = False
        self.step_count = 0
        self.past_rewards = np.zeros(10240, dtype=np.float32)
        self.progress_reward = self.get_game_state_reward()
        self.total_reward = sum([val for _, val in self.progress_reward.items()])
        self.reset_count += 1
        
        if self.save_video:
            base_dir = self.s_path / Path('rollouts')
            base_dir.mkdir(exist_ok=True)
            full_name = Path(f'full_reset_{self.reset_count}_id{self.instance_id}').with_suffix('.mp4')
            model_name = Path(f'model_reset_{self.reset_count}_id{self.instance_id}').with_suffix('.mp4')
            self.full_frame_writer = media.VideoWriter(base_dir / full_name, (144, 160), fps=60)
            self.full_frame_writer.__enter__()
            self.model_frame_writer = media.VideoWriter(base_dir / model_name, self.output_full[:2], fps=60)
            self.model_frame_writer.__enter__()
       
        return self.render(), {}
    
    def init_knn(self):
        # Declaring index
        self.knn_index = hnswlib.Index(space='l2', dim=self.vec_dim) # possible options are l2, cosine or ip
        # Initing index - the maximum number of elements should be known beforehand
        self.knn_index.init_index(
            max_elements=self.num_elements, ef_construction=100, M=16)
        
    def init_map_mem(self):
        self.seen_coords = {}

    def render(self, reduce_res=True, add_memory=True, update_mem=True):
        game_pixels_render = self.screen.screen_ndarray() # (144, 160, 3)
        if reduce_res:
            game_pixels_render = game_pixels_render[:, :, 0]  # should be 3x speed up for rendering
            game_pixels_render = (255*resize(game_pixels_render, self.output_shape)).astype(np.uint8)
            if update_mem:
                reduced_frame = game_pixels_render
                self.recent_frames[0] = reduced_frame
            if add_memory:
                # pad = np.zeros(
                #     shape=(self.mem_padding, self.output_shape[1], 3), 
                #     dtype=np.uint8)
                # game_pixels_render = np.concatenate(
                #     (
                #         self.create_exploration_memory(), 
                #         pad,
                #         self.create_recent_memory(),
                #         pad,
                #         rearrange(self.recent_frames, 'f h w c -> (f h) w c')
                #     ),
                #     axis=0)
                game_pixels_render = {
                    'image': self.recent_frames,
                    'vector': self.get_all_raw_obs(),
                    'map_ids': self.get_last_map_id_obs(),
                    'item_ids': self.get_all_item_ids_obs(),
                    'item_quantity': self.get_items_quantity_obs(),
                    'poke_ids': self.get_all_pokemon_ids_obs(),
                    'poke_type_ids': self.get_all_pokemon_types_obs(),
                    'poke_move_ids': self.get_all_move_ids_obs(),
                    'poke_move_pps': self.get_all_move_pps_obs(),
                    'poke_all': self.get_all_pokemon_obs(),
                    'event_ids': self.get_all_event_ids_obs(),
                    'event_step_since': self.get_all_event_step_since_obs(),
                    # 'in_battle_mask': self.get_in_battle_mask_obs(),
                }

        return game_pixels_render
    
    def update_last_10_map_ids(self):
        current_modified_map_id = self.read_m(0xD35E) + 1
        # check if current_modified_map_id is in last_10_map_ids
        if current_modified_map_id == self.last_10_map_ids[0]:
            return
        else:
            self.last_10_map_ids = np.roll(self.last_10_map_ids, 1)
            self.last_10_map_ids[0] = current_modified_map_id

    def update_last_10_coords(self):
        current_coord = np.array([self.read_m(0xD362), self.read_m(0xD361)])
        # check if current_coord is in last_10_coords
        if (current_coord == self.last_10_coords[0]).all():
            return
        else:
            self.last_10_coords = np.roll(self.last_10_coords, 1, axis=0)
            self.last_10_coords[0] = current_coord
    
    def step(self, action):
        self.run_action_on_emulator(action)
        self.init_caches()
        self.check_if_early_done()
        self.append_agent_stats(action)

        self.update_last_10_map_ids()
        self.update_last_10_coords()
        self.recent_frames = np.roll(self.recent_frames, 1, axis=0)
        obs_memory = self.render()


        if self.use_screen_explore:
            # trim off memory from frame for knn index
            obs_flat = obs_memory['image'].flatten().astype(np.float32)
            self.update_frame_knn_index(obs_flat)
        else:
            self.update_seen_coords()
            
        self.update_heal_reward()
        self.update_num_poke()

        new_reward = self.update_reward()
        
        self.last_health = self.read_hp_fraction()

        # shift over short term reward memory
        # self.recent_memory = np.roll(self.recent_memory, 3)
        # self.recent_memory[0, 0] = min(new_prog[0] * 64, 255)
        # self.recent_memory[0, 1] = min(new_prog[1] * 64, 255)
        # self.recent_memory[0, 2] = min(new_prog[2] * 128, 255)

        self.update_past_events()
        self.past_events_string = self.all_events_string

        # record past rewards
        self.past_rewards = np.roll(self.past_rewards, 1)
        self.past_rewards[0] = self.total_reward

        step_limit_reached = self.check_if_done()
        
        if not self.warmed_up and self.randomize_first_ep_split_cnt and \
            self.step_count and self.step_count % (self.max_steps // self.randomize_first_ep_split_cnt) == 0 and \
            1.0 / self.randomize_first_ep_split_cnt > np.random.rand():
            # not warmed up yet
            # check if step count reached the checkpoint of randomize_first_ep_split_cnt
            # if reached, randomly decide to end the episode based on randomize_first_ep_split_cnt
            step_limit_reached = True
            self.warmed_up = True
            print(f'randomly end episode at step {self.step_count} with randomize_first_ep_split_cnt: {self.randomize_first_ep_split_cnt}')

        self.save_and_print_info(step_limit_reached, obs_memory)

        self.step_count += 1

        return obs_memory, new_reward*0.1, False, step_limit_reached, {}
    
    def init_caches(self):
        # for cached properties
        self._all_events_string = ''
        self._battle_type = -999
    
    def get_first_diff_index(self, arr1, arr2):
        for i in range(len(arr1)):
            if arr1[i] != arr2[i]:
                return i
        return -1
    
    def update_past_events(self):
        if self.past_events_string and self.past_events_string != self.all_events_string:
            self.last_10_event_ids = np.roll(self.last_10_event_ids, 1, axis=0)
            self.last_10_event_ids[0] = [self.get_first_diff_index(self.past_events_string, self.all_events_string), self.step_count]
    
    def is_in_start_menu(self) -> bool:
        menu_check_dict = {
            'wFontLoaded': self.read_m(0xCFC4) == 1,
            'wUpdateSpritesEnabled': self.read_m(0xcfcb) == 1,
            'wMenuWatchedKeys': self.read_m(0xcc29) == 203,
            'wTopMenuItemY': self.read_m(0xcc24) == 2,
            'wTopMenuItemX': self.read_m(0xcc25) == 11,
        }
        for val in menu_check_dict.values():
            if not val:
                return False
        return True
        # return self.read_m(0xD057) == 0x0A

    def get_menu_restricted_action(self, action: int) -> int:
        if not self.is_in_battle():
            if self.is_in_start_menu():
                # not in battle and in start menu
                # if wCurrentMenuItem == 1, then up / down will be changed to down
                # if wCurrentMenuItem == 2, then up / down will be changed to up
                current_menu_item = self.read_m(0xCC26)
                if current_menu_item not in [1, 2]:
                    print(f'\nWarning! current start menu item: {current_menu_item}, not 1 or 2')
                    # do nothing, return action
                    return action
                if action < 4:
                    # any arrow key will be changed to down if wCurrentMenuItem == 1
                    # any arrow key will be changed to up if wCurrentMenuItem == 2
                    if current_menu_item == 1:
                        action = 0  # down
                    elif current_menu_item == 2:
                        action = 3  # up
                pass
            else:
                # no in battle and start menu, pressing START
                # opening menu, always set to 1
                self.pyboy.set_memory_value(0xCC2D, 1)  # wBattleAndStartSavedMenuItem
        return action


    def run_action_on_emulator(self, action):
        if self.extra_buttons and self.restricted_start_menu:
            # restrict start menu choices
            action = self.get_menu_restricted_action(action)
        # press button then release after some steps
        self.pyboy.send_input(self.valid_actions[action])
        # disable rendering when we don't need it
        if self.headless and (self.fast_video or not self.save_video):
            self.pyboy._rendering(False)
        for i in range(self.act_freq):
            # release action, so they are stateless
            if i == 8:
                if action < 4:
                    # release arrow
                    self.pyboy.send_input(self.release_arrow[action])
                if action > 3 and action < 6:
                    # release button 
                    self.pyboy.send_input(self.release_button[action - 4])
                if self.valid_actions[action] == WindowEvent.PRESS_BUTTON_START:
                    self.pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)
            if self.save_video and not self.fast_video:
                self.add_video_frame()
            if i == self.act_freq-1:
                self.pyboy._rendering(True)
            self.pyboy.tick()
        if self.save_video and self.fast_video:
            self.add_video_frame()
    
    def add_video_frame(self):
        self.full_frame_writer.add_image(self.render(reduce_res=False, update_mem=False))
        # self.model_frame_writer.add_image(self.render(reduce_res=True, update_mem=False))
    
    def append_agent_stats(self, action):
        x_pos = self.read_m(0xD362)
        y_pos = self.read_m(0xD361)
        map_n = self.read_m(0xD35E)
        levels = [self.read_m(a) for a in [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]]
        if self.use_screen_explore:
            expl = ('frames', self.knn_index.get_current_count())
        else:
            expl = ('coord_count', len(self.seen_coords))
        self.agent_stats.append({
            'step': self.step_count, 'x': x_pos, 'y': y_pos, 'map': map_n,
            'last_action': action,
            'pcount': self.read_m(0xD163), 
            'levels': levels, 
            'ptypes': self.read_party(),
            'hp': self.read_hp_fraction(),
            expl[0]: expl[1],
            'prev_knn_rew': self.prev_knn_rew,
            # 'deaths': self.died_count, 
            'badge': self.get_badges(),
            'eventr': self.progress_reward['event'],
            'levelr': self.progress_reward['level'],
            'op_lvlr': self.progress_reward['op_lvl'],
            'deadr': self.progress_reward['dead'],
            'visited_pokecenterr': self.progress_reward['visited_pokecenter'],
            'hmr': self.progress_reward['hm'],
            'hm_mover': self.progress_reward['hm_move'],
            'rewards': self.total_reward,
            'early_done': self.early_done,
        })

    def update_frame_knn_index(self, frame_vec):
        
        # if self.get_levels_sum() >= 22 and not self.levels_satisfied:
        #     self.levels_satisfied = True
        #     self.base_explore = self.knn_index.get_current_count()
        #     self.init_knn()

        if self.knn_index.get_current_count() == 0:
            # if index is empty add current frame
            self.knn_index.add_items(
                frame_vec, np.array([self.knn_index.get_current_count()])
            )
        else:
            # check for nearest frame and add if current 
            labels, distances = self.knn_index.knn_query(frame_vec, k = 1)
            if distances[0][0] > self.similar_frame_dist:
                # print(f"distances[0][0] : {distances[0][0]} similar_frame_dist : {self.similar_frame_dist}")
                self.knn_index.add_items(
                    frame_vec, np.array([self.knn_index.get_current_count()])
                )
    
    def update_seen_coords(self):
        x_pos = self.read_m(0xD362)
        y_pos = self.read_m(0xD361)
        map_n = self.read_m(0xD35E)
        coord_string = f"x:{x_pos} y:{y_pos} m:{map_n}"
        # if self.get_levels_sum() >= 22 and not self.levels_satisfied:
        #     self.levels_satisfied = True
        #     self.base_explore = len(self.seen_coords)
        #     self.seen_coords = {}
        
        self.seen_coords[coord_string] = self.step_count

    def update_reward(self):
        # compute reward
        # old_prog = self.group_rewards()
        self.progress_reward = self.get_game_state_reward()
        # new_prog = self.group_rewards()
        new_total = sum([val for _, val in self.progress_reward.items()]) #sqrt(self.explore_reward * self.progress_reward)
        new_step = new_total - self.total_reward
        # if new_step < 0 and self.read_hp_fraction() > 0:
        #     #print(f'\n\nreward went down! {self.progress_reward}\n\n')
        #     self.save_screenshot('neg_reward')
    
        self.total_reward = new_total
        return new_step
    
    def group_rewards(self):
        prog = self.progress_reward
        # these values are only used by memory
        return (prog['level'] * 100 / self.reward_scale, 
                self.read_hp_fraction()*2000, 
                prog['explore'] * 150 / (self.explore_weight * self.reward_scale))
               #(prog['events'], 
               # prog['levels'] + prog['party_xp'], 
               # prog['explore'])

    def create_exploration_memory(self):
        w = self.output_shape[1]
        h = self.memory_height
        
        def make_reward_channel(r_val):
            col_steps = self.col_steps
            max_r_val = (w-1) * h * col_steps
            # truncate progress bar. if hitting this
            # you should scale down the reward in group_rewards!
            r_val = min(r_val, max_r_val)
            row = floor(r_val / (h * col_steps))
            memory = np.zeros(shape=(h, w), dtype=np.uint8)
            memory[:, :row] = 255
            row_covered = row * h * col_steps
            col = floor((r_val - row_covered) / col_steps)
            memory[:col, row] = 255
            col_covered = col * col_steps
            last_pixel = floor(r_val - row_covered - col_covered) 
            memory[col, row] = last_pixel * (255 // col_steps)
            return memory
        
        level, hp, explore = self.group_rewards()
        full_memory = np.stack((
            make_reward_channel(level),
            make_reward_channel(hp),
            make_reward_channel(explore)
        ), axis=-1)
        
        if self.get_badges() > 0:
            full_memory[:, -1, :] = 255

        return full_memory

    def create_recent_memory(self):
        return rearrange(
            self.recent_memory, 
            '(w h) c -> h w c', 
            h=self.memory_height)
    
    def check_if_early_done(self):
        self.early_done = False
        if self.early_stopping and self.step_count > 10241:
            self.early_done = self.past_rewards[0] - self.past_rewards[-1] < 1
            if self.early_done:
                print(f'es, step: {self.step_count}, r1: {self.past_rewards[0]}, r2: {self.past_rewards[-1]}')
        return self.early_done

    def check_if_done(self):
        done = self.step_count >= self.max_steps
        if self.early_done:
            done = True
        return done

    def save_and_print_info(self, done, obs_memory):
        if self.print_rewards:
            prog_string = f'step: {self.step_count:6d} reset: {self.reset_count:4d}'
            for key, val in self.progress_reward.items():
                if key in ['level', 'explore']:
                    prog_string += f' {key}: {val:6.2f}'
                else:
                    prog_string += f' {key}: {val:5.2f}'
            prog_string += f' sum: {self.total_reward:5.2f}'
            print(f'\r{prog_string}', end='', flush=True)
        
        if self.step_count % 1000 == 0:
            try:
                plt.imsave(
                    self.s_path / Path(f'curframe_{self.instance_id}.jpeg'), 
                    self.render(reduce_res=False))
            except:
                pass

        if self.print_rewards and done:
            print('', flush=True)
            if self.save_final_state:
                fs_path = self.s_path / Path('final_states')
                fs_path.mkdir(exist_ok=True)
                try:
                    # plt.imsave(
                    #     fs_path / Path(f'frame_r{self.total_reward:.4f}_{self.reset_count}_small.jpeg'), 
                    #     rearrange(obs_memory['image'], 'c h w -> h w c'))
                    plt.imsave(
                        fs_path / Path(f'frame_r{self.total_reward:.4f}_{self.reset_count}_full.jpeg'), 
                        self.render(reduce_res=False))
                except Exception as e:
                    print(f'error saving final state: {e}')
                if self.save_state_dir:
                    self.save_all_states()

        if self.save_video and done:
            self.full_frame_writer.close()
            self.model_frame_writer.close()

        if done:
            self.all_runs.append(self.progress_reward)
            with open(self.s_path / Path(f'all_runs_{self.instance_id}.json'), 'w') as f:
                json.dump(self.all_runs, f)
            pd.DataFrame(self.agent_stats).to_csv(
                self.s_path / Path(f'agent_stats_{self.instance_id}.csv.gz'), compression='gzip', mode='a')
    
    def read_m(self, addr):
        return self.pyboy.get_memory_value(addr)

    def read_bit(self, addr, bit: int) -> bool:
        # add padding so zero will read '0b100000000' instead of '0b0'
        return bin(256 + self.read_m(addr))[-bit-1] == '1'
    
    def get_levels_sum(self):
        poke_levels = [max(self.read_m(a) - 2, 0) for a in [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]]
        return max(sum(poke_levels) - 4, 0) # subtract starting pokemon level
    
    def get_levels_reward(self):
        level_sum = self.get_levels_sum()
        self.max_level_rew = max(self.max_level_rew, level_sum)
        return self.max_level_rew * 0.5
    
    def get_early_done_reward(self):
        return self.early_done * -0.2
    
    def get_knn_reward(self, last_event_rew):
        if last_event_rew != self.max_event_rew:
            # event reward increased, reset exploration
            if self.use_screen_explore:
                self.prev_knn_rew += self.knn_index.get_current_count()
                self.knn_index.clear_index()
            else:
                self.prev_knn_rew += len(self.seen_coords)
                self.seen_coords = {}
        cur_size = self.knn_index.get_current_count() if self.use_screen_explore else len(self.seen_coords)
        return (self.prev_knn_rew + cur_size) * self.explore_weight * 0.005  # 0.003
    
    def get_visited_pokecenter_reward(self):
        # reward for first time healed in pokecenter
        last_pokecenter_id = self.get_last_pokecenter_id()
        if last_pokecenter_id != -1 and last_pokecenter_id not in self.visited_pokecenter_list:
            self.visited_pokecenter_list.append(last_pokecenter_id)
        return len(self.visited_pokecenter_list) * 2
    
    def get_badges(self):
        return self.bit_count(self.read_m(0xD356))

    def read_party(self, one_indexed=0):
        parties = [self.read_m(addr) for addr in [0xD164, 0xD165, 0xD166, 0xD167, 0xD168, 0xD169]]
        return [p + one_indexed if p != 0xff and p != 0 else 0 for p in parties]
    
    def get_last_pokecenter_list(self):
        pc_list = [0, ] * len(self.pokecenter_ids)
        last_pokecenter_id = self.get_last_pokecenter_id()
        if last_pokecenter_id != -1:
            pc_list[last_pokecenter_id] = 1
        return pc_list
    
    def get_last_pokecenter_id(self):
        
        last_pokecenter = self.read_m(0xD719)
        # will throw error if last_pokecenter not in pokecenter_ids, intended
        if last_pokecenter == 0:
            # no pokecenter visited yet
            return -1
        return self.pokecenter_ids.index(last_pokecenter)
    
    def get_hm_rewards(self):
        hm_ids = [0xC4, 0xC5, 0xC6, 0xC7, 0xC8]
        items = self.get_items_in_bag()
        total_hm_cnt = 0
        for hm_id in hm_ids:
            if hm_id in items:
                total_hm_cnt += 1
        return total_hm_cnt * 1

    def update_heal_reward(self):
        cur_health = self.read_hp_fraction()
        if cur_health > self.last_health:
            # fixed catching pokemon might treated as healing
            # fixed leveling count as healing, min heal amount is 4%
            heal_amount = cur_health - self.last_health
            if self.last_num_poke == self.read_num_poke() and self.last_health > 0 and heal_amount > 0.04:
                if heal_amount > 0.5:
                    print(f'healed: {heal_amount}')
                    # self.save_screenshot('healing')
                self.total_healing_rew += heal_amount * 4
            elif self.last_health <= 0:
                    self.died_count += 1

    def update_num_poke(self):
        self.last_num_poke = self.read_num_poke()
                
    def get_all_events_reward(self):
        # adds up all event flags, exclude museum ticket
        museum_ticket = (0xD754, 0)
        base_event_flags = 13
        return max(
            self.all_events_string.count('1')
            - base_event_flags
            - int(self.read_bit(museum_ticket[0], museum_ticket[1])),
        0,
    )

    def get_game_state_reward(self, print_stats=False):
        # addresses from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map
        # https://github.com/pret/pokered/blob/91dc3c9f9c8fd529bb6e8307b58b96efa0bec67e/constants/event_constants.asm
        '''
        num_poke = self.read_m(0xD163)
        poke_xps = [self.read_triple(a) for a in [0xD179, 0xD1A5, 0xD1D1, 0xD1FD, 0xD229, 0xD255]]
        #money = self.read_money() - 975 # subtract starting money
        seen_poke_count = sum([self.bit_count(self.read_m(i)) for i in range(0xD30A, 0xD31D)])
        all_events_score = sum([self.bit_count(self.read_m(i)) for i in range(0xD747, 0xD886)])
        oak_parcel = self.read_bit(0xD74E, 1) 
        oak_pokedex = self.read_bit(0xD74B, 5)
        opponent_level = self.read_m(0xCFF3)
        self.max_opponent_level = max(self.max_opponent_level, opponent_level)
        enemy_poke_count = self.read_m(0xD89C)
        self.max_opponent_poke = max(self.max_opponent_poke, enemy_poke_count)
        
        if print_stats:
            print(f'num_poke : {num_poke}')
            print(f'poke_levels : {poke_levels}')
            print(f'poke_xps : {poke_xps}')
            #print(f'money: {money}')
            print(f'seen_poke_count : {seen_poke_count}')
            print(f'oak_parcel: {oak_parcel} oak_pokedex: {oak_pokedex} all_events_score: {all_events_score}')
        '''
        last_event_rew = self.max_event_rew
        self.max_event_rew = self.update_max_event_rew()
        state_scores = {
            'event': self.max_event_rew,  
            #'party_xp': self.reward_scale*0.1*sum(poke_xps),
            'level': self.get_levels_reward(), 
            # 'heal': self.total_healing_rew,
            'op_lvl': self.update_max_op_level(),
            'dead': -0.1*self.died_count,
            'badge': self.get_badges() * 5,  # 5
            #'op_poke':self.max_opponent_poke * 800,
            #'money': money * 3,
            #'seen_poke': self.reward_scale * seen_poke_count * 400,
            'explore': self.get_knn_reward(last_event_rew),
            'visited_pokecenter': self.get_visited_pokecenter_reward(),
            'hm': self.get_hm_rewards(),
            'hm_move': self.get_hm_move_reward(),
            # 'early_done': self.get_early_done_reward(),  # removed
        }
        # multiply by reward scale
        state_scores = {k: v * self.reward_scale for k, v in state_scores.items()}
        
        return state_scores
    
    def get_hm_move_reward(self):
        all_moves = self.get_party_moves()
        hm_moves = [0x0f, 0x13, 0x39, 0x46, 0x94]
        hm_move_count = 0
        for hm_move in hm_moves:
            if hm_move in all_moves:
                hm_move_count += 1
        return hm_move_count * 1.5
    
    def save_screenshot(self, name):
        ss_dir = self.s_path / Path('screenshots')
        ss_dir.mkdir(exist_ok=True)
        plt.imsave(
            ss_dir / Path(f'frame{self.instance_id}_r{self.total_reward:.4f}_{self.reset_count}_{name}.jpeg'), 
            self.render(reduce_res=False))
    
    def update_max_op_level(self):
        #opponent_level = self.read_m(0xCFE8) - 5 # base level
        opponent_level = max([self.read_m(a) for a in [0xD8C5, 0xD8F1, 0xD91D, 0xD949, 0xD975, 0xD9A1]]) - 5
        #if opponent_level >= 7:
        #    self.save_screenshot('highlevelop')
        self.max_opponent_level = max(self.max_opponent_level, opponent_level)
        return self.max_opponent_level * 0.1  # 0.1
    
    @property
    def all_events_string(self):
        # cache all events string to improve performance
        if not self._all_events_string:
            event_flags_start = 0xD747
            event_flags_end = 0xD886
            result = ''
            for i in range(event_flags_start, event_flags_end):
                result += bin(self.read_m(i))[2:]  # .zfill(8)
            self._all_events_string = result
        return self._all_events_string
    
    @property
    def battle_type(self):
        if not self._battle_type:
            result = self.read_m(0xD057)
            if result == -1:
                return 0
            return result
        return self._battle_type
    
    def is_wild_battle(self):
        return self.battle_type == 1
    
    def update_max_event_rew(self):
        cur_rew = self.get_all_events_reward()
        self.max_event_rew = max(cur_rew, self.max_event_rew)
        return self.max_event_rew
    
    def is_in_battle(self):
        # D057
        # 0 not in battle
        # 1 wild battle
        # 2 trainer battle
        # -1 lost battle
        return self.battle_type > 0
    
    def get_items_in_bag(self, one_indexed=0):
        first_item = 0xD31E
        # total 20 items
        # item1, quantity1, item2, quantity2, ...
        item_ids = []
        for i in range(0, 20, 2):
            item_id = self.read_m(first_item + i)
            if item_id == 0 or item_id == 0xff:
                break
            item_ids.append(item_id + one_indexed)
        return item_ids
    
    def get_items_quantity_in_bag(self):
        first_quantity = 0xD31F
        # total 20 items
        # quantity1, item2, quantity2, ...
        item_quantities = []
        for i in range(1, 20, 2):
            item_quantity = self.read_m(first_quantity + i)
            if item_quantity == 0 or item_quantity == 0xff:
                break
            item_quantities.append(item_quantity)
        return item_quantities
    
    def get_party_moves(self):
        # first pokemon moves at D173
        # 4 moves per pokemon
        # next pokemon moves is 44 bytes away
        first_move = 0xD173
        moves = []
        for i in range(0, 44*6, 44):
            # 4 moves per pokemon
            move = [self.read_m(first_move + i + j) for j in range(4)]
            moves.extend(move)
        return moves

    def read_hp_fraction(self):
        hp_sum = sum([self.read_hp(add) for add in [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248]])
        max_hp_sum = sum([self.read_hp(add) for add in [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269]])
        return hp_sum / max_hp_sum

    def read_hp(self, start):
        return 256 * self.read_m(start) + self.read_m(start+1)

    # built-in since python 3.10
    def bit_count(self, bits):
        return bin(bits).count('1')

    def read_triple(self, start_add):
        return 256*256*self.read_m(start_add) + 256*self.read_m(start_add+1) + self.read_m(start_add+2)
    
    def read_bcd(self, num):
        return 10 * ((num >> 4) & 0x0f) + (num & 0x0f)
    
    def read_double(self, start_add):
        return 256*self.read_m(start_add) + self.read_m(start_add+1)
    
    def read_money(self):
        return (100 * 100 * self.read_bcd(self.read_m(0xD347)) + 
                100 * self.read_bcd(self.read_m(0xD348)) +
                self.read_bcd(self.read_m(0xD349)))

    def read_num_poke(self):
        return self.read_m(0xD163)
    
    def multi_hot_encoding(self, cnt, max_n):
        return [1 if cnt < i else 0 for i in range(max_n)]
    
    def one_hot_encoding(self, cnt, max_n, start_zero=False):
        if start_zero:
            return [1 if cnt == i else 0 for i in range(max_n)]
        else:
            return [1 if cnt == i+1 else 0 for i in range(max_n)]
    
    def scaled_encoding(self, cnt, max_n: float):
        max_n = float(max_n)
        if isinstance(cnt, list):
            return [min(1.0, c / max_n) for c in cnt]
        elif isinstance(cnt, np.ndarray):
            return np.clip(cnt / max_n, 0, 1)
        else:
            return min(1.0, cnt / max_n)
    
    def get_badges_obs(self):
        return self.multi_hot_encoding(self.get_badges(), 12)

    def get_money_obs(self):
        return [self.scaled_encoding(self.read_money(), 100_000)]
    
    def read_swap_mon_pos(self):
        is_in_swap_mon_party_menu = self.read_m(0xd07d) == 0x04
        if is_in_swap_mon_party_menu:
            chosen_mon = self.read_m(0xcc35)
            if chosen_mon == 0:
                print(f'\nsomething went wrong, chosen_mon is 0')
            else:
                return chosen_mon - 1
        return -1
    
    # def get_swap_pokemon_obs(self):
    #     is_in_swap_mon_party_menu = self.read_m(0xd07d) == 0x04
    #     if is_in_swap_mon_party_menu:
    #         chosen_mon = self.read_m(0xcc35)
    #         if chosen_mon == 0:
    #             print(f'\nsomething went wrong, chosen_mon is 0')
    #         else:
    #             # print(f'chose mon {chosen_mon}')
    #             return self.one_hot_encoding(chosen_mon - 1, 6, start_zero=True)
    #     return [0] * 6
    
    def get_last_pokecenter_obs(self):
        return self.get_last_pokecenter_list()

    def get_visited_pokecenter_obs(self):
        result = [0] * len(self.pokecenter_ids)
        for i in self.visited_pokecenter_list:
            result[i] = 1
        return result
    
    def get_hm_move_obs(self):
        hm_moves = [0x0f, 0x13, 0x39, 0x46, 0x94]
        result = [0] * len(hm_moves)
        all_moves = self.get_party_moves()
        for i, hm_move in enumerate(hm_moves):
            if hm_move in all_moves:
                result[i] = 1
                continue
        return result
    
    def get_hm_obs(self):
        hm_ids = [0xC4, 0xC5, 0xC6, 0xC7, 0xC8]
        items = self.get_items_in_bag()
        result = [0] * len(hm_ids)
        for i, hm_id in enumerate(hm_ids):
            if hm_id in items:
                result[i] = 1
                continue
        return result
    
    def get_items_obs(self):
        # items from self.get_items_in_bag()
        # add 0s to make it 20 items
        items = self.get_items_in_bag(one_indexed=1)
        items.extend([0] * (20 - len(items)))
        return items

    def get_items_quantity_obs(self):
        # items from self.get_items_quantity_in_bag()
        # add 0s to make it 20 items
        items = self.get_items_quantity_in_bag()
        items = self.scaled_encoding(items, 20)
        items.extend([0] * (20 - len(items)))
        return np.array(items, dtype=np.float32).reshape(-1, 1)

    def get_bag_full_obs(self):
        # D31D
        return [1 if self.read_m(0xD31D) >= 20 else 0]
    
    def get_last_10_map_ids_obs(self):
        return self.last_10_map_ids
    
    def get_last_10_coords_obs(self):
        # 10, 2
        # scale x with 45, y with 72
        result = []
        for coord in self.last_10_coords:
            result.append(min(coord[0] / 45, 1))
            result.append(min(coord[1] / 72, 1))
        return result
    
    def get_pokemon_ids_obs(self):
        return self.read_party(one_indexed=1)

    # def get_opp_pokemon_ids_obs(self):
    #     opp_pkmns = [self.read_m(addr) for addr in [0xD89D, 0xD89E, 0xD89F, 0xD8A0, 0xD8A1, 0xD8A2]]
    #     return [p + 1 if p != 0xff and p != 0 else 0 for p in opp_pkmns]
    
    def get_battle_pokemon_ids_obs(self):
        battle_pkmns = [self.read_m(addr) for addr in [0xcfe5, 0xd014]]
        return [p + 1 if p != 0xff and p != 0 else 0 for p in battle_pkmns]
    
    def get_party_types_obs(self):
        # 6 pokemon, 2 types each
        # start from D170 type1, D171 type2
        # next pokemon will be + 44
        # 0xff is no pokemon
        result = []
        for i in range(0, 44*6, 44):
            # 2 types per pokemon
            type1 = self.read_m(0xD170 + i)
            type2 = self.read_m(0xD171 + i)
            result.append(type1)
            result.append(type2)
        return [p + 1 if p != 0xff and p != 0 else 0 for p in result]
    
    def get_opp_types_obs(self):
        # 6 pokemon, 2 types each
        # start from D8A9 type1, D8AA type2
        # next pokemon will be + 44
        # 0xff is no pokemon
        result = []
        for i in range(0, 44*6, 44):
            # 2 types per pokemon
            type1 = self.read_m(0xD8A9 + i)
            type2 = self.read_m(0xD8AA + i)
            result.append(type1)
            result.append(type2)
        return [p + 1 if p != 0xff and p != 0 else 0 for p in result]
    
    def get_battle_types_obs(self):
        # CFEA type1, CFEB type2
        # d019 type1, d01a type2
        result = [self.read_m(0xcfea), self.read_m(0xCFEB), self.read_m(0xD019), self.read_m(0xD01A)]
        return [p + 1 if p != 0xff and p != 0 else 0 for p in result]
    
    def get_party_move_ids_obs(self):
        # D173 move1, D174 move2...
        # next pokemon will be + 44
        result = []
        for i in range(0, 44*6, 44):
            # 4 moves per pokemon
            moves = [self.read_m(addr + i) for addr in [0xD173, 0xD174, 0xD175, 0xD176]]
            result.extend(moves)
        return [p + 1 if p != 0xff and p != 0 else 0 for p in result]
    
    def get_opp_move_ids_obs(self):
        # D8AC move1, D8AD move2...
        # next pokemon will be + 44
        result = []
        for i in range(0, 44*6, 44):
            # 4 moves per pokemon
            moves = [self.read_m(addr + i) for addr in [0xD8AC, 0xD8AD, 0xD8AE, 0xD8AF]]
            result.extend(moves)
        return [p + 1 if p != 0xff and p != 0 else 0 for p in result]
    
    def get_battle_move_ids_obs(self):
        # CFED move1, CFEE move2
        # second pokemon starts from D003
        result = []
        for addr in [0xCFED, 0xD003]:
            moves = [self.read_m(addr + i) for i in range(4)]
            result.extend(moves)
        return [p + 1 if p != 0xff and p != 0 else 0 for p in result]
    
    def get_party_move_pps_obs(self):
        # D188 pp1, D189 pp2...
        # next pokemon will be + 44
        result = []
        for i in range(0, 44*6, 44):
            # 4 moves per pokemon
            pps = [self.read_m(addr + i) for addr in [0xD188, 0xD189, 0xD18A, 0xD18B]]
            result.extend(pps)
        return result
    
    def get_opp_move_pps_obs(self):
        # D8C1 pp1, D8C2 pp2...
        # next pokemon will be + 44
        result = []
        for i in range(0, 44*6, 44):
            # 4 moves per pokemon
            pps = [self.read_m(addr + i) for addr in [0xD8C1, 0xD8C2, 0xD8C3, 0xD8C4]]
            result.extend(pps)
        return result
    
    def get_battle_move_pps_obs(self):
        # CFFE pp1, CFFF pp2
        # second pokemon starts from D02D
        result = []
        for addr in [0xCFFE, 0xD02D]:
            pps = [self.read_m(addr + i) for i in range(4)]
            result.extend(pps)
        return result
    
    # def get_all_move_pps_obs(self):
    #     result = []
    #     result.extend(self.get_party_move_pps_obs())
    #     result.extend(self.get_opp_move_pps_obs())
    #     result.extend(self.get_battle_move_pps_obs())
    #     result = np.array(result, dtype=np.float32) / 30
    #     # every elemenet max is 1
    #     result = np.clip(result, 0, 1)
    #     return result
    
    def get_party_level_obs(self):
        # D18C level
        # next pokemon will be + 44
        result = []
        for i in range(0, 44*6, 44):
            level = self.read_m(0xD18C + i)
            result.append(level)
        return result
    
    def get_opp_level_obs(self):
        # D8C5 level
        # next pokemon will be + 44
        result = []
        for i in range(0, 44*6, 44):
            level = self.read_m(0xD8C5 + i)
            result.append(level)
        return result
    
    def get_battle_level_obs(self):
        # CFF3 level
        # second pokemon starts from D037
        result = []
        for addr in [0xCFF3, 0xD022]:
            level = self.read_m(addr)
            result.append(level)
        return result
    
    def get_all_level_obs(self):
        result = []
        result.extend(self.get_party_level_obs())
        result.extend(self.get_opp_level_obs())
        result.extend(self.get_battle_level_obs())
        result = np.array(result, dtype=np.float32) / 100
        # every elemenet max is 1
        result = np.clip(result, 0, 1)
        return result
    
    def get_party_hp_obs(self):
        # D16C hp
        # next pokemon will be + 44
        result = []
        for i in range(0, 44*6, 44):
            hp = self.read_hp(0xD16C + i)
            max_hp = self.read_hp(0xD18D + i)
            result.extend([hp, max_hp])
        return result

    def get_opp_hp_obs(self):
        # D8A5 hp
        # next pokemon will be + 44
        result = []
        for i in range(0, 44*6, 44):
            hp = self.read_hp(0xD8A5 + i)
            max_hp = self.read_hp(0xD8C6 + i)
            result.extend([hp, max_hp])
        return result
    
    def get_battle_hp_obs(self):
        # CFE6 hp
        # second pokemon starts from CFFC
        result = []
        for addr in [0xCFE6, 0xCFF4, 0xCFFC, 0xD00A]:
            hp = self.read_hp(addr)
            result.append(hp)
        return result
    
    def get_all_hp_obs(self):
        result = []
        result.extend(self.get_party_hp_obs())
        result.extend(self.get_opp_hp_obs())
        result.extend(self.get_battle_hp_obs())
        result = np.array(result, dtype=np.float32)
        # every elemenet max is 1
        result = np.clip(result, 0, 600) / 600
        return result
    
    def get_all_hp_pct_obs(self):
        hps = []
        hps.extend(self.get_party_hp_obs())
        hps.extend(self.get_opp_hp_obs())
        hps.extend(self.get_battle_hp_obs())
        # divide every hp by max hp
        hps = np.array(hps, dtype=np.float32)
        hps = hps.reshape(-1, 2)
        hps = hps[:, 0] / (hps[:, 1] + 0.00001)
        # every elemenet max is 1
        return hps
    
    def get_all_pokemon_dead_obs(self):
        # 1 if dead, 0 if alive
        hp_pct = self.get_all_hp_pct_obs()
        return [1 if hp <= 0 else 0 for hp in hp_pct]
    
    def get_battle_status_obs(self):
        # D057
        # 0 not in battle return 0, 0
        # 1 wild battle return 1, 0
        # 2 trainer battle return 0, 1
        # -1 lost battle return 0, 0
        result = []
        status = self.battle_type
        if status == 1:
            result = [1, 0]
        elif status == 2:
            result = [0, 1]
        else:
            result = [0, 0]
        return result
    
    def fix_pokemon_type(self, ptype: int) -> int:
        if ptype < 9:
            return ptype
        elif ptype < 27:
            return ptype - 11
        else:
            print(f'invalid pokemon type: {ptype}')
            return 16
        
    def get_pokemon_types(self, start_addr):
        return [self.fix_pokemon_type(self.read_m(start_addr + i)) + 1 for i in range(2)]
        
    def get_all_pokemon_types_obs(self):
        # 6 party pokemon types start from D170
        # 6 enemy pokemon types start from D8A9
        party_type_addr = 0xD170
        enemy_type_addr = 0xD8A9
        result = []
        pokemon_count = self.read_num_poke()
        for i in range(pokemon_count):
            # 2 types per pokemon
            ptypes = self.get_pokemon_types(party_type_addr + i * 44)
            result.append(ptypes)
        remaining_pokemon = 6 - pokemon_count
        for i in range(remaining_pokemon):
            result.append([0, 0])
        if self.is_in_battle():
            # zero padding if not in battle, reduce dimension
            if not self.is_wild_battle():
                pokemon_count = self.read_opp_pokemon_num()
                for i in range(pokemon_count):
                    # 2 types per pokemon
                    ptypes = self.get_pokemon_types(enemy_type_addr + i * 44)
                    result.append(ptypes)
                remaining_pokemon = 6 - pokemon_count
                for i in range(remaining_pokemon):
                    result.append([0, 0])
            else:
                wild_ptypes = self.get_pokemon_types(0xCFEA)  # 2 ptypes only, add padding for remaining 5
                result.append(wild_ptypes)
                result.extend([[0, 0]] * 5)
        else:
            result.extend([[0, 0]] * 6)
        result = np.array(result, dtype=np.uint8)  # shape (24,)
        assert result.shape == (12, 2), f'invalid ptypes shape: {result.shape}'  # set PYTHONOPTIMIZE=1 to disable assert
        return result
    
    def get_pokemon_status(self, addr):
        # status
        # bit 0 - 6
        # one byte has 8 bits, bit unused: 7
        statuses = [self.read_bit(addr, i) for i in range(7)]
        return statuses  # shape (7,)
    
    def get_one_pokemon_obs(self, start_addr, team, position, is_wild=False):
        # team 0 = my team, 1 = opp team
        # 1 pokemon, address start from start_addr
        # +0 = id
        # +5 = type1 (15 types) (physical 0 to 8 and special 20 to 26)  + 1 to be 1 indexed, 0 is no pokemon/padding
        # +6 = type2 (15 types)
        # +33 = level
        # +4 = status (bit 0-6)
        # +1 = current hp (2 bytes)
        # +34 = max hp (2 bytes)
        # +36 = attack (2 bytes)
        # +38 = defense (2 bytes)
        # +40 = speed (2 bytes)
        # +42 = special (2 bytes)
        # exclude id, type1, type2
        result = []
        # status
        status = self.get_pokemon_status(start_addr + 4)
        result.extend(status)
        # level
        level = self.scaled_encoding(self.read_m(start_addr + 33), 100)
        result.append(level)
        # hp
        hp = self.scaled_encoding(self.read_double(start_addr + 1), 250)
        result.append(hp)
        # max hp
        max_hp = self.scaled_encoding(self.read_double(start_addr + 34), 250)
        result.append(max_hp)
        # attack
        attack = self.scaled_encoding(self.read_double(start_addr + 36), 134)
        result.append(attack)
        # defense
        defense = self.scaled_encoding(self.read_double(start_addr + 38), 180)
        result.append(defense)
        # speed
        speed = self.scaled_encoding(self.read_double(start_addr + 40), 140)
        result.append(speed)
        # special
        special = self.scaled_encoding(self.read_double(start_addr + 42), 154)
        result.append(special)
        # is alive
        is_alive = 1 if hp > 0 else 0
        result.append(is_alive)
        # is in battle, check position 0 indexed against the following addr
        if is_wild:
            in_battle = 1
        else:
            if self.is_in_battle():
                if team == 0:
                    in_battle = 1 if position == self.read_m(0xCC35) else 0
                else:
                    in_battle = 1 if position == self.read_m(0xCFE8) else 0
            else:
                in_battle = 0
        result.append(in_battle)
        # my team 0 / opp team 1
        result.append(team)
        # position 0 to 5, one hot, 5 elements, first pokemon is all 0
        result.extend(self.one_hot_encoding(position, 5))
        # is swapping this pokemon
        if team == 0:
            swap_mon_pos = self.read_swap_mon_pos()
            if swap_mon_pos != -1:
                is_swapping = 1 if position == swap_mon_pos else 0
            else:
                is_swapping = 0
        else:
            is_swapping = 0
        result.append(is_swapping)
        return result

    def get_party_pokemon_obs(self):
        # 6 party pokemons start from D16B
        # 2d array, 6 pokemons, N features
        result = np.zeros((6, self.n_pokemon_features), dtype=np.float32)
        pokemon_count = self.read_num_poke()
        for i in range(pokemon_count):
            result[i] = self.get_one_pokemon_obs(0xD16B + i * 44, 0, i)
        for i in range(pokemon_count, 6):
            result[i] = np.zeros(self.n_pokemon_features, dtype=np.float32)
        return result

    def read_opp_pokemon_num(self):
        return self.read_m(0xD89C)
    
    def get_battle_base_pokemon_obs(self, start_addr, team):
        # CFE5
        result = []
        # status
        status = self.get_pokemon_status(start_addr + 4)
        result.extend(status)
        # level
        level = self.scaled_encoding(self.read_m(start_addr + 14), 100)
        result.append(level)
        # hp
        hp = self.scaled_encoding(self.read_double(start_addr + 1), 250)
        result.append(hp)
        # max hp
        max_hp = self.scaled_encoding(self.read_double(start_addr + 15), 250)
        result.append(max_hp)
        # attack
        attack = self.scaled_encoding(self.read_double(start_addr + 17), 134)
        result.append(attack)
        # defense
        defense = self.scaled_encoding(self.read_double(start_addr + 19), 180)
        result.append(defense)
        # speed
        speed = self.scaled_encoding(self.read_double(start_addr + 21), 140)
        result.append(speed)
        # special
        special = self.scaled_encoding(self.read_double(start_addr + 23), 154)
        result.append(special)
        # is alive
        is_alive = 1 if hp > 0 else 0
        result.append(is_alive)
        # is in battle, check position 0 indexed against the following addr
        in_battle = 1
        result.append(in_battle)
        # my team 0 / opp team 1
        result.append(team)
        # position 0 to 5, one hot, 5 elements, first pokemon is all 0
        result.extend(self.one_hot_encoding(0, 5))
        return result
    
    def get_wild_pokemon_obs(self):
        start_addr = 0xCFE5
        return self.get_battle_base_pokemon_obs(start_addr, team=1)

    def get_opp_pokemon_obs(self):
        # 6 enemy pokemons start from D8A4
        # 2d array, 6 pokemons, N features
        result = []
        if self.is_in_battle():
            if not self.is_wild_battle():
                pokemon_count = self.read_opp_pokemon_num()
                for i in range(pokemon_count):
                    result.append(self.get_one_pokemon_obs(0xD8A4 + i * 44, 1, i))
                remaining_pokemon = 6 - pokemon_count
                for i in range(remaining_pokemon):
                    result.append([0] * self.n_pokemon_features)
            else:
                # wild battle, take the battle pokemon
                result.append(self.get_wild_pokemon_obs())
                for i in range(5):
                    result.append([0] * self.n_pokemon_features)
        else:
            return np.zeros((6, self.n_pokemon_features), dtype=np.float32)
        result = np.array(result, dtype=np.float32)
    
    def get_all_pokemon_obs(self):
        # 6 party pokemons start from D16B
        # 6 enemy pokemons start from D8A4
        # gap between each pokemon is 44
        party = self.get_party_pokemon_obs()
        opp = self.get_opp_pokemon_obs()
        # print(f'party shape: {party.shape}, opp shape: {opp.shape}')
        result = np.concatenate([party, opp], axis=0)
        return result  # shape (12, 22)
    
    def get_party_pokemon_ids_obs(self):
        # 6 party pokemons start from D16B
        # 1d array, 6 pokemons, 1 id
        result = []
        pokemon_count = self.read_num_poke()
        for i in range(pokemon_count):
            result.append(self.read_m(0xD16B + i * 44) + 1)
        remaining_pokemon = 6 - pokemon_count
        for i in range(remaining_pokemon):
            result.append(0)
        result = np.array(result, dtype=np.uint8)
        return result
    
    def get_opp_pokemon_ids_obs(self):
        # 6 enemy pokemons start from D8A4
        # 1d array, 6 pokemons, 1 id
        result = []
        if self.is_in_battle():
            if not self.is_wild_battle():
                pokemon_count = self.read_opp_pokemon_num()
                for i in range(pokemon_count):
                    result.append(self.read_m(0xD8A4 + i * 44) + 1)
                remaining_pokemon = 6 - pokemon_count
                for i in range(remaining_pokemon):
                    result.append(0)
            else:
                # wild battle, take the battle pokemon
                result.append(self.read_m(0xCFE5) + 1)
                for i in range(5):
                    result.append(0)
        else:
            return np.zeros(6, dtype=np.uint8)
        result = np.array(result, dtype=np.uint8)
        return result
    
    def get_all_pokemon_ids_obs(self):
        # 6 party pokemons start from D16B
        # 6 enemy pokemons start from D8A4
        # gap between each pokemon is 44
        party = self.get_party_pokemon_ids_obs()
        opp = self.get_opp_pokemon_ids_obs()
        result = np.concatenate((party, opp), axis=0)
        return result
    
    def get_one_pokemon_move_ids_obs(self, start_addr):
        # 4 moves
        return [self.read_m(start_addr + i) for i in range(4)]
    
    def get_party_pokemon_move_ids_obs(self):
        # 6 party pokemons start from D173
        # 2d array, 6 pokemons, 4 moves
        result = []
        pokemon_count = self.read_num_poke()
        for i in range(pokemon_count):
            result.append(self.get_one_pokemon_move_ids_obs(0xD173 + (i * 44)))
        remaining_pokemon = 6 - pokemon_count
        for i in range(remaining_pokemon):
            result.append([0] * 4)
        result = np.array(result, dtype=np.uint8)
        return result

    def get_opp_pokemon_move_ids_obs(self):
        # 6 enemy pokemons start from D8AC
        # 2d array, 6 pokemons, 4 moves
        result = []
        if self.is_in_battle():
            if not self.is_wild_battle():
                pokemon_count = self.read_opp_pokemon_num()
                for i in range(pokemon_count):
                    result.append(self.get_one_pokemon_move_ids_obs(0xD8AC + (i * 44)))
                remaining_pokemon = 6 - pokemon_count
                for i in range(remaining_pokemon):
                    result.append([0] * 4)
            else:
                # wild battle, take the battle pokemon
                result.append(self.get_one_pokemon_move_ids_obs(0xCFED))
                for i in range(5):
                    result.append([0] * 4)
        else:
            return np.zeros((6, 4), dtype=np.uint8)
        result = np.array(result, dtype=np.uint8)
        return result
    
    def get_all_move_ids_obs(self):
        # 6 party pokemons start from D173
        # 6 enemy pokemons start from D8AC
        # gap between each pokemon is 44
        party = self.get_party_pokemon_move_ids_obs()
        opp = self.get_opp_pokemon_move_ids_obs()
        result = np.concatenate((party, opp), axis=0)
        return result  # shape (12, 4)
    
    def get_one_pokemon_move_pps_obs(self, start_addr):
        # 4 moves
        result = np.zeros((4, 2), dtype=np.float32)
        for i in range(4):
            pp = self.scaled_encoding(self.read_m(start_addr + i), 30)
            have_pp = 1 if pp > 0 else 0
            result[i] = [pp, have_pp]
        return result
    
    def get_party_pokemon_move_pps_obs(self):
        # 6 party pokemons start from D188
        # 2d array, 6 pokemons, 8 features
        # features: pp, have pp
        result = np.zeros((6, 4, 2), dtype=np.float32)
        pokemon_count = self.read_num_poke()
        for i in range(pokemon_count):
            result[i] = self.get_one_pokemon_move_pps_obs(0xD188 + (i * 44))
        for i in range(pokemon_count, 6):
            result[i] = np.zeros((4, 2), dtype=np.float32)
        return result
    
    def get_opp_pokemon_move_pps_obs(self):
        # 6 enemy pokemons start from D8C1
        # 2d array, 6 pokemons, 8 features
        # features: pp, have pp
        result = np.zeros((6, 4, 2), dtype=np.float32)
        if self.is_in_battle():
            if not self.is_wild_battle():
                pokemon_count = self.read_opp_pokemon_num()
                for i in range(pokemon_count):
                    result[i] = self.get_one_pokemon_move_pps_obs(0xD8C1 + (i * 44))
                for i in range(pokemon_count, 6):
                    result[i] = np.zeros((4, 2), dtype=np.float32)
            else:
                # wild battle, take the battle pokemon
                result.append(self.get_one_pokemon_move_pps_obs(0xCFFE))
                for i in range(5):
                    result.append(np.zeros((4, 2), dtype=np.float32))
        else:
            return np.zeros((6, 4, 2), dtype=np.float32)
        return result
    
    def get_all_move_pps_obs(self):
        # 6 party pokemons start from D188
        # 6 enemy pokemons start from D8C1
        party = self.get_party_pokemon_move_pps_obs()
        opp = self.get_opp_pokemon_move_pps_obs()
        result = np.concatenate((party, opp), axis=0)
        return result
    
    def get_all_item_ids_obs(self):
        # max 85
        return np.array(self.get_items_obs(), dtype=np.uint8)
    
    def get_all_event_ids_obs(self):
        # max 249
        # padding_idx = 0
        # change dtype to uint8 to save space
        return np.array(self.last_10_event_ids[:, 0] + 1, dtype=np.uint8)
    
    def get_all_event_step_since_obs(self):
        step_gotten = self.last_10_event_ids[:, 1]  # shape (10,)
        step_since = self.step_count - step_gotten
        # step_count - step_since and scaled_encoding
        return self.scaled_encoding(step_since, 1000).reshape(-1, 1)  # shape (10,)
    
    def get_last_coords_obs(self):
        # 2 elements
        coord = self.last_10_coords[0]
        return [self.scaled_encoding(coord[0], 45), self.scaled_encoding(coord[1], 72)]
    
    def get_num_turn_in_battle_obs(self):
        if self.is_in_battle:
            return self.scaled_encoding(self.read_m(0xCCD5), 30)
        else:
            return 0
    
    def get_all_raw_obs(self):
        obs = []
        obs.extend(self.get_badges_obs())
        obs.extend(self.get_money_obs())
        obs.extend(self.get_last_pokecenter_obs())
        obs.extend(self.get_visited_pokecenter_obs())
        obs.extend(self.get_hm_move_obs())
        obs.extend(self.get_hm_obs())
        obs.extend(self.get_battle_status_obs())
        pokemon_count = self.read_num_poke()
        obs.extend([self.scaled_encoding(pokemon_count, 6)])  # number of pokemon
        obs.extend([1 if pokemon_count == 6 else 0])  # party full
        obs.extend([self.scaled_encoding(self.read_m(0xD31D), 20)])  # bag num items
        obs.extend(self.get_bag_full_obs())  # bag full
        obs.extend(self.get_last_coords_obs())  # last coords x, y
        obs.extend([self.get_num_turn_in_battle_obs()])  # num turn in battle
        # obs.extend(self.get_reward_check_obs())  # reward check
        return np.array(obs, dtype=np.float32)

    def get_last_map_id_obs(self):
        return np.array([self.last_10_map_ids[0]], dtype=np.uint8)
    
    def get_in_battle_mask_obs(self):
        return np.array([self.is_in_battle()], dtype=np.float32)