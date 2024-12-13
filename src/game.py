import pandas as pd
import numpy as np



def _levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            s1, s2 = s2, s1
        
        prev_row = range(len(s2) + 1)
        current_row = [0] * (len(s2) + 1)
        
        for i in range(len(s1)):
            current_row[0] = i + 1
            for j in range(len(s2)):
                add = prev_row[j + 1] + 1
                delete = current_row[j] + 1
                change = prev_row[j]
                if s1[i] != s2[j]:
                    change += 1
                current_row[j + 1] = min(add, delete, change)
            prev_row = current_row[:]
            
        return prev_row[-1]

def find_closest_string(target, string_list):
    
    closest = string_list[0]
    min_distance = _levenshtein_distance(target, closest)
    
    for string in string_list[1:]:
        distance = _levenshtein_distance(target, string)
        if distance < min_distance:
            min_distance = distance
            closest = string
            
    return closest


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
            name = find_closest_string(name, self.dex["name_api"].values)
            print(f"Corrected to: {name}")
            guessed_pokemon = self.dex[self.dex["name_api"] == name]

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
