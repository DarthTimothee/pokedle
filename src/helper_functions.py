import pandas as pd
import requests
import shutil
import os
from shutil import which
import argparse
    
    
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
    parser.add_argument('--repeats_benchmark', '-rb', dest='repeats', default=1, type=int,
                        help='Choose number of repeats per pokemon in the benchmark')
    parser.add_argument('--verbose_game', '-vg', dest='verbose_game', type=int, default=0,
                        help='0 means no info about correctness or not. 1 means it tells you if it is correct or not!')
    parser.add_argument('--verbose_benchmark', '-vb', dest='verbose_benchmark', type=int, default=0,
                        help='0 means no info about correctness or not. 1 means it tells you if it is correct or not!')
    args = parser.parse_args()
    print(f'Running args:{args}')
    return args

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
            
def image_checker(imagify, dex, pokemon_pic_loc):
    if imagify and which('catimg') is None:
        print(f'Images will not be available. Please install catimg package into your system with brew(os) or apt-get(linux).')
        imagify = False
    elif imagify and not os.path.exists(pokemon_pic_loc):
        print(f"catimg package is available but picture of pokemon at {pokemon_pic_loc.parent} does not exist!")
        imagify = False
        img_download_permission = input("Do you want to download pictures to data/img location? (yes,y,true,1 or no,n,false,0)")
        if img_download_permission.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
            download_pokemon_images(dex, pokemon_pic_loc.parent, verbose=False)
            if os.path.exists(pokemon_pic_loc):
                imagify = True
                
    return imagify