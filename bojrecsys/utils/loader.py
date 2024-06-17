import os
import pickle
import json
import pandas as pd
from ..recsys import RecSys
from . import path

class Loader:

    def __init__(self, raw_path = path.RAW_PATH, preproc_path = path.PREPROC_PATH, model_path = path.MODEL_PATH):
        self.raw_path = raw_path
        self.preproc_path = preproc_path
        self.model_path = model_path

    def load_preproc_df(self, df_name: str) -> pd.DataFrame:
        path = os.path.join(self.preproc_path, f'{df_name}.csv')
        problem_df = pd.read_csv(path, index_col=0)
        return problem_df.reset_index(drop=True)

    def load_all_problem_contents(self) -> list[dict]:
        path = os.path.join(self.raw_path, 'problem_contents')
        contents = []
        for file_name in os.listdir(path):
            with open(os.path.join(path, file_name), 'r', encoding='UTF-8') as file:
                contents += json.load(file)
        return contents

    def load_all_problem_info(self) -> list[dict]:
        path = os.path.join(self.raw_path, 'problem_info')
        info = []
        for file_name in os.listdir(path): 
            with open(os.path.join(path, file_name), 'r') as file:
                info.append(json.load(file))
        return info

    def load_all_top_100_problems(self) -> dict:
        path = os.path.join(self.raw_path, 'top_100_problems')
        info = {}
        for univ_name in os.listdir(path):
            univ_path = os.path.join(path, univ_name)
            info[univ_name] = {}
            for file_name in os.listdir(univ_path):
                handle = file_name.removesuffix('.json')
                with open(os.path.join(univ_path, file_name), 'r') as file:
                    info[univ_name][handle] = json.load(file)
        return info

    def load_all_univ_user_info(self) -> dict:
        path = os.path.join(self.raw_path, 'univ_user_info')
        info = {}
        for file_name in os.listdir(path):
            univ_path = os.path.join(path, file_name)
            univ_name = file_name.removesuffix('_user_info.json')
            with open(univ_path, 'r') as file:
                info[univ_name] = json.load(file)
        return info

    def load_model(self, model_name: str) -> RecSys:
        path = os.path.join(self.model_path, f'{model_name}.pkl')
        with open(path, 'br') as file:
            model = pickle.load(file)
        return model
