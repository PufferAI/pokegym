from pdb import set_trace as T
from gymnasium import Env, spaces
import numpy as np
import os

from pokegym.pyboy_binding import (ACTIONS, make_env, open_state_file,
                                   load_pyboy_state, run_action_on_emulator)
from pokegym import ram_map, game_map


def play():
    '''Creates an environment and plays it'''
    env = Environment(
        rom_path='pokemon_red.gb', 
        state_path=None, 
        headless=False,
        disable_input=False, 
        sound=False, 
        sound_emulated=False, 
        verbose=True
                      )

    env.reset()
    env.game.set_emulation_speed(12)

    # Display available actions
    print("Available actions:")
    for idx, action in enumerate(ACTIONS):
        print(f"{idx}: {action}")

    # Create a mapping from WindowEvent to action index
    window_event_to_action = {
        'PRESS_ARROW_DOWN': 0,
        'PRESS_ARROW_LEFT': 1,
        'PRESS_ARROW_RIGHT': 2,
        'PRESS_ARROW_UP': 3,
        'PRESS_BUTTON_A': 4,
        'PRESS_BUTTON_B': 5,
        'PRESS_BUTTON_START': 6,
        'PRESS_BUTTON_SELECT': 7,
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
                    action_index, fast_video=False)

                # Check for game over
                if done:
                    print(f"{done}")
                    break

                # Additional game logic or information display can go here
                print(f"new Reward: {reward}\n")


