DUMMY_UNIVERSITIES = [
    {
        'organizationId': id,
        'name': f'univ_{id}'
    }
    for id in range(1, 100)
]

DUMMY_PROBLEMS = [
    {
        "problemId": id,
        "titleKo": f"prob_{id}", 
        "titles": [{"language": "ko"}],
        "level": 1,
        "tags": [{"key": "dummy"}],
        "metadata": {}
    }
    for id in range(1000, 10000)
]

DUMMY_USERS = [
    {
        "handle": f"user_{id}",
        "solvedCount": 1,
        "class": 1,
        "tier": 1,
        "ratingByProblemsSum": 1
    }
    for id in range(1, 1000)
]