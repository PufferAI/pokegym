from pdb import set_trace as T
from gymnasium import Env, spaces
import numpy as np
import os

from pokegym.pyboy_binding import (ACTIONS, make_env, open_state_file,
    load_pyboy_state, run_action_on_emulator)
from pokegym import ram_map, game_map


def play():
    '''Creates an environment and plays it'''
    env = PokemonRed(rom_path='pokemon_red.gb', state_path=None, headless=False,
        disable_input=False, sound=False, sound_emulated=False
    )
    env.reset()

    env.game.set_emulation_speed(3)
    while True:
        env.render()
        env.game.tick()

class PokemonRed:
    def __init__(self, rom_path='pokemon_red.gb',
            state_path=None, headless=True, quiet=False,
            disable_input=True, sound=False, sound_emulated=False):
        '''Creates a PokemonRed environment'''
        if state_path is None:
            state_path = __file__.rstrip('environment.py') + 'has_pokedex_nballs.state'

        self.game, self.screen = make_env(
            rom_path, headless, quiet,
            disable_input=disable_input,
            sound_emulated=sound_emulated,
            sound=sound,
        )
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


class PokemonRedV1(PokemonRed):
    def __init__(self, rom_path='pokemon_red.gb',
            state_path=None, headless=True, quiet=False):
        super().__init__(rom_path, state_path, headless, quiet)
        self.counts_map = np.zeros((444, 365))

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

        self.death_count = 0
        self.total_healing = 0
        self.last_hp_fraction = 1.0
        self.last_party_size = 1
        self.last_reward = None

        return self.render()[::2, ::2], {}

    def step(self, action):
        run_action_on_emulator(self.game, self.screen, ACTIONS[action], self.headless)
        self.time += 1

        # Exploration reward
        r, c, map_n = ram_map.position(self.game)
        self.seen_coords.add((r, c, map_n))
        self.seen_maps.add(map_n)
        exploration_reward = 0.01 * len(self.seen_coords)
        glob_r, glob_c = game_map.local_to_global(r, c, map_n)
        try:
            self.counts_map[glob_r, glob_c] += 1
        except:
            pass

        # Level reward
        party, party_size, party_levels = ram_map.party(self.game)
        self.max_level_sum = max(self.max_level_sum, sum(party_levels))
        if self.max_level_sum < 30:
            level_reward = 4 * self.max_level_sum
        else:
            level_reward = 30 + (self.max_level_sum - 30)/4

        # Healing and death rewards
        hp_fraction = ram_map.hp_fraction(self.game)
        fraction_increased = hp_fraction > self.last_hp_fraction
        party_size_constant = party_size == self.last_party_size
        if fraction_increased and party_size_constant:
            if self.last_hp_fraction > 0:
                self.total_healing += hp_fraction - self.last_hp_fraction
            else:
                self.death_count += 1
        healing_reward = self.total_healing
        death_reward = -0.05 * self.death_count

        # Opponent level reward
        max_opponent_level = max(ram_map.opponent(self.game))
        self.max_opponent_level = max(self.max_opponent_level, max_opponent_level)
        opponent_level_reward = 0.2 * self.max_opponent_level

        # Badge reward
        badges = ram_map.badges(self.game)
        badges_reward = 5 * badges

        # Event reward
        events = ram_map.events(self.game)
        self.max_events = max(self.max_events, events)
        event_reward = self.max_events

        money = ram_map.money(self.game)

        reward = self.reward_scale * (event_reward + level_reward + 
            opponent_level_reward + death_reward + badges_reward +
            healing_reward + exploration_reward)

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

        return self.render()[::2, ::2], reward, done, done, info
