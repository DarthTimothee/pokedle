import pandas as pd
import numpy as np

from benchmark import BenchMark


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

    from strategies.slowpoke import SlowpokeStrategy

    seed = 42

    scores = {}
    for name in dex["name"]:
        bench = BenchMark(SlowpokeStrategy, dex, gen=1, net=False, strat_kwargs={"initial_guess": name}, random_state=seed)
        results = bench.run(1000, verbose=False)
        scores[name] = np.mean(results)
        print(f"Score for {name}: {np.mean(results):.3f} +- {np.std(results):.3f}")

    # find best starter
    best_starter = min(scores, key=scores.get)
    
    # bench.save()