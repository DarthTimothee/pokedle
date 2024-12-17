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
    parser.add_argument('--guess_limit', '-gl', dest='guess_limit', type=int,
                        help='Choose the number of limits for guesses', default=999)
    parser.add_argument('--testing', dest='testing', action='store_true',
                        help='Answer is shown before the game starts, do it for testing and debugging purposes!')
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
    def __init__(self, dex, gen, net: bool = False):
        self.dex = dex
        self.gen = gen
        self.net = net

        # select a random pokemon from the dex
        self.pokemon = self.dex.sample(1).iloc[0]
        
        # game related settings
        self.end = False
        self.won = False
        self.tries = 0
    
    def _validator(self, _, text):
        if text in self.dex['name'].values:
            return True
        raise inquirer.errors.ValidationError("", reason=f'Team "{text}" do not exist')
    
    def _completer(self, text, state):
        teams = self.dex['name'].values
        candidates = [team for team in teams if team.startswith(text.capitalize())]
        if candidates:
            return candidates[state % len(candidates)]
        
    def game_ending(self):
        if self.end and self.won:
            for _ in range(3):  # Loop the animation 3 times
                print("🎉 " * 10)
                time.sleep(0.3)
                print("✨ " * 10)
                time.sleep(0.3)
            print("🎉🎉🎉 CONGRATULATIONS! 🎉🎉🎉\nYou won!")
        if self.end and not self.won:
            print("You lost!")


    def guess(self, name) -> bool:
        name = name.lower() #Convert the name to lower case
        
        guessed_pokemon = self.dex[self.dex["name_api"] == name]
        if guessed_pokemon.empty:
            name = find_closest_string(name, self.dex["name_api"].values)
            print(f"Corrected to: {name}")
            guessed_pokemon = self.dex[self.dex["name_api"] == name]

        if guessed_pokemon.iloc[0]["name_api"] == self.pokemon["name_api"]:
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
        return guessed_pokemon.iloc[0]["name_api"] == self.pokemon["name_api"], d


if __name__ == "__main__":
    args = _init_argparse()
    if args.testing:
        print(args)
    gen = args.gen #1
    net = args.net #False
    guess_limit = args.guess_limit #Limit on number of guesses
    dex = pd.read_csv(f"data/dex_gen{gen}.csv")
    game = Game(dex, gen=gen, net=net)
    if args.testing:
        print(f"Testing stage activated! Answer is: {game.pokemon['name']}")

    while not game.end:
        #name = input("Enter a pokemon name: ")
        name = inquirer.text("Enter a pokemon name", autocomplete=game._completer)#, validate=game._validator)
        iscorrect, hints = game.guess(name)
        game.tries += 1
        if iscorrect:
            game.end = True
            game.won = True
        elif game.tries >= guess_limit:
            game.end = True
            game.won = False
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

    game.game_ending()
    print(f"You took {game.tries} tries")
