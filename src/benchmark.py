import json
import random
import os
import argparse 

import pandas as pd
import numpy as np

from tqdm import tqdm

try:
    from src import config
except:
    import config

from game import Game
from strategies.abstract import AbstractStrategy


def _init_argparse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Enter game options"
    )
    parser.add_argument('--gen', '-g', dest='gen', type=int,
                        help='Choose the generation of pokemons', default=1)
    parser.add_argument('--net', '-n', dest='net', action='store_true',
                        help='Choose columns for the game')
    parser.add_argument('--i', '-iterations', dest='iterations', default=1,
                        help='Choose number of iterations in the benchmark')
    parser.add_argument('--verbose', dest='verbose', type=int, default=0,
                        help='0 means no info about correctness or not. 1 means it tells you if it is correct or not!')
    args = parser.parse_args()
    print(f'Running args:{args}')
    return args

class BenchMark:

    def __init__(self, strat: AbstractStrategy, dex: pd.DataFrame, gen: int, net: bool, random_state: int = None, strat_kwargs: dict = {}):
        """
        IMPORTANT:
        - strat should not be instantiated, only the class itself. 
            So call it like: `BenchMark(RandomStrategy, ...)`, not `BenchMark(RandomStrategy(), ...)`
        """

        self.strat = strat
        self.dex = dex
        self.gen = gen
        self.net = net
        self.results = []
        self.strat_kwargs = strat_kwargs

        if random_state is not None:
            self.random_state = random_state
        else:
            self.random_state = random.randint(0, 1000)


    def run(self, n: int, verbose: bool = False):
        seeds = np.random.default_rng(self.random_state).permutation(n).tolist()
           
        for _ in tqdm(range(n), desc="Benchmarking...", disable=not verbose):
            game = Game(dex=self.dex, gen=self.gen, net=self.net, random_state=seeds.pop())
            strat = self.strat(self.dex.copy(), self.gen, self.net, **self.strat_kwargs)
            
            hints = []
            while not game.end:
                guess = strat.guess(hints)
                _, hint = game.guess(guess)
                hints.append(hint)

            self.results.append({
                'target': game.pokemon.to_dict(),
                'tries': game.tries,
                'hints': hints,
            })

        return [r["tries"] for r in self.results]

    def save(self, out_filename=None):
        if out_filename is None:
            out_filename = config.RESULT_DIR / f"{self.strat.name}_gen{self.gen}{'_net' if self.net else ''}_rs{self.random_state}.json"

        print(self.results)
        with open(out_filename, 'w') as f:
            json.dump(self.results, f)



if __name__ == "__main__":
    args = _init_argparse()
    dex = pd.read_csv(config.DATA_DIR / f"dex_gen{args.gen}.csv", dtype={
        "pokedex_number": int,
        "generation": int,
        "evolution_stage": int,
        "fully_evolved": bool,
        "height_m": float,
        "weight_kg": float
    })    

    from strategies.random import RandomStrategy
    from strategies.slowpoke import SlowpokeStrategy
    from strategies.biggestdivider import BiggestDividerStrategy

    #bench = BenchMark(SlowpokeStrategy, dex, gen=1, net=False, strat_kwargs={"initial_guess": "slowpoke"})
    bench = BenchMark(BiggestDividerStrategy, dex, gen=args.gen, net=args.net)

    results = bench.run(args.iterations, verbose=bool(args.verbose))

    print(results)

    # bench.save()