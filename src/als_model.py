import os
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import implicit

def get_recommendations(target_handle: str, num: int) -> list[int]:
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
    project_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(project_dir, 'data', 'preprocessed', 'solved_info.csv')
    solved_df = pd.read_csv(data_dir, index_col=0)

    handle_to_id = {}
    for id, user in enumerate(set(solved_df['handle'])):
        handle_to_id[user] = id

    user_item_matrix = np.zeros((len(set(solved_df['handle'])), 32000), dtype=np.int32)
    for handle, problem in solved_df.itertuples(index=False):
        id = handle_to_id[handle]
        user_item_matrix[id][problem] = 1
    user_item_matrix = csr_matrix(user_item_matrix)

    model = implicit.als.AlternatingLeastSquares(factors=64, regularization=0.05, alpha=2.0)
    model.fit(user_item_matrix)

    target_id = handle_to_id[target_handle]
    recommendations, _ = model.recommend(target_id, user_item_matrix[target_id], N=num)
    return list(recommendations)

if __name__ == '__main__':
    problems = get_recommendations(target_handle='37aster', num=10)
    print(problems)