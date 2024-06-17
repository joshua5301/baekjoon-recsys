import os
import pickle
import json
import pandas as pd
from ..recsys import RecSys
from . import path

class Dumper:

    def __init__(self, raw_path = path.RAW_PATH, preproc_path = path.PREPROC_PATH, model_path = path.MODEL_PATH):
        self.raw_path = raw_path
        self.preproc_path = preproc_path
        self.model_path = model_path

    def dump_preproc_df(self, preproc_df: pd.DataFrame, df_name: str):
        file_path = os.path.join(self.preproc_path, f'{df_name}.csv')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        preproc_df.to_csv(file_path)

    def dump_problem_info(self, problem_info: dict):
        file_path = os.path.join(self.raw_path, 'problem_info', f'{problem_info['problemId']}.json')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(problem_info, file)

    def dump_top_100_problems(self, top_100_problems: dict[dict], univ_name: str, handle: str):
        file_path = os.path.join(self.raw_path, 'top_100_problems', univ_name, f'{handle}.json')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(top_100_problems, file)

    def dump_univ_user_info(self, univ_user_info: list[dict], univ_name: str):
        file_path = os.path.join(self.raw_path, 'univ_user_info', f'{univ_name}_user_info.json')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(univ_user_info, file)

    def dump_model(self, model: RecSys, model_name: str):
        file_path = os.path.join(self.model_path, f'{model_name}.pkl')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'bw') as file:
            pickle.dump(model, file)