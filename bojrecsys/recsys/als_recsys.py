import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import implicit
from .recsys import RecSys
from .. import utils

class ALSRecSys(RecSys):

    def __init__(self):
        self.model = implicit.als.AlternatingLeastSquares(factors=64, regularization=0.05, alpha=2.0)
        self.handle_to_index = {}
        self.user_item_matrix = None

    def fit(self):
        loader = utils.Loader()
        solved_df = loader.load_preproc_df('solved_info')

        handles = list(set(solved_df['handle']))
        for index, handle in enumerate(handles):
            self.handle_to_index[handle] = index
        
        user_item_matrix = np.zeros((len(handles), 32000), dtype=np.int32)
        for handle, problem in solved_df.itertuples(index=False):
            user_index = self.handle_to_index[handle]
            user_item_matrix[user_index][problem] = 1

        self.user_item_matrix = csr_matrix(user_item_matrix)
        self.model.fit(self.user_item_matrix)

    def get_recommendations(self, target_handle: str, num: int) -> list[int]:
        target_index = self.handle_to_index[target_handle]
        recommendations, _ = self.model.recommend(target_index, self.user_item_matrix[target_index], N=num)
        return recommendations