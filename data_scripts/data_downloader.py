import itertools
import time
import requests

class Downloader:
    """
    Solved.ac data downloader
    """

    # Solved.ac main API url
    URL = 'https://solved.ac/api'
    # Max page when calling api
    MAX_PAGE = 30

    def __init__(self, error_sleep_sec: int, call_sleep_sec: int) -> None:
        """Initialize downloader.

        Parameters
        ----------
        error_sleep_sec : int
            Sleeping seconds when getting too many requests error
        call_sleep_sec : int
            Sleeping seconds after calling API
        """
        self.error_sleep_sec = error_sleep_sec
        self.call_sleep_sec = call_sleep_sec

    
    def _get(self, *args, **kwargs):
        """Wrapper function for requests.get()

        When it gets 429 error, sleep for a while and retry it.
        After getting response, sleep for a short time.

        Returns
        -------
        Any
            Return value of requests.get() with the parameter given.
        """
        
        response = requests.get(*args, **kwargs)
        time.sleep(self.call_sleep_sec)
        try:
            response.raise_for_status()
        except Exception as error:
            if response.status_code == 429:
                time.sleep(self.error_sleep_sec)
                response = self._get(*args, **kwargs)
            else:
                raise error
        return response

    def get_universities(self) -> dict:
        """Get info about universities.

        Universities are sorted in an ascending order with respect to rank.

        Returns
        -------
        dict
            University info that are given as a json file.
        """
        endpoint = '/v3/ranking/organization' 
        universities = {'items': []}
        for cur_page in range(1, Downloader.MAX_PAGE + 1):
            params = {'type': 'university', 'page': cur_page}
            response = self._get(Downloader.URL + endpoint, params)
            if not response.json()['items']:
                break
            universities['items'] += response.json()['items']
        else:
            raise Exception('Max page reached!')

        universities['count'] = len(universities['items'])
        return universities

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
        endpoint = '/v3/ranking/in_organization'
        students = {'items': []}
        for cur_page in range(1, Downloader.MAX_PAGE + 1):
            params = {'organizationId': univ_id, 'page': cur_page}
            response = self._get(Downloader.URL + endpoint, params)
            if not response.json()['items']:
                break
            students['items'] += response.json()['items']
        else:
            raise Exception('Max page reached!')
        students['count'] = len(students['items'])
        return students

    def get_top_100_problems(self, handle: str) -> dict:
        """Get all info about top 100 problems that are solved by the handle.

        Problems are sorted in an ascending order with respect to tier.

        Parameters
        ----------
        handle : str
            Handle that problems are solved by.

        Returns
        -------
        dict
            Solved problems info that are given as a json file.
        """
        endpoint = '/v3/user/top_100'
        params = {'handle': handle, 'x-solvedac-language': 'ko'}
        response = self._get(Downloader.URL + endpoint, params)
        return response.json()
    
    def get_problem(self, problem_id: int) -> dict:
        """Get problem info corresponding to the given problem id.

        Parameters
        ----------
        problem_id : int
            Problem id that will be searched.

        Returns
        -------
        dict
            Problem info that are given as a json file.
        """
        endpoint = '/v3/problem/show'
        params = {'problemId': problem_id}
        response = self._get(Downloader.URL + endpoint, params)
        return response.json()
    
    def _get_problems(self, problem_ids: list[int]) -> list[dict]:
        endpoint = '/v3/problem/lookup'
        problem_ids = [str(id) for id in problem_ids]
        params = {'problemIds': ','.join(problem_ids)}
        response = self._get(Downloader.URL + endpoint, params)
        return response.json()
    
    def get_problems(self, problem_ids: list[int]) -> list[dict]:
        """Get problem info corresponding to the given problem ids.

        Parameters
        ----------
        problem_ids : list[int]
            List of problem ids that will be searched.

        Returns
        -------
        list[dict]
            Problem info that are given as a json file.
        """
        all_problems = []
        for batch_ids in itertools.batched(problem_ids, 100):
            problems = self._get_problems(list(batch_ids))
            all_problems += problems
        return all_problems