class Base:
    def __init__(
        self, 
        rom_path='pokemon_red.gb',
        state_path=None, 
        headless=True, 
        quiet=False, 
        verbose=False, 
        **kwargs
        ):
        '''Creates a PokemonRed environment'''
        if state_path is None:
            # state_path = __file__.rstrip('environment.py') + 'pokemon_red.cerulean.state'
            # state_path = __file__.rstrip('environment.py') + 'pokemon_red_300m_step.state'
            state_path = __file__.rstrip('environment.py') + 'has_pokedex_nballs.state'


        self.game, self.screen = make_env(
            rom_path, headless, quiet, **kwargs)

        self.initial_state = open_state_file(state_path)
        self.headless = headless

        R, C = self.screen.raw_screen_buffer_dims()
        self.observation_space = spaces.Box(
            low=0, high=255, dtype=np.uint8,
            shape=(R // 2, C // 2, 3),
        )
        self.action_space = spaces.Discrete(len(ACTIONS))

    def reset(self, seed=None, options=None):
        '''Resets the game. Seeding is NOT supported'''
        load_pyboy_state(self.game, self.initial_state)
        return self.screen.screen_ndarray(), {}

    def render(self):
        return self.screen.screen_ndarray()

    def step(self, action):
        run_action_on_emulator(self.game, self.screen, ACTIONS[action], self.headless)
        return self.render(), 0, False, False, {}

    def close(self):
        self.game.stop(False)


class Environment(Base):
    def __init__(self, rom_path='pokemon_red.gb',
                 state_path=None, headless=True, quiet=False, verbose=False, **kwargs):
        super().__init__(rom_path, state_path, headless, quiet, verbose, **kwargs)
        self.counts_map = np.zeros((444, 365))
        self.verbose = verbose
        self.screenshot_counter = 0
        self.include_conditions = []
        self.seen_maps_difference = set()
        self.seen_maps = 0
        self.
        self.current_maps = []
        # self.exclude_map_n = {37, 38, 39, 43, 52, 53, 55, 57}
        self.exclude_map_n = set()
        self.exclude_map_n_moon = {0, 1, 2, 12, 13, 14, 15, 33, 34, 37, 38, 39, 40, 41, 42, 43, 44, 47, 50, 51, 52, 53, 54, 55, 56, 57, 58, 193, 68}

    def save_screenshot(self, x, y, steps, comment):
        self.screenshot_counter += 1
        ss_dir = Path('screenshots')
        ss_dir.mkdir(exist_ok=True)
        plt.imsave(
            ss_dir / Path(f'ss_{x}_y_{y}_steps_{steps}_{comment}.jpeg'),
            self.screen.screen_ndarray())  # (144, 160, 3)

    def update_heat_map(self, r, c, current_map):
        """
        Updates the heat map based on the agent's current position.

        Args:
            r (int): global y coordinate of the agent's position.
            c (int): global x coordinate of the agent's position.
            current_map (int): ID of the current map (map_n)

        Updates the counts_map to track the frequency of visits to each position on the map.
        """
        # Convert local position to global position
        glob_r, glob_c = game_map.local_to_global(r, c, current_map)

        # Update heat map based on current map
        if self.last_map == current_map or self.last_map == -1:
            # Increment count for current global position
            self.counts_map[(glob_r, glob_c)] += 1
        else:
            # Reset count for current global position if it's a new map for warp artifacts
            self.counts_map[(glob_r, glob_c)] = -1

        # Update last_map for the next iteration
        self.last_map = current_map

    def check_exclude_include(self, glob_r, glob_c, map_n):
        # EXCLUDE coordinates
        '''
        red_house_f1
        red_house_f2
        blue_house
        pokemon_academy
        pewter_museum_f1
        pewter_museum_f2
        trainer_house_trader_pewter
        trainer_house_npc_pewter
        '''


        # print(f'LINE 135 exclude_map_n: {self.exclude_map_n}')
        # print(f'LINE 136 self.seen_maps: {self.seen_maps}')
        # print(f'LINE 137 map_n = {map_n}')
        if map_n not in self.seen_maps:
            self.current_maps.append(map_n)
            # print(f'LINE 141 self.current_maps.append(map_n): {self.current_maps}')
            # print(f'LINE 142 len(self.current_maps)={len(self.current_maps)}')
            if len(self.current_maps) == 1:
                pass
            if len(self.current_maps) == 2 and self.current_maps[0] == self.current_maps[1]:
                self.current_maps.pop(1)
                pass
            if len(self.current_maps) == 2 and self.current_maps[0] != self.current_maps[1]:
                self.seen_maps.add(self.current_maps[0])
                # print(f'LINE 147 self.seen_maps.add(self.current_maps[0]): {self.seen_maps}')
                self.current_maps.pop(0)
                # print(f'LINE 149 self.current_maps.pop(0): {self.current_maps}')
                self.exclude_map_n = self.seen_maps.union(self.exclude_map_n)
                # print(f'LINE 151 exclude_map_n (new): {self.exclude_map_n}')

        self.include_conditions = [
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
            (137 <= glob_c <= 197) and (82 <= glob_r <= 142), # Mt Moon Route 3
            (137 <= glob_c <= 187) and (53 <= glob_r <= 103), # Mt Moon B1F
            (137 <= glob_c <= 197) and (16 <= glob_r <= 66), # Mt Moon B2F
            (137 <= glob_c <= 365) and (82 <= glob_r <= 444),  # Most of the rest of map after Mt Moon
        ]
            # print(f'executing INCLUDE_CONDITIONS')
            # INCLUDE coordinates
        return any(self.include_conditions)

    r, c, map_n = ram_map.position(self.game)
    self.seen_coords.add((r, c, map_n))
    self.seen_maps.add(map_n)

        # INCLUDE coordinates

        # INCLUDE coordinates

    def print_coordinate_test(self, glob_r, glob_c):
        include_conditions = self.include_conditions

        for line_num, (condition, pair) in enumerate(zip(include_conditions, self.include_conditions), start=133):
            if condition:
                print(f"Line {line_num}: {pair}: {condition}")

    def reset(self, seed=None, options=None, max_episode_steps=20480, reward_scale=3.0):
        '''Resets the game. Seeding is NOT supported'''
        load_pyboy_state(self.game, self.initial_state)

        self.time = 0
        self.max_episode_steps = max_episode_steps
        self.reward_scale = reward_scale

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
        # self.moon = False

        return self.render()[::2, ::2], {}

    def step(self, action, fast_video=True):
        run_action_on_emulator(self.game, self.screen, ACTIONS[action],
                               self.headless, fast_video=fast_video)
        self.time += 1

        if self.time == 1:
            self.event_r_pc = 0
            self.level_r_pc = 0
            self.opp_lvl_r_pc = 0
            self.death_r_pc = 0
            self.badges_r_pc = 0
            self.heal_r_pc = 0
            self.explor_r_pc = 0
            self.list_r_pc = 0
            self.total_r_pc = 0

        # Exploration reward
        # map_n in map_data.json; towns are 0-10, routes are 12-36, buildings and dungeons are randomly numbered 37+
        r, c, map_n = ram_map.position(self.game)
        glob_r, glob_c = game_map.local_to_global(r, c, map_n)

        if map_n == 15 or map_n >= 59:
            exploration_reward = 0.05 * len(self.seen_coords) # 0.01
            # glob_r, glob_c = game_map.local_to_global(r, c, map_n)
            # try:
            #     self.counts_map[glob_r, glob_c] += 1
            # except:
            #     pass
        else:
            # Check for exclusion and inclusion conditions
            if not self.check_exclude_include(glob_r, glob_c, map_n) and map_n != 54:
                self.seen_coords_no_reward.add((r, c, map_n))
            else:
                self.seen_coords.add((r, c, map_n))
                self.seen_maps.add(map_n)

            if map_n == 3 or map_n == 65 or map_n == 64 or map_n == 66:
                exploration_reward = 0.05 * len(self.seen_coords)  # 0.01
            else:
                exploration_reward = 0.01 * len(self.seen_coords)

        # self.print_coordinate_test(glob_r, glob_c)

        # Level reward
        party, party_size, party_levels = ram_map.party(self.game)
        self.max_level_sum = max(self.max_level_sum, sum(party_levels))
        if self.max_level_sum < 30:
            level_reward = 1 * self.max_level_sum
        else:
            level_reward = 1.75 + (self.max_level_sum - 50) / 4

        # Healing and death rewards
        party, party_size, party_levels = ram_map.party(self.game)
        hp = ram_map.hp(self.game)
        hp_delta = hp - self.last_hp
        party_size_constant = party_size == self.last_party_size

        # Dead if hp is zero
        if self.last_hp > 0 >= hp:
            self.death_count += 1
            # asyncio.run(self.save_screenshot(f'Death',f'Deaths_{self.death_count}_at_{self.map_name}_({c},{r})_step_{self.time}'))
            hp_delta = -1
            self.last_hp = 1
        else:
            if hp_delta > 0.30 and self.last_hp != 0.00 and party_size_constant:
                self.total_healing += hp_delta
                # asyncio.run(self.save_screenshot(f'Healing',f'healed_{round(self.total_healing, 2)}_from_{round(self.last_hp,2)}_at_{self.map_name}_({c},{r})_step_{self.time}'))
            else:
                self.total_healing = 0
            # Update last known values for next iteration
        self.last_hp = hp
        self.last_party_size = party_size

        # Set rewards
        healing_reward = self.total_healing
        death_reward = 0 # -0.08 * self.death_count  # -0.05

        # Opponent level reward
        max_opponent_level = max(ram_map.opponent(self.game))
        self.max_opponent_level = max(self.max_opponent_level, max_opponent_level)
        opponent_level_reward = 0 # 0.2 * self.max_opponent_level # 0 for mt moon testing

        # Badge reward
        badges = ram_map.badges(self.game)
        # badges_reward = 7 * badges  # 5
        badges_reward = 7

        # Event reward
        events = ram_map.events(self.game)
        self.max_events = max(self.max_events, events)
        event_reward = 0 # self.max_events

        money = ram_map.money(self.game)

        reward_components = (event_reward + level_reward +
                             opponent_level_reward + death_reward + badges_reward +
                             healing_reward + exploration_reward)

        if reward_components == 0:
            pass
        else:
            self.event_r_pc = events / reward_components * 100
            self.level_r_pc = level_reward / reward_components * 100
            self.opp_lvl_r_pc = opponent_level_reward / reward_components * 100
            self.death_r_pc = death_reward / reward_components * 100
            self.badges_r_pc = badges_reward / reward_components * 100
            self.heal_r_pc = healing_reward / reward_components * 100
            self.explor_r_pc = exploration_reward / reward_components * 100
            self.list_r_pc = (self.event_r_pc, self.level_r_pc, self.opp_lvl_r_pc, self.death_r_pc, self.badges_r_pc, self.heal_r_pc, self.explor_r_pc)
            self.total_r_pc = sum(self.list_r_pc)

        reward = self.reward_scale * reward_components

        # Subtract previous reward
        # TODO: Don't record large cumulative rewards in the first place
        if self.last_reward is None:
            reward = 0
            self.last_reward = 0
        else:
            nxt_reward = reward
            reward -= self.last_reward
            self.last_reward = nxt_reward

        last_ai_reward_list = list()
        last_ai_reward_list.append(reward)

        info = {}
        done = self.time >= self.max_episode_steps
        if done:
            info = {
                'reward': {
                    'delta': reward,
                    'event': event_reward,
                    'level': level_reward,
                    'opponent_level': opponent_level_reward,
                    'death': death_reward,
                    'badges': badges_reward,
                    'healing': healing_reward,
                    'exploration': exploration_reward,
                },
                'maps_explored': len(self.seen_maps),
                'party_size': party_size,
                'highest_pokemon_level': max(party_levels),
                'total_party_level': sum(party_levels),
                'deaths': self.death_count,
                'badge_1': float(badges == 1),
                'badge_2': float(badges > 1),
                'event': events,
                'money': money,
                'pokemon_exploration_map': self.counts_map,
            }

        if self.verbose:

            print(
                f'steps: {self.time}\n',
                f'level_reward: {level_reward}\n',
                f'healing: {healing_reward}\n',
                f'death: {death_reward}\n',
                f'ai reward: {reward}\n',
                f'Info: {info}\n',
                f'exploration reward: {exploration_reward}\n',
                f'non-rewardable coords explored: {len(self.seen_coords_no_reward)}\n',
                f'rewardable coords explored: {len(self.seen_coords)}\n',
                # f'=======================================================\n',
                # f'x_pos_addr: X POSITION ADDRESS VALUE= {ram_map.mem_val(self.game, 0xD362)}\n',
                # f'y_pos_addr: Y POSITION ADDRESS VALUE= {ram_map.mem_val(self.game, 0xD361)}\n',
                # f'glob_c (GLOBAL X POSITION): {glob_c}\n',
                # f'glob_r (GLOBAL Y POSITION): {glob_r}\n',
                # f'c (LOCAL X POSITION): {c}\n',
                # f'r (LOCAL Y POSITION): {r}\n',
                f'map_n (MAP ADDRESS VALUE): {map_n}\n\n',
                f' REWARD PERCENTAGES\n',
                f'event_r_pc = {self.event_r_pc}\n',
                f'level_r_pc =  {self.level_r_pc}\n',
                f'opp_lvl_r_pc =  {self.opp_lvl_r_pc}\n',
                f'death_r_pc =  {self.death_r_pc}\n',
                f'badges_r_pc =  {self.badges_r_pc}\n',
                f'heal_r_pc =  {self.heal_r_pc}\n',
                f'explor_r_pc =  {self.explor_r_pc}\n',
                f'total_r_pc = {self.total_r_pc}\n\n',
                f'death_r_pc = {self.death_r_pc}\n',
                f'opp_level: {opponent_level_reward}\n',
                f'badges reward: {badges_reward}\n',
                f'event reward: {event_reward}\n',
                f'money: {money}\n',

            )
            # rewardable_area = self.check_exclude_include(glob_r, glob_c, map_n)
            # if rewardable_area:
            #     print(f'Agent is in rewardable area. {rewardable_area}\n')
            # elif not rewardable_area:
            #     print(f'Agent is not in rewardable area. {rewardable_area}\n')
            # else:
            #     print(f'ERROR! AREA NEITHER INCLUDED NOR EXCLUDED! ({glob_c},{glob_r})\n')

        return self.render()[::2, ::2], reward, done, done, info