import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import umap
import numpy as np

try:
    from src import config
except:
    import config
    
from src import helper_functions
from src import game

def show_umap(game, out_loc='tmp.png', color_cols=[], umap_kwargs={'n_neighbors':7}):
    onehot_dex = pd.get_dummies(game.dex[game.prediction_cols]).astype(int)
    umap_embs = umap.UMAP(**umap_kwargs).fit_transform(onehot_dex)
    cols = 4
    rows = int(np.ceil(len(color_cols)/cols))
    plt.rcParams["figure.figsize"] = (cols*5,rows*5)

    df = pd.concat((pd.DataFrame(umap_embs, columns=['x', 'y']), game.dex), axis=1)
    if len(color_cols)==0:
        sns.scatterplot(data=df, x='x', y='y')
    if len(color_cols)==1:
        sns.scatterplot(data=df, x='x', y='y', hue=color_cols[0])
    else:
        f, axes = plt.subplots(rows, cols)
        for ax_idx, ax in enumerate(axes.reshape(-1)):  
            if ax_idx<len(color_cols):
                asubplot = sns.scatterplot(data=df, x='x', y='y', hue=color_cols[ax_idx], ax=ax)
                ax.set(title=f'{color_cols[ax_idx]}')
            ax.set(xticklabels=[], xlabel=None, yticklabels=[], ylabel=None)
            ax.tick_params(bottom=False, left=False)
    plt.savefig(out_loc)
    
if __name__ == "__main__":
    args = helper_functions._init_argparse()
    umap_params = {'n_neighbors':7}
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
    game = game.Game(dex, gen=gen, net=net, verbose=0)
    color_cols = game.prediction_cols
    out_loc = config.RESULT_DIR / 'visuals' / 'UMAP' / f'gen{gen}_net{net}_{"_".join(color_cols)}_nn{umap_params["n_neighbors"]}'
    out_loc.parent.mkdir(parents=True, exist_ok=True)
    show_umap(game, out_loc, color_cols=color_cols, umap_kwargs = umap_params)
    