import pandas as pd
import numpy as np
import argparse
import inquirer
import os, time
from src import game

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

class Predictor:
    def __init__(self, dex, gen, net: bool = False, heuristic='random'):
        self.dex = dex
        self.gen = gen
        self.net = net
        self.heuristic = heuristic
        
        self.dex['is_predicted']=False
        self.dex['possible']=True
        if self.net:
            self.prediction_columns = ["type1", "type2", "habitat", "color", "evolution_stage", "height", "weight"]
        else:
            self.prediction_columns = ["type1", "type2", "evolution_stage", "fully_evolved", "color", "habitat", "generation"]
        
        self.investigation_dex = self.dex[(self.dex['is_predicted']==False)&(self.dex['possible']==True)]
        self.predictions = []
    
    def _elimination_gain(self, _, text):
        if text in self.dex['name'].values:
            return True
        raise inquirer.errors.ValidationError("", reason=f'Team "{text}" do not exist')
    
    def _calculate_frequencies(self, col):
        return self.investigation_dex[col].value_counts()/len(self.investigation_dex).to_dict()
        
    def _eliminate_unmatched(self, hints):
        for col, hint in hints.items():
            if hint[1]:
                self.dex.loc[self.dex[col]!=hint[0],'possible']=False
            elif not hint[1]:
                self.dex.loc[self.dex[col]==hint[0],'possible']=False


    def predict(self):
        if self.heuristic=='random':
            choice = self.investigation_dex.sample(1).iloc[0]
        if self.heuristic=='elimination_gain':
            print('TBD')#choice = self.investigation_dex.sample(1).iloc[0]
            
        self.dex.loc[self.dex['name_api']==choice['name_api'],'is_predicted']=True
        self.predictions.append(choice)
        return choice
            
    def evaluate_response(self, hints):
        self._eliminate_unmatched(hints)
        self.investigation_dex = self.dex[(self.dex['is_predicted']==False)&(self.dex['possible']==True)]
            


if __name__ == "__main__":
    args = _init_argparse()
    if args.testing:
        print(args)
    gen = args.gen #1
    net = args.net #False
    guess_limit = args.guess_limit #Limit on number of guesses
    dex = pd.read_csv(f"data/dex_gen{gen}.csv").astype(str)
    game_instance = game.Game(dex=dex, gen=gen, net=net)
    predictor_instance = Predictor(dex=dex, gen=gen, net=net, heuristic='random')
    if args.testing:
        print(f"Testing stage activated! Answer is: {game_instance.pokemon['name']}")

    while not game_instance.end:
        #name = input("Enter a pokemon name: ")
        #name = inquirer.text("Enter a pokemon name", autocomplete=game._completer)#, validate=game._validator)
        prediction = predictor_instance.predict()
        print(f'Predictor predicted: {prediction["name"]}')
        iscorrect, hints = game_instance.guess(prediction['name'])
        game_instance.tries += 1
        if iscorrect:
            game_instance.end = True
            game_instance.won = True
        elif game_instance.tries >= guess_limit:
            game_instance.end = True
            game_instance.won = False
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
        
        predictor_instance.evaluate_response(hints)

    game_instance.game_ending()
    print(f"You took {game_instance.tries} tries")
