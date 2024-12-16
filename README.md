# Pokedle Strategies

Pokedle is a daily puzzle game, inspired by Wordle where you have to guess a pokemon, and get hints based on your guesses, and which parts are correct (type, region, evolution stage). There are two different versions, hosted on http://www.pokedle.com/ and http://www.pokedle.net/ respectively, which use slightly different properties for the hints.

This repository provides some utility code for investigating the best strategies for guessing. Functionalities currently include:
- `get_dataset.py` - Dataset corresponding to the databases used in both versions mentioned above.
- `game.py` - Game simulation script, for testing purposes (or if you just want to play multiple times a day)

Known limitations:
- Pokedle.com may include multiple regions and/or colors for a pokemon, but all existing databases include only one.

---

## Environment / Setup

The code environment used to develop and test everything is described by the `pixi.toml`, and after installing pixi can be installed by just running `pixi install` in the root folder of the repository.

The game script can then be run using: `pixi run python src/game.py`
