from pdb import set_trace as T
from gymnasium import Env, spaces
import numpy as np
import os

from pokegym.pyboy_binding import (ACTIONS, make_env, open_state_file,
    load_pyboy_state, run_action_on_emulator)
from pokegym import ram_map, game_map


def play():
    '''Creates an environment and plays it'''
    env = Environment(rom_path='pokemon_red.gb', state_path=None, headless=False,
        disable_input=False, sound=False, sound_emulated=False, verbose=True
    )

    env.reset()
    env.game.set_emulation_speed(1)

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
    def __init__(self, rom_path='pokemon_red.gb',
            state_path=None, headless=True, quiet=False, **kwargs):
        '''Creates a PokemonRed environment'''
        if state_path is None:
            state_path = __file__.rstrip('environment.py') + 'has_pokedex_nballs.state' # 'mtmoon.state'

        self.game, self.screen = make_env(
            rom_path, headless, quiet, **kwargs)

        self.initial_state = open_state_file(state_path)
        self.headless = headless

        R, C = self.screen.raw_screen_buffer_dims()
        self.observation_space = spaces.Box(
            low=0, high=255, dtype=np.uint8,
            shape=(R//2, C//2, 3),
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
        super().__init__(rom_path, state_path, headless, quiet, **kwargs)
        self.counts_map = np.zeros((444, 365))
        self.verbose = verbose

    def reset(self, seed=None, options=None, max_episode_steps=20480, reward_scale=4.0):
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

        self.total_healing = 0
        self.last_party_size = 1
        self.last_reward = None

        self.lvl = 0
        self.last_hp = [0] * 6
        self.death = 0

        return self.render()[::2, ::2], {}

    def step(self, action, fast_video=True):
        run_action_on_emulator(self.game, self.screen, ACTIONS[action],
            self.headless, fast_video=fast_video)
        self.time += 1

        # Exploration reward
        r, c, map_n = ram_map.position(self.game)
        self.seen_coords.add((r, c, map_n))
        self.seen_maps.add(map_n)
        coord_reward = 0.01 * len(self.seen_coords)
        map_reward = 1.0 * len(self.seen_maps)
        exploration_reward = coord_reward + map_reward

        glob_r, glob_c = game_map.local_to_global(r, c, map_n)
        try:
            self.counts_map[glob_r, glob_c] += 1
        except:
            pass

        # Level reward
        party, party_size, party_levels = ram_map.party(self.game)

        # Party rewards
        party_size_constant = party_size == self.last_party_size

        poke, type1, type2, level, hp = ram_map.pokemon(self.game) #  status,
        # Level
        level_rewards = []
        for lvl in level:
            if lvl < 15:
                level_reward = .5 * lvl
            else:
                level_reward = 7.5 + (lvl - 15) / 4
            level_rewards.append(level_reward)
        # HP / Death
        assert len(hp) == len(self.last_hp)
        for h, i in zip(hp, self.last_hp):
            hp_delta = h - i
            if hp_delta > 0 and party_size_constant:
                self.total_healing += hp_delta
            if h <= 0 and i > 0:
                self.death += 1
            i = h
        lvl_rew = sum(level_rewards)
        healing_reward = self.total_healing
        self.max_level_sum = sum(level)
        self.last_party_size = party_size
        death_reward = -0.05 * self.death

        # # Update last known values for next iteration
        self.last_hp = hp
        self.last_party_size = party_size

        # # Set rewards
        # healing_reward = self.total_healing
        # death_reward = -0.05 * self.death_count

        # Opponent level reward
        # max_opponent_level = max(ram_map.opponent(self.game))
        # self.max_opponent_level = max(self.max_opponent_level, max_opponent_level)
        # opponent_level_reward = 0.2 * self.max_opponent_level

        # Badge reward
        badges = ram_map.badges(self.game)
        badges_reward = 5 * badges

        # Event reward
        events = ram_map.events(self.game)
        self.max_events = max(self.max_events, events)
        event_reward = self.max_events

        #money reward
        money = ram_map.money(self.game)

        #sum reward
        reward = self.reward_scale * (event_reward + lvl_rew + death_reward + badges_reward + exploration_reward + healing_reward) # + healing_reward
        
        reward1 = (event_reward + lvl_rew + badges_reward + exploration_reward + healing_reward) # + healing_reward
        
        if death_reward == 0:
            neg_reward = 1
        else:
            neg_reward = death_reward

        #print rewards
        if self.headless == False:
            print(f'-------------Counter-------------')
            print(f'Steps:',self.time,)
            print(f'Sum Reward:',reward)
            print(f'Events:',self.max_events)
            print(f'Total Level:',self.max_level_sum)
            print(f'Levels:',level)
            print(f'HP:',hp)
            print(f'Deaths:',self.death)
            print(f'Total Heal:',self.total_healing)
            print(f'Party Size:',self.last_party_size)
            print(f'-------------Rewards-------------')
            print(f'Total:',reward1)
            print(f'Explore:',exploration_reward,'--%',100 * (exploration_reward/reward1))
            print(f'Healing:',healing_reward,'--%',100 * (healing_reward/reward1))
            print(f'Badges:',badges_reward,'--%',100 * (badges_reward/reward1))
            #print(f'Op Level:',opponent_level_reward,'--%',100 * (opponent_level_reward/reward1))
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
            # print(f'Coords:',self.seen_coords)
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
        if done:
            info = {
                'reward': {
                    'delta': reward,
                    'event': event_reward,
                    'level': level_reward,
                    #'opponent_level': opponent_level_reward,
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
                'badge_1': float(badges == 1),
                'badge_2': float(badges > 1),
                'event': events,
                'money': money,
                'pokemon_exploration_map': self.counts_map,
            }

        if self.verbose:
            print(
                f'steps: {self.time}',
                f'exploration reward: {exploration_reward}',
                f'level_Reward: {level_reward}',
                f'healing: {healing_reward}',
                f'death: {death_reward}',
                #f'op_level: {opponent_level_reward}',
                f'badges reward: {badges_reward}',
                f'event reward: {event_reward}',
                f'money: {money}',
                f'ai reward: {reward}',
                f'Info: {info}',
            )

        return self.render()[::2, ::2], reward, done, done, info
