import csv
from pdb import set_trace as T
import uuid
from gymnasium import Env, spaces
import numpy as np
from collections import defaultdict
import io, os
import random
from pathlib import Path
import mediapy as media


from pokegym.pyboy_binding import (ACTIONS, make_env, open_state_file,
    load_pyboy_state, run_action_on_emulator)
from pokegym import ram_map, game_map, data

STATE_PATH = __file__.rstrip("environment.py") + "States/"
def get_random_state():
    state_files = [f for f in os.listdir(STATE_PATH) if f.endswith(".state")]
    if not state_files:
        raise FileNotFoundError("No State files found in the specified directory.")
    return random.choice(state_files)

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
            state_path = STATE_PATH + "Bulbasaur.state" # STATE_PATH + "has_pokedex_nballs.state" or self.randstate 
        with open("experiments/current_exp.txt", "r") as file:
            exp_name = file.read()
        
        self.game, self.screen = make_env(rom_path, headless, quiet, save_video=True, **kwargs)
        R, C = self.screen.raw_screen_buffer_dims()
        self.state_file = get_random_state()
        self.randstate = os.path.join(STATE_PATH, self.state_file)
        self.initial_states = [open_state_file(state_path)]
        self.save_video = save_video
        self.headless = headless
        self.mem_padding = 2
        self.memory_shape = 80
        self.use_screen_memory = True
        self.exp_path = Path(f'experiments/{str(exp_name)}')
        self.env_id = Path(f'session_{str(uuid.uuid4())[:4]}')
        self.s_path = Path(f'{str(self.exp_path)}/sessions/{str(self.env_id)}')
        self.reset_count = 0
        self.obs_size = (R // 2, C // 2)

        if self.use_screen_memory:
            self.screen_memory = defaultdict(lambda: np.zeros((255, 255, 1), dtype=np.uint8))
            self.obs_size += (4,)
        else:
            self.obs_size += (3,)
        self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8, shape=self.obs_size)
        self.action_space = spaces.Discrete(len(ACTIONS))

    def save_state(self):
        state = io.BytesIO()
        state.seek(0)
        self.game.save_state(state)
        self.initial_states.append(state)

    def load_random_state(self):
        rand_idx = random.randint(0, len(self.initial_states) - 1)
        return self.initial_states[rand_idx]

    def reset(self, seed=None, options=None):
        """Resets the game. Seeding is NOT supported"""
        load_pyboy_state(self.game, self.load_random_state())
        return self.screen.screen_ndarray(), {}

    def get_fixed_window(self, arr, y, x, window_size):
        height, width, _ = arr.shape
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
            if 0 <= r < mmap.shape[0] and 0 <= c < mmap.shape[1]:
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
        
    def video(self):
        video = self.screen.screen_ndarray()
        return video

    def step(self, action):
        run_action_on_emulator(self.game, self.screen, ACTIONS[action], self.headless)
        return self.render(), 0, False, False, {}

    def close(self):
        self.game.stop(False)

