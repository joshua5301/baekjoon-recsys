from unittest.mock import Mock
from .mock_requests_const import *

def get(url: str, params: dict):

    response_json = None

    if url.endswith('/v3/ranking/organization'):
        assert params['type'] == 'university'
        assert params['page'] >= 1
        if params['page'] <= 10:
            start_idx = (params['page'] - 1) * 10
            response_json = {'count': 10, 'items': DUMMY_UNIVERSITIES[start_idx: start_idx + 10]}
        else:
            response_json = {'count': 0, 'items': []}

    if url.endswith('/v3/ranking/in_organization'):
        assert params['page'] >= 1
        if params['page'] <= 10:
            start_idx = (params['page'] - 1) * 10
            response_json = {'count': 10, 'items': DUMMY_USERS[start_idx: start_idx + 10]}
        else:
            response_json = {'count': 0, 'items': []}

    if url.endswith('/v3/user/top_100'):
        response_json = {'count': 100, 'items': DUMMY_PROBLEMS[:100]}

    if url.endswith('/v3/problem/show'):
        for problem in DUMMY_PROBLEMS:
            if problem['problemId'] == params['problemId']:
                response_json = problem
                break

    if url.endswith('/v3/problem/lookup'):
        response_json = []
        param_problems = list(map(int, params['problemIds'].split(',')))
        for problem in DUMMY_PROBLEMS:
            if problem['problemId'] in param_problems:
                response_json.append(problem)

    response = Mock()
    response.json = Mock()
    response.json.return_value = response_json
    return response
