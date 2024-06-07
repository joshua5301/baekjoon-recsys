import os
from data_preprocessor import Preprocessor

project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
raw_data_dir = os.path.join(project_dir, 'data', 'raw')
output_dir = os.path.join(project_dir, 'data', 'preprocessed')

preproc = Preprocessor(raw_data_dir)
problem_df = preproc.get_problem_df()
problem_df.to_csv(os.path.join(output_dir, 'problem_info.csv'))
user_df = preproc.get_user_df()
user_df.to_csv(os.path.join(output_dir, 'user_info.csv'))
solved_df = preproc.get_solved_df()
solved_df.to_csv(os.path.join(output_dir, 'solved_info.csv'))