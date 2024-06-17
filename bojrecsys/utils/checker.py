import os
from . import path

class Checker:
    
    def __init__(self, raw_path = path.RAW_PATH, preproc_path = path.PREPROC_PATH, model_path = path.MODEL_PATH):
        self.raw_path = raw_path
        self.preproc_path = preproc_path
        self.model_path = model_path

    def is_raw_problem_info_missing(self, problem_id: int):
        file_path = os.path.join(self.raw_path, 'problem_info', f'{problem_id}.json')
        return not os.path.exists(file_path)
        
    def is_raw_top_100_problems_missing(self, univ_name: str, handle: str):
        file_path = os.path.join(self.raw_path, 'top_100_problems', univ_name, f'{handle}.json')
        return not os.path.exists(file_path)

    def is_raw_univ_user_info_missing(self, univ_name: str):
        file_path = os.path.join(self.raw_path, 'univ_user_info', f'{univ_name}_user_info.json')
        return not os.path.exists(file_path)
