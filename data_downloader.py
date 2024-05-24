import os
import sys
import time
import json
import requests

class Downloader:
    """
    Solved.ac info downloader
    """

    # Solved.ac main API url
    URL = 'https://solved.ac/api'
    # Max page when calling api
    MAX_PAGE = 30
    # Sleeping seconds when getting too many requests error
    SLEEP_SECONDS_ERROR = 60 * 15
    # Sleeping seconds after calling API
    SLEEP_SECONDS_CALL = 1
 
    @staticmethod
    def _get(*args, **kwargs):
        """Wrapper function for requests.get()

        When it gets 429 error, sleep for a while and retry it.

        Returns
        -------
        Any
            Return value of requests.get() with the parameter given.
        """
        try:
            response = requests.get(*args, **kwargs)
            time.sleep(Downloader.SLEEP_SECONDS_CALL)
            response.raise_for_status()
        except Exception as e:
            if response.status_code == 429:
                time.sleep(Downloader.SLEEP_SECONDS_ERROR)
                response = Downloader._get(*args, **kwargs)
            else:
                print(repr(e))
                sys.exit(-1)
        return response

    def get_universities(self) -> dict:
        """Get all university info.

        Universities are sorted in an ascending order with respect to rank.

        Returns
        -------
        dict
            University info that are given as a json file.
        """
        endpoint = '/v3/ranking/organization'
        params = {'type': 'university', 'page': 1}
        response = Downloader._get(Downloader.URL + endpoint, params)
        return response.json()

    def get_students(self, univ_id: int) -> dict:
        """Get all info about students that are in given university.

        Students are sorted in an ascending order with respect to rank.

        Parameters
        ----------
        univ_id : int
            University id that users are in.

        Returns
        -------
        dict
            Student info that are given as a json file.
        """
        end_point = '/v3/ranking/in_organization'
        students = {'items': []}
        for cur_page in range(1, Downloader.MAX_PAGE + 1):
            params = {'organizationId': univ_id, 'page': cur_page}
            response = Downloader._get(Downloader.URL + end_point, params)
            if not response.json()['items']:
                break
            students['items'] += response.json()['items']
        students['count'] = len(students['items'])
        return students

    def get_top_100_problems(self, handle: str) -> dict:
        """Get all info about top 100 problems that are solved by a handle.

        Problems are sorted in an ascending order with respect to tier.

        Parameters
        ----------
        handle : str
            Handle that problems are solved by.

        Returns
        -------
        dict
            Solved problem info that are given as a json file.
        """
        endpoint = '/v3/user/top_100'
        params= {'handle': handle, 'x-solvedac-language': 'ko'}
        response = Downloader._get(Downloader.URL + endpoint, params)
        return response.json()


if __name__ == '__main__':
    cur_dir = os.path.realpath(__file__)
    data_dir = os.path.join(os.path.dirname(cur_dir), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    downloader = Downloader()
    univs = downloader.get_universities()
    for univ in univs['items']:
        univ_dir = os.path.join(data_dir, univ['name'])
        if not os.path.exists(univ_dir):
            os.makedirs(univ_dir)
        
        # Write student info
        print(f'Downloading {univ["name"]} student info...')
        user_info_dir = os.path.join(univ_dir, 'USER_INFO')
        if os.path.exists(user_info_dir):
            with open(user_info_dir, 'r') as file:
                students = json.load(file)
        else:
            students = downloader.get_students(univ['organizationId'])
            with open(user_info_dir, 'w') as file:
                json.dump(students, file)
        
        # Write problem info 
        for cur_num, student in enumerate(students['items']):
            print(f'{univ["name"]}: {student["handle"]} - {cur_num + 1}/{students["count"]}')
            student_dir = os.path.join(univ_dir, student['handle'])
            if os.path.exists(student_dir):
                print('Already exists!')
            else:
                problems = downloader.get_top_100_problems(student['handle'])
                with open(student_dir, 'w') as file:
                    json.dump(problems, file)
