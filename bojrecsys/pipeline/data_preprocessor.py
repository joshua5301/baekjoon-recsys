import pandas as pd
 
class DataPreprocessor:
    """
    Solved.ac data preprocessor
    """
    
    def get_problem_df(self, raw_problems: list[dict], raw_contents: list[dict]) -> pd.DataFrame:
        """Get dataframe that contains detail information about all problems.

        Parameters
        ----------
        raw_problems : list[dict]
            Raw problem info
        raw_contents : list[dict]
            Raw problem content info

        Returns
        -------
        pd.DataFrame
            Dataframe about problem information
        """
        problem_df = pd.DataFrame(raw_problems)
        content_df = pd.DataFrame(raw_contents)
        content_df['problemId'] = pd.to_numeric(content_df['problemId'], errors='coerce')

        # Merge contents into problem dataframe
        problem_df = problem_df.merge(content_df, how='inner', on='problemId')

        # Make tag feature into one clean string
        def get_clean_tags(tags: list[dict]) -> str:
            keys = [tag['key'] for tag in tags]
            return ' '.join(keys)
        problem_df['tags'] = problem_df['tags'].apply(get_clean_tags)

        # Extract language feature from titles
        def get_langauge_from_titles(titles: list[dict]) -> str:
            languages = [title['language'] for title in titles]
            if len(languages) == 1:
                language = languages[0]
            elif 'ko' in languages:
                language = 'ko'
            elif 'en' in languages:
                language = 'en'
            else:
                language = 'other'
            return language
        problem_df['language'] = problem_df['titles'].apply(get_langauge_from_titles)

        # Clean up space chararcters in content feature
        def get_clean_content(content: str):
            return ' '.join(content.split()[1:])
        problem_df['content'] = problem_df['content'].apply(get_clean_content)
        
        # Drop unnecessary features    
        problem_df = problem_df.drop(['titles', 'metadata'], axis=1)
        
        # Make 'content' to be the last feature for ease of displaying dataframe
        columns = problem_df.columns.to_list()
        columns.remove('content')
        columns.append('content')
        problem_df = problem_df[columns]
        return problem_df

    def get_user_df(self, raw_users: dict[dict]) -> pd.DataFrame:
        user_info = []
        for univ_name, univ_users in raw_users.items():
            for user in univ_users:
                user['university'] = univ_name
                user_info.append(user)
        user_df = pd.DataFrame(user_info)
        
        # Only pick necessary features
        features = ['handle', 'solvedCount', 'class', 'tier', 'ratingByProblemsSum', 'university']
        user_df = user_df[features]
        return user_df

    def get_solved_df(self, raw_top_100_problems: dict) -> pd.DataFrame:
        solved_info = []
        for univ_name, handle_to_top_100 in raw_top_100_problems.items():
            for handle, top_100 in handle_to_top_100.items():
                for problem in top_100:
                    solved_info.append({'handle': handle, 'problemId': problem['problemId']})
        solved_problem_df = pd.DataFrame(solved_info)
        return solved_problem_df
