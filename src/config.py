import os, sys
print(os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path

ROOT_DIR = os.environ.get('POKEDLE_ROOT_DIR', None)
if ROOT_DIR is not None:
    ROOT_DIR = Path(ROOT_DIR)

if ROOT_DIR is None or not ROOT_DIR.exists() or not ROOT_DIR.is_dir():
    start_file_loc = Path(__file__).resolve()
    while start_file_loc.name.lower() != 'src' and start_file_loc.parent.name.lower() != 'pokedle':
        start_file_loc = start_file_loc.parent
    ROOT_DIR = start_file_loc.parent

sys.path.insert(0, ROOT_DIR.absolute().as_posix())

DATA_DIR = ROOT_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

RESULT_DIR = ROOT_DIR / 'results'
RESULT_DIR.mkdir(parents=True, exist_ok=True)