class Environment(Base):
    def __init__(self, rom_path='pokemon_red.gb',
            state_path=None, headless=True, save_video=True, quiet=False, verbose=False, **kwargs):
        super().__init__(rom_path, state_path, headless, save_video, quiet, **kwargs)
        self.counts_map = np.zeros((444, 436))
        self.verbose = verbose
        self.log = True

    def add_video_frame(self):
        self.full_frame_writer.add_image(self.video())

    def write_to_log(self):
        pokemon_info = data.pokemon_l(self.game)
        x, y ,map_n = ram_map.position(self.game)
        session_path = self.s_path
        base_dir = self.exp_path
        reset = self.reset_count
        env_id = self.env_id
        base_dir.mkdir(parents=True, exist_ok=True)
        session_path.mkdir(parents=True, exist_ok=True)
        csv_file_path = base_dir / "unique_positions.csv"
        with open(session_path / self.full_name_log, 'w') as f:
            for pokemon in pokemon_info:
                f.write(f"Slot: {pokemon['slot']}\n")
                f.write(f"Name: {pokemon['name']}\n")
                f.write(f"Level: {pokemon['level']}\n")
                f.write(f"Moves: {', '.join(pokemon['moves'])}\n")
                f.write("\n")  # Add a newline between Pokémon
        with open(csv_file_path, 'a') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([env_id, reset, x, y, map_n])

    def reset(self, seed=None, options=None, max_episode_steps=20480, reward_scale=4.0):
        """Resets the game. Seeding is NOT supported"""
        load_pyboy_state(self.game, self.load_random_state())

        if self.save_video:
            env_path = self.s_path
            env_path.mkdir(parents=True, exist_ok=True)
            full_name = Path(f'reset_{self.reset_count}').with_suffix('.mp4')
            self.full_frame_writer = media.VideoWriter(env_path / full_name, (144, 160), fps=60)
            self.full_frame_writer.__enter__()

        if self.use_screen_memory:
            self.screen_memory = defaultdict(lambda: np.zeros((255, 255, 1), dtype=np.uint8))

        self.time = 0
        self.max_episode_steps = max_episode_steps
        self.reward_scale = reward_scale
        self.prev_map_n = None
        self.max_events = 0
        self.max_level_sum = 0
        self.max_opponent_level = 0
        self.seen_coords = set()
        self.seen_maps = set()
        self.healing = 0
        self.total_healing = 0
        self.last_party_size = 1
        self.last_reward = None
        self.last_hp = [1] * 6
        self.hp = [0] * 6
        self.hp_delta = [0] * 6
        self.death = 0
        self.qty = 0
        self.reset_count += 1

        return self.render(), {}

    def step(self, action, fast_video=True):
        run_action_on_emulator(self.game, self.screen, ACTIONS[action],
            self.headless, fast_video=fast_video)
        
        self.time += 1
        if self.save_video:
            self.add_video_frame()
        

        if self.log:
            self.full_name_log = Path(f'party_log').with_suffix('.txt')
            self.full_name_csv = Path(f'position_csv').with_suffix('.csv')
            self.write_to_log() 

    # Constants
        pokecenters = [41, 58, 64, 68, 81, 89, 133, 141, 154, 171, 147, 182]
        towns = set({1, 2, 3, 4, 5, 6, 7, 8, 9, 10})
        item_check = [1, 2, 3, 4, 6, 11, 16, 17, 18, 19, 20, 41, 42, 72, 73, 196, 197, 198, 199, 200, 53, 54]

    # Functions / Variables
        
        party, party_size, party_levels = ram_map.party(self.game)
        party_size_constant = party_size == self.last_party_size
        
        

    # Exploration
        # Map Reward
        r, c, map_n = ram_map.position(self.game)
        self.seen_coords.add((r, c, map_n))
        if map_n != self.prev_map_n:
            self.prev_map_n = map_n
            if map_n not in self.seen_maps and map_n in pokecenters:
                self.save_state()
        if map_n not in self.seen_maps:
            self.seen_maps.add(map_n)

        coord_reward = 0.001 * len(self.seen_coords)
        map_reward = 0.01 * len(self.seen_maps)
        exploration_reward = coord_reward + map_reward

        #Plot Map
        glob_r, glob_c = game_map.local_to_global(r, c, map_n)
        try:
            self.counts_map[glob_r, glob_c] += 1
        except:
            pass

    # Pokemon
        poke, type1, type2, level, hp, status, death = ram_map.pokemon(self.game)
        level_rewards = []

        #Levels
        for lvl in level:
            if lvl < 20:
                level_reward = .5 * lvl
            else:
                level_reward = 7.5 + (lvl - 20) / 4
            level_rewards.append(level_reward)
        lvl_rew = sum(level_rewards)
        self.max_level_sum = sum(level)

        # HP / Death    
        self.hp = hp
        assert len(self.hp) == len(self.last_hp)
        for h, i in zip(self.hp, self.last_hp):
        #     hp_delta = h - i
        #     if hp_delta > 0.25 and party_size_constant: #updated from 0 to 0.25 to .50
        #         self.total_healing += hp_delta
        #     i = h
        # self.death = sum(death)
        #     # if h <= 0 and i > 0 and dead_delta > 0:
        #     #     j = 1
        #     # elif h > 0.01:
        #     #     j = 0
        #     # if (sum(hp)) <= 0 and (sum(self.last_hp)) > 0:
            last_hp = i
            cur_health = h
            if (cur_health > last_hp and party_size_constant):
                if last_hp > 0:
                    heal_amount = cur_health - last_hp
                    if heal_amount > 0.1:
                        self.total_healing += heal_amount * 2
                else:
                    self.death += 1
        self.last_hp = self.hp
        healing_reward = self.total_healing 
        death_reward = -1.0 * self.death

    # Update Values
        self.last_party_size = party_size
        
    # Badges
        badges = ram_map.badges(self.game)
        badges_reward = 5 * badges

    # # Event reward
        events = ram_map.events(self.game)
        self.max_events = events
        event_reward = self.max_events

    # HM reward
        hm_count = ram_map.get_hm_rewards(self.game)
        hm_reward = hm_count * 10 # 5

    # Testing
        # # Items
        # items = ram_map.get_items_in_bag(self.game)
        # if items[0] in item_check:
        #     self.qty += .01 * items[1]
        # print(f'Items:{items}')
        # print(f'Debug:{items[0]}, {items[1]}')

    #TODO

        # # Opponent level reward
        # max_opponent_level = max(ram_map.opponent(self.game))
        # self.max_opponent_level = max(self.max_opponent_level, max_opponent_level)
        # opponent_level_reward = 0.2 * self.max_opponent_level


        

        # # money reward
        # money = ram_map.money(self.game)

        # sum reward
        reward = self.reward_scale * (lvl_rew + badges_reward + exploration_reward + healing_reward + event_reward + hm_reward) #  + death_reward
        reward1 = (lvl_rew + badges_reward + exploration_reward + healing_reward + event_reward + hm_reward) # + healing_reward
        if death_reward == 0:
            neg_reward = 1
        else:
            neg_reward = death_reward

        # print rewards
        if self.headless == False or self.save_video == True:
            print(f'-------------Counter-------------')
            print(f'Steps:',self.time,)
            print(f'Sum Reward:',reward)
            print(f'Coords:',len(self.seen_maps))
            print(f'HM Count:',hm_count)
            # print(f'Items:',items)
            # print(f'Items Reward::',self.qty)
            print(f'Total Level:',self.max_level_sum)
            print(f'Levels:',level)
            print(f'HP:',hp)
            print(f'Status:',status)
            print(f'Deaths:',self.death)
            print(f'Is Dead:', death)
            print(f'Total Heal:',self.total_healing)
            print(f'Party Size:',self.last_party_size)
            print(f'-------------Rewards-------------')
            print(f'Total:',reward1)
            print(f'HM Reward:',hm_reward)
            print(f'Explore:',exploration_reward,'--%',100 * (exploration_reward/reward1))
            print(f'Healing:',healing_reward,'--%',100 * (healing_reward/reward1))
            print(f'Badges:',badges_reward,'--%',100 * (badges_reward/reward1))
            print(f'Level:',lvl_rew,'--%',100 * (lvl_rew/reward1))
            print(f'Events:',event_reward,'--%',100 * (event_reward/reward1))
            print(f'-------------Negatives-------------')
            print(f'Total:',neg_reward)
            print(f'Deaths:',death_reward, '--%', 100 * (death_reward/neg_reward))
            # print(f'-------------Party-------------')
            # print(f'P1--','Lvl:',p1lvl,', Status:',p1status,', HP:',self.last_p1hp,', Deaths:',self.p1death)    
            # print(f'P2--','Lvl:',p2lvl,', Status:',p2status,', HP:',self.last_p2hp,', Deaths:',self.p2death)         
            # print(f'P3--','Lvl:',p3lvl,', Status:',p3status,', HP:',self.last_p3hp,', Deaths:',self.p3death) 
            # print(f'P4--','Lvl:',p4lvl,', Status:',p4status,', HP:',self.last_p4hp,', Deaths:',self.p4death) 
            # print(f'P5--','Lvl:',p5lvl,', Status:',p5status,', HP:',self.last_p5hp,', Deaths:',self.p5death) 
            # print(f'P6--','Lvl:',p6lvl,', Status:',p6status,', HP:',self.last_p6hp,', Deaths:',self.p6death) 
            # print(f'Coords:',self.seen_maps)
            # print(f'Dest_status:',self.dest_reward,'--%',100 * (self.dest_reward/neg_reward))
            # print(f'-------------Test-------------')
            # print(f'Last Health:',self.last_health)
            # print(f'Current Health:',cur_health)
            # print(f'Heal Amount',self.heal_amount)

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
                'reward': {
                    'delta': reward,
                    'event': event_reward,
                    'level': level_reward,
                    'hm_count': hm_count,
                    'death': death_reward,
                    'badges': badges_reward,
                    'healing': healing_reward,
                    'exploration': exploration_reward,
                },
                'maps_explored': len(self.seen_maps),
                'party_size': party_size,
                'highest_pokemon_level': max(party_levels),
                'total_party_level': sum(party_levels),
                'deaths': self.death,
                'hm': hm_reward,
                'badge_1': float(badges >= 1),
                'badge_2': float(badges > 1),
                'event': events,
                'healing': self.total_healing,
                'pokemon_exploration_map': self.counts_map,
            }

        # if self.verbose:
        #     print(
        #         f'steps: {self.time}',
        #         f'exploration reward: {exploration_reward}',
        #         f'level_Reward: {level_reward}',
        #         f'healing: {healing_reward}',
        #         f'death: {death_reward}',
        #         #f'op_level: {opponent_level_reward}',
        #         f'badges reward: {badges_reward}',
        #         f'event reward: {event_reward}',
        #         # f'money: {money}',
        #         f'ai reward: {reward}',
        #         f'Info: {info}',
        #     )

        return self.render(), reward, done, done, info
