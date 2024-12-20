import pandas as pd
import numpy as np
import argparse
import inquirer
import os, time
import random

try:
    from src import config
except:
    import config
    
from src import helper_functions


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
    parser.add_argument('--imagify', dest='imagify', action='store_true', 
                        help='When the game is won, show the image of the pokemon!')
    parser.add_argument('--verbose', dest='verbose', type=int, default=0,
                        help='0 means no info about correctness or not. 1 means it tells you if it is correct or not!')
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
    def __init__(self, dex, gen, net: bool = False, 
                 random_state: int = None, imagify: bool = False, 
                 verbose: int = 1, multiple_typings: dict = {}):
        self.dex = dex
        self.gen = gen
        self.net = net
        self.imagify = imagify
        self.verbose = verbose
        self.multiple_typings = multiple_typings #{'type1': 'type2', 'type2':'type1'}
        
        if random_state is not None:
            self.random_state = random_state
        else:
            self.random_state = random.randint(0, 1000)

        # select a random pokemon from the dex and image location
        self.pokemon = self.dex.sample(1).iloc[0]
        self.pokemon_pic_loc = config.DATA_DIR / 'img' / f'gen{self.gen}' / f'{self.pokemon["name"]}.jpg'

        if self.net:
            self.prediction_cols = ["type1", "type2", "habitat", "color", "evolution_stage", "height", "weight"]
        else:
            self.prediction_cols = ["type1", "type2", "evolution_stage", "fully_evolved", "color", "habitat", "generation"]
        
        self._discretizer() 
        
        #Check if images exist
        helper_functions.image_checker(self.imagify, self.dex, self.pokemon_pic_loc)
        
        # game related settings
        self.end = False
        self.tries = 0
    
    def _completer(self, text, state):
        teams = self.dex['name'].values
        candidates = [team for team in teams if team.startswith(text.lower())]
        if candidates:
            return candidates[state % len(candidates)]
    
    def _discretizer(self):
        encoded_df = self.dex[self.prediction_cols].copy()
        categorizable_cols = self.dex[encoded_df.columns].select_dtypes(['object', 'bool']).columns
        encoded_df[categorizable_cols] = encoded_df[categorizable_cols].astype('category')
        self.encoder_conversion = {col: encoded_df[col].cat.categories.values for col in categorizable_cols}
        encoded_df[categorizable_cols] = encoded_df[categorizable_cols].apply(lambda x: x.cat.codes)
        self.encoded_matrix = encoded_df.values
        
    def game_ending(self):
        if self.end:
            if self.verbose==1:
                for _ in range(1):  # Loop the animation 3 times
                    print("🎉 " * 10)
                    time.sleep(0.3)
                    print("✨ " * 10)
                    time.sleep(0.3)
            print("🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉\nYou won!")
            if self.imagify:
                os.system(f"catimg -r 2 -w 80 {self.pokemon_pic_loc.absolute().as_posix()}")


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

        d = {}
        # For each column we check if it's correct, so we can give it as a hint
        for col in self.prediction_cols:
            guessed_val = guessed_pokemon[col]
            d[col] = [guessed_val, bool(guessed_val == self.pokemon[col])]
            if self.multiple_typings and col in self.multiple_typings and guessed_val == self.pokemon[self.multiple_typings[col]]:
                d[col] = [guessed_val, 2]
                
        return self.end, d
    
    def set_target(self, target_pokemon: str):
        self.pokemon = self.dex[self.dex["name"] == target_pokemon].iloc[0]
        self.end = False
        self.tries = 0
        helper_functions.image_checker(self.imagify, self.dex, self.pokemon_pic_loc)


if __name__ == "__main__":
    args = _init_argparse()
    if args.testing:
        print(args)
    gen = args.gen #1
    net = args.net #False
    
    dex = pd.read_csv(config.DATA_DIR / f'dex_gen{gen}.csv', dtype={
        "pokedex_number": int,
        "generation": int,
        "evolution_stage": int,
        "fully_evolved": bool,
        "height_m": float,
        "weight_kg": float
    })
    multiple_typings = {'type1': 'type2', 'type2':'type1'}
    game = Game(dex, gen=gen, net=net, imagify=args.imagify, verbose=args.verbose, multiple_typings=multiple_typings)
    if args.testing:
        print(f"Testing stage activated! Answer is: {game.pokemon['name']}")

    while not game.end:
        #name = input("Enter a pokemon name: ")
        name = inquirer.text("Enter a pokemon name", autocomplete=game._completer)
        iscorrect, hints = game.guess(name)

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
