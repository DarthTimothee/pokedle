import pandas as pd
import requests
import shutil
import os
from shutil import which
    
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