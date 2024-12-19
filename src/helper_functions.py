import pandas as pd
import requests
import shutil
import os
from pathlib import Path
    
def download_pokemon_images(dex, save_folder, verbose=False):
    save_folder.mkdir(parents=True, exist_ok=True)
    for pokemon_name in dex['name'].values:
        url = f'https://img.pokemondb.net/artwork/{pokemon_name}.jpg'
        save_loc = save_folder / f'{pokemon_name}.jpg'
        res = requests.get(url, stream = True)
        if res.status_code == 200:
            with open(save_loc,'wb') as f:
                shutil.copyfileobj(res.raw, f)
            if verbose:
                print('Image sucessfully Downloaded: ',save_loc)
        else:
            print('Image Couldn\'t be retrieved')
            
