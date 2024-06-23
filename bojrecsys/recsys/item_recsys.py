import numpy as np
import pandas as pd
import implicit
from requests import HTTPError
from scipy.sparse import csr_matrix
from threadpoolctl import threadpool_limits

from .recsys import RecSys
from ..pipeline import DataDownloader
from .. import utils

class ItemRecSys(RecSys):

    def __init__(self):
        threadpool_limits(1, "blas")
        self.model = implicit.nearest_neighbours.BM25Recommender()
        self.handle_to_index = {}
        self.problem_id_to_index = {}
        self.index_to_problem_id = {}
        self.user_item_matrix = None

    def fit(self):
        loader = utils.Loader()
        solved_df = loader.load_preproc_df('solved_info')

        handles = list(set(solved_df['handle']))
        for index, handle in enumerate(handles):
            self.handle_to_index[handle] = index
        problem_ids = list(set(solved_df['problemId']))
        for index, problem_id in enumerate(problem_ids):
            self.problem_id_to_index[problem_id] = index
        self.index_to_problem_id = {index: id for id, index in self.problem_id_to_index.items()}
        
        user_item_matrix = np.zeros((len(handles), len(problem_ids)), dtype=np.float32)
        for handle, problem_id in solved_df.itertuples(index=False):
            user_index = self.handle_to_index[handle]
            item_index = self.problem_id_to_index[problem_id]
            user_item_matrix[user_index][item_index] = 1
        self.user_item_matrix = csr_matrix(user_item_matrix)

        self.model.fit(self.user_item_matrix)

    def get_recommendations(self, handle: str, problem_num: int) -> list[int]:
        downloader = DataDownloader()
        try:
            problems = downloader.get_top_100_problems(handle)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise KeyError
            else:
                raise e
        solved_indices = [self.problem_id_to_index[problem['problemId']] for problem in problems]
        problem_num = len(self.problem_id_to_index)
        solve_info = csr_matrix([1 if index in solved_indices else 0 for index in range(problem_num)], dtype=np.float32)
        
        recommendations, _ = self.model.recommend('dummy_index', solve_info, recalculate_user=True)
        recommendations = [self.index_to_problem_id[index] for index in recommendations]
        return recommendations[:problem_num]

    def get_similar_problems(self, problem_id: int, problem_num: int):
        problem_index = self.problem_id_to_index[problem_id]
        similar_problems, _ = self.model.similar_items(problem_index, N=problem_num)
        similar_problems = [self.index_to_problem_id[index] for index in similar_problems]
        return similar_problems