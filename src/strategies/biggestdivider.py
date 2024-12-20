from .abstract import AbstractStrategy


class BiggestDividerStrategy(AbstractStrategy):
    """
    
    This strategy is the same as RandomStrategy, but instead it always starts witht the same pokemon.
    (According to Jasper, the best one to start with is Slowpoke)
    """

    name = "random"

    def __init__(self, dex, gen, net: bool = False, initial_guess: str = None):
        self.dex = dex
        self.gen = gen
        self.net = net

        self.dex['is_predicted']=False
        self.dex['possible']=True
        if self.net:
            self.prediction_columns = ["type1", "type2", "habitat", "color", "evolution_stage", "height", "weight"]
        else:
            self.prediction_columns = ["type1", "type2", "evolution_stage", "fully_evolved", "color", "habitat", "generation"]
        
        self.investigation_dex = self.dex[(self.dex['is_predicted']==False)&(self.dex['possible']==True)]
        self.predictions = []

    def __calculate_frequencies(self, custom_dex, col):
        return (custom_dex[col].value_counts()/len(custom_dex)).to_dict()
    
    def _get_col_frequencies(self, col_list, custom_dex):
        frequencies = {}
        for col in col_list:
            freq_dict_for_col = self.__calculate_frequencies(custom_dex, col)
            frequencies[col] = freq_dict_for_col
        return frequencies
    
    def __eliminate_unmatched(self, hint):
        for col, col_hint in hint.items():
            if col_hint[1]==1:
                self.dex.loc[self.dex[col]!=col_hint[0],'possible']=False
            elif not col_hint[1]:
                self.dex.loc[self.dex[col]==col_hint[0],'possible']=False

    def _evaluate_response(self, hint):
        self.__eliminate_unmatched(hint)
        self.investigation_dex = self.dex[(self.dex['is_predicted']==False)&(self.dex['possible']==True)]

    def guess(self, hints=[]) -> str:
        dex_for_choosing = self.investigation_dex.copy()
        if len(hints) > 0:
            last_hint = hints[-1]
            self._evaluate_response(last_hint)
            leftover_cols = self.prediction_columns.copy()
            stop=False
            while not stop: 
                frequencies = self._get_col_frequencies(leftover_cols, dex_for_choosing)
                col_val_pairs = {(col,val): abs(freq-0.5)  for col, freqs in frequencies.items() for val, freq in freqs.items() }
                max_divider_col, max_divider_val = min(col_val_pairs, key=col_val_pairs.get)
                max_divider_freq = col_val_pairs[(max_divider_col, max_divider_val)]
                dex_for_choosing = dex_for_choosing[dex_for_choosing[max_divider_col]==max_divider_val]
                leftover_cols.remove(max_divider_col)
                if len(dex_for_choosing)==1 or max_divider_freq==0.5:
                    stop=True
        
        choice = dex_for_choosing.sample(1).iloc[0]
        del dex_for_choosing
            
        self.dex.loc[self.dex['name']==choice['name'],'is_predicted']=True
        self.predictions.append(choice)
        return choice['name']