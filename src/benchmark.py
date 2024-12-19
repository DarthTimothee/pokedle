import json
import random
import os

import pandas as pd
import numpy as np

from tqdm import tqdm

from game import Game
from strategies.abstract import AbstractStrategy

class BenchMark:

    def __init__(self, strat: AbstractStrategy, dex: pd.DataFrame, gen: int, net: bool, random_state: int = None):
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

        if random_state is not None:
            self.random_state = random_state
        else:
            self.random_state = random.randint(0, 1000)


    def run(self, n: int):
    
        seeds = np.random.default_rng(self.random_state).permutation(n).tolist()
           
        for _ in tqdm(range(n), desc="Benchmarking..."):
            game = Game(dex=self.dex, gen=self.gen, net=self.net, random_state=seeds.pop())
            strat = self.strat(self.dex.copy(), self.gen, self.net)
            
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
        
        return self.results

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
    bench = BenchMark(RandomStrategy, dex, gen=1, net=False)

    results = bench.run(1)

    # bench.save()