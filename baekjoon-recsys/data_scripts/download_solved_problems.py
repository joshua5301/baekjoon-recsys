import os
import json
from data_downloader import Downloader

downloader = Downloader(error_sleep_sec=100, call_sleep_sec=1)
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
solved_dir = os.path.join(project_dir, 'data', 'raw', 'solved_problems')
os.makedirs(solved_dir, exist_ok=True)

universities = downloader.get_universities()['items']
for university in universities:
    univ_solved_dir = os.path.join(solved_dir, university['name'])
    os.makedirs(univ_solved_dir, exist_ok=True)
    students = downloader.get_students(university['organizationId'])['items']
    for num, student in enumerate(students):
        print(f'{university['name']}: {student["handle"]} - {num + 1}/{len(students)}')
        student_solved_dir = os.path.join(univ_solved_dir, student['handle'] + '.json')
        if os.path.exists(student_solved_dir):
            print('Already exists!')
        else:
            problems = downloader.get_top_100_problems(student['handle'])
            with open(student_solved_dir, 'w') as file:
                json.dump(problems, file)
