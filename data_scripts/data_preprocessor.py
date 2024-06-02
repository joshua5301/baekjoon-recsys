import os
import copy
import sys
import json
import pandas as pd
 
class Preprocessor:
    """
    Solved.ac data preprocessor
    """

    def __init__(self, raw_data_dir: str,):
        """Initialize preprocessor.

        Parameters
        ----------
        raw_data_dir : str
            Directory where raw data exsits.
        """
        self.raw_data_dir = raw_data_dir
    
    def get_problem_df(self) -> pd.DataFrame:
        """Get dataframe that contains detail information about all problems.

        Returns
        -------
        pd.DataFrame
            Dataframe about problem information
        """
        problem_info = {}
        # Load problem info to problem_info dictionary
        all_problem_dir = os.path.join(self.raw_data_dir, 'problem_information')
        for file_name in os.listdir(all_problem_dir):
            problem_dir = os.path.join(all_problem_dir, file_name)
            with open(problem_dir, 'r') as file:
                problem = json.load(file)
                problem_info[int(problem['problemId'])] = problem
        
        # Load problem contents to problem_info dictionary
        contents_dir = os.path.join(self.raw_data_dir, 'problem_contents')
        for file_name in os.listdir(contents_dir):
            bundle_dir = os.path.join(contents_dir, file_name)
            with open(bundle_dir, 'r', encoding='utf-8') as file:
                problems = json.load(file)
                for problem in problems:
                    try:
                        id = int(problem['problemId'])
                    except ValueError:
                        continue
                    problem_info[id]['content'] = problem['content']

        # Feature preprocessing
        for problem in problem_info.values():
            # Integrate tags into one feature
            tag_keys = [tag['key'] for tag in problem['tags']]
            problem['tags'] = ' '.join(tag_keys)
            # Extract language feature from titles
            languages = [title['language'] for title in problem['titles']]
            if 'ko' in languages:
                problem['language'] = 'ko'
            elif 'en' in languages:
                problem['language'] = 'en'
            else:
                problem['language'] = 'other'           
            del problem['titles']
            # Clean up space chararcters in problem content
            if 'content' in problem:
                problem['content'] = ' '.join(problem['content'].split()[1:])
            # Remove metadata feature
            del problem['metadata']
        
        # Make dataframe from problem_info dictionary
        problem_df = pd.DataFrame.from_dict(problem_info, orient='index')
        problem_df = problem_df.sort_index()
        # Make 'content' to be the last feature for ease of displaying dataframe
        columns = problem_df.columns.to_list()
        columns.remove('content')
        columns.append('content')
        problem_df = problem_df[columns]
        return problem_df

    def get_user_df(self) -> pd.DataFrame:
        """Get dataframe that contains user information.

        Returns
        -------
        pd.DataFrame
            Dataframe about user information
        """
        user_info = {}
        # Load user information to user_info dictionary
        all_user_dir = os.path.join(self.raw_data_dir, 'user_information')
        for file_name in os.listdir(all_user_dir):
            user_dir = os.path.join(all_user_dir, file_name)
            univ_name = file_name.removesuffix('_user_info.json')
            with open(user_dir, 'r') as file:
                users = json.load(file)['items']
                for user in users:
                    user['university'] = univ_name
                    user_info[user['handle']] = user
        
        # Feature preprocessing
        users = copy.deepcopy(list(user_info.values()))
        for user in users:
            features = ['handle', 'solvedCount', 'voteCount', 'class', 'tier', 'ratingByProblemsSum', 'university']
            user = {key: user[key] for key in features}
            user_info[user['handle']] = user
        
        # Make dataframe from user_info dictionary
        user_df = pd.DataFrame.from_dict(user_info, orient='index') 
        user_df = user_df.sort_index()
        return user_df

    def get_solved_df(self) -> pd.DataFrame:
        """Get dataframe that contains solve history about top 100 problems for each users.

        Returns
        -------
        pd.DataFrame
            Dataframe about solve history
        """
        solved_info = {'handle': [], 'solved': []}

        # Load solve history to solved_info dictionary
        all_solved_dir = os.path.join(self.raw_data_dir, 'solved_problems')
        for dir_name in os.listdir(all_solved_dir):
            univ_solved_dir = os.path.join(all_solved_dir, dir_name)
            for file_name in os.listdir(univ_solved_dir):
                handle = file_name.removesuffix('.json')
                solved_dir = os.path.join(univ_solved_dir, file_name)
                with open(solved_dir, 'r') as file:
                    solved_problems = json.load(file)['items']
                    for problem in solved_problems:
                        solved_info['handle'].append(handle)
                        solved_info['solved'].append(problem['problemId'])

        # Make dataframe from solved_info dictionary
        solved_df = pd.DataFrame.from_dict(solved_info, orient='columns')
        solved_df.sort_index()
        return solved_df
