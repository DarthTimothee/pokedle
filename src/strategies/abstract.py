import pandas as pd


class AbstractStrategy:
    """
    This class can be inherited by any strategy.
    The strategy should implement the guess method, and specify the name (used to output)
    """

    name: str = None

    def __init__(self, dex: pd.DataFrame, gen: int, net: bool):
        self.dex = dex
        self.gen = gen
        self.net = net


    def guess(self, hints=[]) -> str:
        """
        The guess method received the entire history of hints from the game (if any, None otherwise).
        It should return the name of the pokemon to guess next.
        """

        raise NotImplementedError