import os
import json
from data_downloader import Downloader

downloader = Downloader(error_sleep_sec=100, call_sleep_sec=3)
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
all_problem_dir = os.path.join(project_dir, 'data', 'raw', 'problem_information')
os.makedirs(all_problem_dir, exist_ok=True)

missing_ids = []
for id in range(1000, 32000):
    problem_dir = os.path.join(all_problem_dir, str(id) + '.json')
    if not os.path.exists(problem_dir):
        missing_ids.append(id)

problems = downloader.get_problems(missing_ids)
for problem in problems:
    problem_dir = os.path.join(all_problem_dir, str(problem['problemId']) + '.json')
    with open(problem_dir, 'w') as file:
        json.dump(problem, file)