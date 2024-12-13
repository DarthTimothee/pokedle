import os
import requests
import json

import pandas as pd


def _download_data():
    # Download data from the web
    # Return a pandas DataFrame
    
    os.system("curl -L -o data/dex.zip https://www.kaggle.com/api/v1/datasets/download/rounakbanik/pokemon")
    os.system("tar -xvf data/dex.zip -C data/")
    os.system("rm data/dex.zip")
    os.system("mv data/Pokemon.csv data/kaggle_raw.csv")


def _get_species_from_api(id: int, cols: list) -> dict:
    url = f"https://pokeapi.co/api/v2/pokemon-species/{id}"
    response = requests.get(url)
    data = json.loads(response.text)
    res = {}
    for col in cols:
        if col == "name":
            res[col] = data[col]
        elif col == "evolution_chain":
            res[col] = data[col]["url"]
        else:
            res[col] = data[col]["name"]
    return res


def _get_pokemon_from_api(id: int, cols: list) -> dict:
    url = f"https://pokeapi.co/api/v2/pokemon/{id}"
    response = requests.get(url)
    data = json.loads(response.text)
    res = {}
    for col in cols:
        res[col] = data[col]
    return res


def get_stage(name: str, chain_url: int, dex: pd.DataFrame):
    name = name.lower()
    response = requests.get(chain_url)
    data = json.loads(response.text)["chain"]
    stage1 = [data["species"]["name"]]
    stage2 = [e["species"]["name"] for e in data["evolves_to"]]
    stage3 = []
    for e in data["evolves_to"]:
        stage3 += [f["species"]["name"] for f in e["evolves_to"]]
    stage3 = list(set(stage3))

    # Filter out the pokemon that are not in the dex
    stage1 = [p for p in stage1 if p in dex["name_api"].values]
    stage2 = [p for p in stage2 if p in dex["name_api"].values]
    stage3 = [p for p in stage3 if p in dex["name_api"].values]
    
    # This could mean stage 1 is empty now, so we shift the stages (at most twice)
    for _ in range(2):
        if stage1 == []:
            stage1 = stage2
            stage2 = stage3
            stage3 = []

    # Get the evolution stage
    stage = 0
    if name in stage1:
        stage = 1
    elif name in stage2:
        stage = 2
    elif name in stage3:
        stage = 3

    # To find if it's fully evolved we find the max stage
    max_stage = 1
    if stage2 != []:
        max_stage = 2
        if stage3 != []:
            max_stage = 3
    is_fully_evolved = (stage == max_stage)

    return stage, is_fully_evolved


def _add_columns(raw: pd.DataFrame, gen: int = 1) -> pd.DataFrame:
    """
    Adds the missing columns to the dataset

    Parameters:
    raw (pd.DataFrame): The raw dataset
    com (bool): Whether the dataset is from .com or .org
    """

    # Required columns (.com)
    # - type 1
    # - type 2
    # - evolution_stage
    # - fully evolved
    # - color
    # - habitats
    # - generation

    # Required columns (.org)
    # - type 1
    # - type 2
    # - habitat
    # - color
    # - evolution_stage
    # - height
    # - weight

    dex = raw[["name", "pokedex_number", "type1", "type2", "generation", "weight_kg", "height_m"]]

    # from API, get name, color, habitat
    new_cols = dex["pokedex_number"].apply(_get_species_from_api, cols=["name", "color", "habitat", "evolution_chain"])
    new_cols = pd.DataFrame(new_cols.tolist())
    
    dex["name_api"] = new_cols["name"]
    dex["color"] = new_cols["color"]
    dex["habitat"] = new_cols["habitat"]
    dex["chain_url"] = new_cols["evolution_chain"]

    # Get the evolution stage and if it's fully evolved
    stages = []
    fully_evolveds = []
    for name, chain_url in zip(dex["name"], dex["chain_url"]):
        stage, is_fully_evolved = get_stage(name, chain_url, dex)
        stages.append(stage)
        fully_evolveds.append(is_fully_evolved)
    dex["evolution_stage"] = stages
    dex["fully_evolved"] = fully_evolveds

    dex.drop(columns=["chain_url"], inplace=True)
    dex_net = dex[["name", "pokedex_number", "type1", "type2", "evolution_stage", "fully_evolved", "color", "habitat", "generation"]]
    dex_com = dex[["name", "pokedex_number", "type1", "type2", "habitat", "color", "evolution_stage", "weight_kg", "height_m", "generation"]]
    return dex_net, dex_com, dex


def fix_types(dex: pd.DataFrame, gen: int = 1) -> pd.DataFrame:
    """
    Some pokemon have different types in different generations, so we get them from the API,
    and use the past_types field if it applies for this generation.

    Parameters:
    dex (pd.DataFrame): The dataset
    gen (int): The generation of the dataset
    """

    type1s = []
    type2s = []
    for id in dex["pokedex_number"]:
        f = _get_pokemon_from_api(id, cols=["past_types", "types"])
        types = f["types"]
        past_types = f["past_types"]

        # Get the types
        assert types[0]["slot"] == 1
        type1 = types[0]["type"]["name"]
        if len(types) > 1:
            assert types[1]["slot"] == 2
            type2 = types[1]["type"]["name"]
        else:
            type2 = None

        # Get the past types
        
        for t in past_types:
            type_gen = int(t["generation"]["url"].split("/")[-2])
            if gen <= type_gen:
                # Then this is the type we want

                types = t["types"]
                assert types[0]["slot"] == 1
                type1 = types[0]["type"]["name"]
                if len(types) > 1:
                    assert types[1]["slot"] == 2
                    type2 = types[1]["type"]["name"]
                else:
                    type2 = None
                
        type1s.append(type1)
        type2s.append(type2)

    dex["type1"] = type1s
    dex["type2"] = type2s
    return dex


if __name__ == "__main__":
    GEN = 2

    if not os.path.exists("data/kaggle_raw.csv"):
        _download_data()
    
    dex = pd.read_csv("data/kaggle_raw.csv")
    dex = dex[dex["generation"] <= GEN].copy()

    dex = fix_types(dex, gen=GEN)

    dex_net, dex_com, dex = _add_columns(dex, gen=GEN)

    if not os.path.exists("data"):
        os.mkdir("data")

    dex.to_csv(f"data/dex_gen{GEN}.csv", index=False)
    dex_net.to_csv(f"data/dex_gen{GEN}_net.csv", index=False)
    dex_com.to_csv(f"data/dex_gen{GEN}_com.csv", index=False)