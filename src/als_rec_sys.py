import os
import pickle
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import implicit
from rec_sys import RecSys

class ALSRecSys(RecSys):

    def __init__(self):
        self.model = implicit.als.AlternatingLeastSquares(factors=64, regularization=0.05, alpha=2.0)
        self.handle_to_id = {}
        self.user_item_matrix = None

    def fit(self):
        project_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(project_dir, 'data', 'preprocessed', 'solved_info.csv')
        solved_df = pd.read_csv(data_dir, index_col=0)

        for id, user in enumerate(set(solved_df['handle'])):
            self.handle_to_id[user] = id

        self.user_item_matrix = np.zeros((len(set(solved_df['handle'])), 32000), dtype=np.int32)
        for handle, problem in solved_df.itertuples(index=False):
            id = self.handle_to_id[handle]
            self.user_item_matrix[id][problem] = 1
        self.user_item_matrix = csr_matrix(self.user_item_matrix)
        self.model.fit(self.user_item_matrix)

    def get_recommendations(self, target_handle: str, num: int) -> list[int]:
        """Get recommendations by using ALS.

        Parameters
        ----------
        handle : str
            User that recommendations will be given
        num : int
            Number of recommendations

        Returns
        -------
        list[int]
            List of recommendations
        """
        target_id = self.handle_to_id[target_handle]
        recommendations, _ = self.model.recommend(target_id, self.user_item_matrix[target_id], N=num)
        return recommendations


if __name__ == '__main__':
    als = ALSRecSys()
    als.fit()
    project_path = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(project_path, 'models', 'ALS_model.pkl'), 'bw') as file:
        pickle.dump(als, file)
    problems = als.get_recommendations(target_handle='37aster', num=10)
    print(problems)