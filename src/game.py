import pandas as pd
import numpy as np


class Game:
    def __init__(self, dex, gen, net: bool = False):
        self.dex = dex
        self.gen = gen
        self.net = net

        # select a random pokemon from the dex
        self.pokemon = self.dex.sample(1).iloc[0]

    def guess(self, name) -> bool:
        
        guessed_pokemon = self.dex[self.dex["name_api"] == name]
        if guessed_pokemon.empty:
            print("Pokemon not found")
            return False, None

        if name == self.pokemon["name_api"]:
            print("Correct!")
        else:
            print("Incorrect!")

        com_cols = ["type1", "type2", "evolution_stage", "fully_evolved", "color", "habitat", "generation"]
        net_cols = ["type1", "type2", "habitat", "color", "evolution_stage", "height", "weight"]

        if self.net:
            cols = net_cols
        else:
            cols = com_cols

        # For each column we check if it's correct, so we can give it as a hint
        d = {}
        for col in cols:
            guessed_val = guessed_pokemon[col].values[0]
            correct = bool(guessed_val == self.pokemon[col])
            if col == "type2" and pd.isnull(guessed_val) and pd.isnull(self.pokemon[col]):
                correct = True
            d[col] = [guessed_val, correct]
        return name == self.pokemon["name_api"], d


if __name__ == "__main__":

    dex = pd.read_csv("data/dex_gen1.csv")
    game = Game(dex, gen=2, net=False)

    # print(game.pokemon)

    end = False
    tries = 0
    while not end:
        tries += 1
        name = input("Enter a pokemon name: ")
        end, hints = game.guess(name)
        if hints is None:
            continue

        # pretty print each hint with colored background
        # if the hint is correct, the background will be green
        # if the hint is incorrect, the background will be red
        # TODO: align the columns
        line = ""
        for k, v in hints.items():
            if v[1]:
                # correct, so green background
                line += f"\033[42m{k}: {v[0]}\033[0m "
            else:
                line += f"\033[41m{k}: {v[0]}\033[0m "
        print(line)

    print(f"You took {tries} tries")
