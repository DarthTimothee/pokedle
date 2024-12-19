from .abstract import AbstractStrategy


class SlowpokeStrategy(AbstractStrategy):
    """
    
    This strategy is the same as RandomStrategy, but instead it always starts witht the same pokemon.
    (According to Jasper, the best one to start with is Slowpoke)
    """

    name = "random"

    def __init__(self, dex, gen, net: bool = False, initial_guess: str = None):
        self.dex = dex
        self.gen = gen
        self.net = net

        if initial_guess is not None:
            self.initial_guess = initial_guess
        else:
            self.initial_guess = "slowpoke"

    def guess(self, hints=[]) -> str:

        if len(hints) > 0:
            last_hint = hints[-1]

            # Update dex based on hint from last guess
            for col in last_hint.keys():
                if last_hint[col][1]:  # If this column was correct, eliminate all other possibilities
                    self.dex = self.dex[self.dex[col] == last_hint[col][0]]
                else:  # If this column was incorrect, eliminate this possibility
                    self.dex = self.dex[self.dex[col] != last_hint[col][0]]

            guess = self.dex.sample(1).iloc[0]['name']    
        else:
            guess = self.initial_guess
        self.dex.drop(self.dex[self.dex["name"] == guess].index, inplace=True)

        return guess