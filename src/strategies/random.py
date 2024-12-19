from .abstract import AbstractStrategy


class RandomStrategy(AbstractStrategy):
    name = "random"

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

        self.dex.drop(self.dex[self.dex["name"] == guess].index, inplace=True)

        return guess