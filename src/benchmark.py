import json
import random
import os

import pandas as pd
import numpy as np

from tqdm import tqdm

from game import Game
from strategies.abstract import AbstractStrategy

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
        if not os.path.exists("results"):
            os.makedirs("results")

        if out_filename is None:
            out_filename = f"results/{self.strat.name}_gen{self.gen}{'_net' if self.net else ''}.json"

        print(self.results)
        with open(out_filename, 'w') as f:
            json.dump(self.results, f)



if __name__ == "__main__":

    gen = 1
    dex = pd.read_csv(f"data/dex_gen{gen}.csv", dtype={
        "pokedex_number": int,
        "generation": int,
        "evolution_stage": int,
        "fully_evolved": bool,
        "height_m": float,
        "weight_kg": float
    })    

    from strategies.random import RandomStrategy
    from strategies.slowpoke import SlowpokeStrategy

    bench = BenchMark(SlowpokeStrategy, dex, gen=1, net=False, strat_kwargs={"initial_guess": "slowpoke"})

    results = bench.run(1000, verbose=False)

    print(results)

    # bench.save()