import os
import json
from data_downloader import Downloader

downloader = Downloader(error_sleep_sec=100, call_sleep_sec=3)
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
all_user_dir = os.path.join(project_dir, 'data', 'raw', 'user_information')
os.makedirs(all_user_dir, exist_ok=True)

universities = downloader.get_universities()['items']
for num, university in enumerate(universities):
    univ_user_dir = os.path.join(all_user_dir, university['name'] + '_user_info.json')
    print(f'{university['name']} - {num + 1}/{len(universities)}')
    if not os.path.exists(univ_user_dir):
        students = downloader.get_students(university['organizationId'])
        with open(univ_user_dir, 'w') as file:
            json.dump(students, file)
    else:
        print(f'Already exists!')