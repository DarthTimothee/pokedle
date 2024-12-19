import pandas as pd
import numpy as np
import argparse
import inquirer
import os, time

def _init_argparse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Enter game options"
    )
    parser.add_argument('--gen', '-g', dest='gen', type=int,
                        help='Choose the generation of pokemons', default=1)
    parser.add_argument('--net', '-n', dest='net', action='store_true',
                        help='Choose columns for the game')
    parser.add_argument('--testing', dest='testing', action='store_true',
                        help='Answer is shown before the game starts, do it for testing and debugging purposes!')
    parser.add_argument('--v2', dest='updated_version', action='store_true',
                        help='Work with updated version that shows yellow color when type is correct but in wrong column')
    args = parser.parse_args()
    print(f'Running args:{args}')
    return args

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
    def __init__(self, dex, gen, net: bool = False, random_state: int = None, updated_version: bool = False):
        self.dex = dex
        self.gen = gen
        self.net = net

        # select a random pokemon from the dex
        self.pokemon = self.dex.sample(1).iloc[0]
        
        # game related settings
        self.end = False
        self.tries = 0
    
    def _completer(self, text, state):
        teams = self.dex['name'].values
        candidates = [team for team in teams if team.startswith(text.lower())]
        if candidates:
            return candidates[state % len(candidates)]
        
    def game_ending(self):
        if game.end:
            for _ in range(3):  # Loop the animation 3 times
                print("🎉 " * 10)
                time.sleep(0.3)
                print("✨ " * 10)
                time.sleep(0.3)
            print("🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉\nYou won!")


    def guess(self, name) -> bool:
        name = name.lower() #Convert the name to lower case
        
        guessed_pokemon = self.dex[self.dex["name"] == name].iloc[0]
        if guessed_pokemon.empty:
            name = find_closest_string(name, self.dex["name"].values)
            print(f"Corrected to: {name}")
            guessed_pokemon = self.dex[self.dex["name"] == name].iloc[0]

        self.tries += 1

        if guessed_pokemon["name"] == self.pokemon["name"]:
            self.end = True

        com_cols = ["type1", "type2", "evolution_stage", "fully_evolved", "color", "habitat", "generation"]
        net_cols = ["type1", "type2", "habitat", "color", "evolution_stage", "height", "weight"]

        if self.net:
            cols = net_cols
        else:
            cols = com_cols


        if not updated_version:
            # For each column we check if it's correct, so we can give it as a hint (old version)
            d = {}
            for col in cols:
                guessed_val = guessed_pokemon[col]
                d[col] = [guessed_val, bool(guessed_val == self.pokemon[col])   ]
            return self.end, d
        else:
        # EXPERIMENTAL: check every column, but be aware of multiple typings (new version)
            d = {}
            for col in cols:
                guessed_val = guessed_pokemon[col]
                d[col] = [guessed_val, 0]
                if col == "type1":
                    if guessed_val == self.pokemon["type1"]:
                        d[col][1] = 1
                    elif guessed_val == self.pokemon["type2"]:
                        d[col][1] = 2
                elif col == "type2":
                    if guessed_val == self.pokemon["type2"]:
                        d[col][1] = 1
                    elif guessed_val == self.pokemon["type1"]:
                        d[col][1] = 2
                else:
                    if guessed_val == self.pokemon[col]:
                        d[col][1] = 1
        return self.end, d



if __name__ == "__main__":
    args = _init_argparse()
    if args.testing:
        print(args)
    gen = args.gen #1
    net = args.net #False
    dex = pd.read_csv(f"data/dex_gen{gen}.csv", dtype={
        "pokedex_number": int,
        "generation": int,
        "evolution_stage": int,
        "fully_evolved": bool,
        "height_m": float,
        "weight_kg": float
    })
    updated_version = args.updated_version
    game = Game(dex, gen=gen, net=net, updated_version=updated_version)
    if args.testing:
        print(f"Testing stage activated! Answer is: {game.pokemon['name']}")

    while not game.end:
        #name = input("Enter a pokemon name: ")
        name = inquirer.text("Enter a pokemon name", autocomplete=game._completer)
        iscorrect, hints = game.guess(name)


        if not updated_version:
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

        else:
            # pretty print each hint with colored background
            # if the hint is correct, the background will be green
            # if the hint is incorrect, the background will be red
            # TODO: align the columns
            # EXPERIMENTAL: yellow color if type is correct but in wrong column
            line = ""
            for k, v in hints.items():
                if v[1] == 1:
                    # correct -> green background
                    line += f"\033[42m{k}: {v[0]}\033[0m "
                elif v[1] == 2:
                    # semi-correct -> yellow background
                    line += f"\033[43m{k}: {v[0]}\033[0m "
                else:
                    # wrong -> red background
                    line += f"\033[41m{k}: {v[0]}\033[0m "
        print(line)

    game.game_ending()
    print(f"You took {game.tries} tries")
