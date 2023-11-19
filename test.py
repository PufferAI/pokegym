from pdb import set_trace as T
import gymnasium

from pokegym import PokemonRed, PokemonRedV1
import time


def play_game(steps):
    game = PokemonRed(headless=False)
    game.reset()

    for _ in range(steps):
        game.render()
        game.step(game.action_space.sample())

def performance_test(game_cls, steps=10000):
    game = game_cls()
    game.reset()

    for _ in range(1000):
        game.step(0)#game.action_space.sample())

    start = time.time()
    for _ in range(steps):
        game.step(0)#game.action_space.sample())

    game.close()
    end = time.time()
    print('Steps per second: {}'.format(steps / (end - start)))

if __name__ == '__main__':
    performance_test(PokemonRed)
    performance_test(PokemonRedV1)
