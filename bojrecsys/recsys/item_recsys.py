import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import implicit

from .recsys import RecSys
from .. import utils

class ItemRecSys(RecSys):

    def __init__(self):
        self.model = implicit.nearest_neighbours.TFIDFRecommender(K=20)
        self.handle_to_index = {}
        self.user_item_matrix = None

    def fit(self):
        loader = utils.Loader()
        solved_df = loader.load_preproc_df('solved_info')

        handles = list(set(solved_df['handle']))
        for index, handle in enumerate(handles):
            self.handle_to_index[handle] = index
        
        user_item_matrix = np.zeros((len(handles), 32000), dtype=np.float32)
        for handle, problem in solved_df.itertuples(index=False):
            user_index = self.handle_to_index[handle]
            user_item_matrix[user_index][problem] = 1

        self.user_item_matrix = csr_matrix(user_item_matrix)
        self.model.fit(self.user_item_matrix)

    def get_recommendations(self, handle: str, problem_num: int) -> list[int]:
        index = self.handle_to_index[handle]
        recommendations, _ = self.model.recommend(index, self.user_item_matrix[index], N=problem_num)
        return recommendations
    
    def get_similar_problems(self, problem_id: int, problem_num: int):
        similar_problems, _ = self.model.similar_items(itemid=problem_id, N=problem_num)
        return similar_problems
        