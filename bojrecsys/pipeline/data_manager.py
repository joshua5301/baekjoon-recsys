import itertools
from tqdm import tqdm
from .data_downloader import DataDownloader
from .data_preprocessor import DataPreprocessor
from .. import utils

def _exit_when_keyboard_interrupt(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyboardInterrupt:
            print('!!!!!--------------Early exit by keyboard interrupt--------------!!!!!\n')
    return wrapper

class DataManager:

    def __init__(self, downloader = DataDownloader(), preprocessor = DataPreprocessor(),
                 loader = utils.Loader(), dumper = utils.Dumper(), checker = utils.Checker()) -> None:
        self.downloader = downloader
        self.preprocessor = preprocessor
        self.loader = loader
        self.dumper = dumper
        self.checker = checker

    @_exit_when_keyboard_interrupt
    def download_problem_info(self, problem_ids: list[int]):
        print('--------------------Problem info download started---------------------')
        missing_ids = []
        for id in problem_ids:
            if self.checker.is_raw_problem_info_missing(id):
                missing_ids.append(id)
        print(f'Total {len(missing_ids)} missing problems found.')

        download_cnt = 0
        tqdm_iter = tqdm(list(itertools.batched(missing_ids, n=100)))
        for ids in tqdm_iter:
            tqdm_iter.set_description_str(f'Currently downloading - {ids[0]} to {ids[-1]}')
            problems = self.downloader.get_problems(ids)
            for problem in problems:
                self.dumper.dump_problem_info(problem)
                download_cnt += 1
        print(f'Total {download_cnt} non-empty problems downloaded.')
        print('-------------------Problem info download completed--------------------\n')

    @_exit_when_keyboard_interrupt
    def download_top_100_problems(self):
        print('------------------Top 100 problems download started-------------------')
        univ_user_info = self.loader.load_all_univ_user_info()
        missing_solved_problems = []
        for univ_name, students in univ_user_info.items():
            for student in students:
                if self.checker.is_raw_top_100_problems_missing(univ_name, student['handle']):
                    missing_solved_problems.append((univ_name, student['handle']))
        print(f'Total {len(missing_solved_problems)} missing solve info found.')

        tqdm_iter = tqdm(missing_solved_problems)
        for univ_name, handle in tqdm_iter:
            tqdm_iter.set_description_str(f'Currently downloading - {handle}')
            top_100_problems = self.downloader.get_top_100_problems(handle)
            self.dumper.dump_top_100_problems(top_100_problems, univ_name, handle)
        tqdm_iter.close()
        print('-----------------Top 100 problems download completed------------------\n')

    @_exit_when_keyboard_interrupt
    def download_user_info(self):
        print('----------------------User info download started----------------------')
        universities = self.downloader.get_universities()
        tqdm_iter = tqdm(universities)
        for university in tqdm_iter:
            tqdm_iter.set_description_str(f'Currently downloading - {university['name']} users')
            if self.checker.is_raw_univ_user_info_missing(university['name']):
                students = self.downloader.get_students(university['organizationId'])
                self.dumper.dump_univ_user_info(students, university['name'])
        print('---------------------User info download completed---------------------\n')

    @_exit_when_keyboard_interrupt
    def preprocess(self):
        print('----------------------Preprocessing started----------------------')
        print('Loading problem info...')
        raw_problems = self.loader.load_all_problem_info()
        print('Loading content info...')
        raw_contents = self.loader.load_all_problem_contents()
        print('Loading top 100 problems info... - (This may take some time...)')
        raw_top_100_problems = self.loader.load_all_top_100_problems()
        print('Loading university user info...')
        raw_users = self.loader.load_all_univ_user_info()

        print('Preprocessing problem info...')
        problem_df = self.preprocessor.get_problem_df(raw_problems, raw_contents)
        self.dumper.dump_preproc_df(problem_df, 'problem_info')
        print('Preprocessing user info...')
        user_df = self.preprocessor.get_user_df(raw_users)
        self.dumper.dump_preproc_df(user_df, 'user_info')
        print('Preprocessing solved info...')
        solved_df = self.preprocessor.get_solved_df(raw_top_100_problems)
        self.dumper.dump_preproc_df(solved_df, 'solved_info')
        print('---------------------Preprocessing completed---------------------\n')